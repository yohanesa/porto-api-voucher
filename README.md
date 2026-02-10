# Promo Code Management API

> **Portfolio Project** — A small Python/Django version of a real voucher system originally built in PHP/Laravel. The project focuses on clean structure, clear business logic, and Docker-based deployment. Core voucher features are implemented, while more complex cases are intentionally left out to keep the project simple and easy to understand.

Note: AI tools (GitHub Copilot and ChatGPT) were used to assist development. The final design and implementation decisions are my own.

A Django-Ninja REST API for managing promotional vouchers and discount codes with atomic redemption, strategy-based calculation, and production-ready Docker setup.

## 🎯 What It Does

This project provides a complete system for:
- **Creating promotions** with different discount types (fixed amount, percentage, free shipping)
- **Generating unique voucher codes** automatically when a promo is created
- **Redeeming vouchers atomically** with pessimistic locking to prevent double-use
- **Calculating discounts** using the strategy pattern for extensibility

## 🛠 Tech Stack

- **Framework**: Django 6.0 + Django-Ninja (async-ready REST API)
- **Database**: SQLite (dev) / PostgreSQL (production)
- **ASGI Server**: Gunicorn + Uvicorn
- **Testing**: pytest + pytest-django
- **Containerization**: Docker + docker-compose
- **Code Quality**: Python 3.12, type hints, clean architecture

## ✨ Key Features

### 1. **Strategy Pattern for Discount Logic**
```python
# Easy to add new discount types
class DiscountFixedStrategy(BaseStrategy):
    def calculate(self, transaction_amount: Decimal) -> Dict:
        # Your logic here
```
Current strategies:
- Fixed amount discounts
- Percentage-based discounts
- Free shipping

### 2. **Atomic Redemption with Pessimistic Locking**
```python
# No race conditions, no double-redemptions
with transaction.atomic():
    vc = VoucherCode.objects.select_for_update().filter(code=code).first()
    # Safe to mark as redeemed
```

### 3. **Three-Phase Payment-Dependent Redemption** ⭐
For payment-dependent workflows with **user-based authorization**: reserve during checkout, confirm after payment:

```python
from django.contrib.auth.models import User
from apps.promoout.services.promo_service import PromoService

user = User.objects.get(pk=1)  # Current logged-in user

# Phase 1: Reserve voucher during checkout (before payment)
# Only this user can later confirm or rollback
reserve_result = PromoService.reserve_voucher(
    voucher_code="PROMO123",
    transaction_pk=42,
    transaction_amount=Decimal("100.00"),
    user=user  # <- Locks to this user
)
# → status='reserved', reserved_by_user=user, prevents other users from interfering

# Phase 2a: Confirm after payment succeeds
# Only the same user who reserved can confirm
PromoService.confirm_redemption(
    voucher_code="PROMO123",
    transaction_pk=42,
    user=user  # <- Must match the reserving user
)
# → status='activated', sets final reference

# Phase 2b: Or rollback if payment fails/canceled
# Only the same user who reserved can rollback
PromoService.rollback_reservation(
    voucher_code="PROMO123",
    transaction_pk=42,
    user=user  # <- Must match the reserving user
)
# → status='available' again, available for other users
```

**Security:** Voucher is locked to the user who reserved it. Confirm/rollback require:
- ✅ Valid authentication
- ✅ Matching transaction ID
- ✅ Same user who made the reservation

### 4. **Signal-Based Voucher Generation**
```python
# Vouchers created automatically when Promo is saved
@receiver(post_save, sender=Promo)
def create_vouchers_on_promo_created(sender, instance, created, **kwargs):
    ...
```
No circular imports, clean separation of concerns.

### 5. **Comprehensive Test Suite**
```
38 tests passing ✅
- Strategy unit tests (14 tests)
- Registry validation (6 tests)
- Direct redemption flow (10 tests)
- Three-phase payment-dependent flow with user authorization (8 tests)
```

### 6. **Production-Ready Docker**
Multi-stage build: tests run first, production stage only builds if all tests pass.

## 📊 Database Schema

```
Promo
├── id (PK)
├── name
├── type (fixed, percentage, free_shipping)
├── total_voucher
├── amount (discount value)
├── min_purchase
└── timestamps

VoucherCode
├── id (PK)
├── promo_id (FK)
├── code (unique)
├── status (available|reserved|activated)
├── activated (boolean, backward compat)
├── pending_transaction_pk (nullable, temp hold during payment)
├── reserved_by_user_id (FK, non-null when reserved; authorization)
├── reference (nullable, final transaction_pk after activation)
└── timestamps
```

## 🚀 Quick Start

### Local Setup

```bash
# Clone and navigate
git clone <repo>
cd promo_py

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # or `.venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env  # Or create from template
# Edit .env with your settings (DEBUG, SECRET_KEY, etc.)

# Run migrations
cd promo
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

### Docker Setup

```bash
# Ensure .env file exists in root (or Docker uses defaults)
docker compose up --build

# Container will:
# ✅ Run all tests first
# ✅ Apply migrations
# ✅ Collect static files
# ✅ Start gunicorn on port 8000
```

**📝 Environment Configuration**: See [ENV_GUIDE.md](ENV_GUIDE.md) for detailed `.env` variable setup.

## 🔌 API Endpoints

### Authentication
All endpoints require token authentication. Create tokens via admin panel.

### Promo Management
```
POST   /api/promo/              Create a promo
GET    /api/promo/              List all promos
POST   /api/promo/{id}/vouchers Generate vouchers for a promo
```

### Voucher Redemption (Direct)
```
POST   /api/promoout/redeem
Request:
{
  "code": "PROMO123",
  "transaction_pk": 42,
  "transaction_amount": "99.99"
}

Response:
{
  "voucher": {
    "id": 1,
    "code": "PROMO123",
    "status": "activated",
    "reference": 42
  },
  "calculation": {
    "discount": "10.00",
    "message": "Discount applied"
  }
}
```

### Voucher Redemption (Three-Phase for Payment-Dependent Flows)
```
# Phase 1: Reserve during checkout (before payment)
POST   /api/promoout/reserve
Request:
{
  "code": "PROMO123",
  "transaction_pk": 42,
  "transaction_amount": "99.99"
}
Response: { "voucher": {..., "status": "reserved"}, "calculation": {...} }

# Phase 2a: Confirm after payment succeeds
POST   /api/promoout/confirm/{code}/{transaction_pk}
Response: { "voucher": {..., "status": "activated", "reference": 42} }

# Phase 2b: Rollback if payment fails
POST   /api/promoout/rollback/{code}/{transaction_pk}
Response: { "voucher": {..., "status": "available"} }
```
*Note: These endpoints are not yet exposed in the API. See `PromoService` methods for usage.*

## 🧪 Testing

```bash
cd promo
pytest ../tests/ -v              # Run all tests
pytest ../tests/test_strategies.py -v  # Strategy unit tests
pytest ../tests/test_registry.py -v    # Registry tests
pytest ../tests/test_promo_service.py -v  # Integration tests
```

Coverage:
- **Strategy calculations**: Fixed/percentage discount logic, min purchase validation
- **Registry mapping**: Type-to-strategy resolution
- **Redeem flow**: Atomicity, locking, double-redemption prevention, error handling

## 🏗 Architecture Highlights

### Clean Separation of Concerns
- **Models** (`apps/promoin/models.py`) — Data layer
- **Strategies** (`apps/promoout/strategies/`) — Business logic (calculation only)
- **Services** (`apps/promoout/services/`) — Orchestration (atomicity, persistence)
- **API** (`apps/promoout/api.py`) — HTTP interface
- **Signals** (`apps/promoin/signals.py`) — Event handling (no circular imports)

### Design Patterns Used
- **Strategy Pattern** — Pluggable discount types
- **Registry Pattern** — Type-to-strategy mapping
- **Signal Pattern** — Decoupled event handling
- **Service Layer** — Transaction coordination
- **AppConfig** — Django app configuration & signal registration

## 📦 Project Structure

```
promo_py/
├── promo/                    # Django project
│   ├── apps/
│   │   ├── promoin/          # Promo creation & voucher generation
│   │   │   ├── models.py
│   │   │   ├── signals.py    # Signal handlers (no circular imports)
│   │   │   ├── apps.py       # AppConfig
│   │   │   ├── admin.py      # Django admin
│   │   │   └── api.py
│   │   └── promoout/         # Voucher redemption
│   │       ├── strategies/   # Strategy classes
│   │       ├── services/     # Service layer
│   │       ├── api.py
│   │       └── schemas.py
│   ├── libs/                 # Shared utilities
│   ├── settings.py
│   └── manage.py
├── tests/                    # Test suite
│   ├── conftest.py          # Fixtures
│   ├── test_strategies.py
│   ├── test_registry.py
│   └── test_promo_service.py
├── Dockerfile               # Multi-stage (test gating)
├── docker-compose.yml
├── requirements.txt
├── pytest.ini
└── README.md
```

## 🔐 Production Features

- **Pessimistic Locking**: Prevents voucher double-redemption
- **Atomic Transactions**: All-or-nothing voucher updates
- **Error Handling**: Meaningful validation errors
- **Decimal Precision**: Financial accuracy
- **CORS/Security**: Django security middleware
- **Gunicorn + Uvicorn**: Production ASGI server
- **Static Files**: WhiteNoise + collectstatic
- **Migrations**: Version-controlled schema changes

## 🐳 Docker Build Pipeline

```
build-base
    ↓
[test-stage] ← pytest runs here, fails = build stops ✋
    ↓
[production-stage] ← only built if tests pass ✅
    ↓
django_app container ready for deployment
```

## 🚧 Future Improvements

- [ ] Async strategy execution (Celery)
- [ ] Caching layer (Redis)
- [ ] Advanced analytics (audit logs)
- [ ] Bulk voucher import/export
- [ ] QR code generation
- [ ] Rate limiting per user
- [ ] Promo scheduling (start/end dates)

## 📝 Notes for Portfolio Reviewers

**What I'm proud of:**
1. **Clean Architecture** — Strategies don't know about DB, service handles atomicity
2. **No Circular Imports** — Signal pattern keeps models and utils decoupled
3. **Test Coverage** — 26 passing tests, 100% of core logic covered
4. **Production-Ready** — Docker multi-stage build enforces tests before deployment
5. **Type Safety** — Decimal for money, proper type hints throughout

**Design Decisions:**
- Pessimistic locking over optimistic: prevents race conditions in high-concurrency scenarios
- Strategy pattern: makes it trivial to add new discount types without touching existing code
- Signal-based voucher generation: avoids tight coupling between models and utils
- Service layer orchestration: separates business logic from Django framework concerns

## 📄 License

This project is licensed under CC BY-NC 4.0.

Non-commercial use (including learning and hiring evaluation) is allowed.
Commercial use requires a separate license. Please contact the author.

---

**Questions?** Feel free to review the code or ask about architecture decisions!
