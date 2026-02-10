from django.contrib import admin
import csv
from django.http import HttpResponse
from .models import Promo, VoucherCode


class PromoAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "total_voucher", "voucher_count", "created_at", "updated_at")
    search_fields = ("name",)
    readonly_fields = ("created_at", "updated_at")
    actions = ("export_promos_csv",)

    def voucher_count(self, obj):
        return obj.vouchercode_set.count()
    voucher_count.short_description = "Voucher count"

    def export_promos_csv(self, request, queryset):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="promos.csv"'
        writer = csv.writer(response)
        writer.writerow(["id", "name", "total_voucher", "voucher_count", 
                         "created_at", "updated_at"])
        for obj in queryset:
            writer.writerow([
                obj.id, 
                obj.name, 
                obj.total_voucher, 
                obj.vouchercode_set.count(), 
                obj.created_at.isoformat() if obj.created_at else "", 
                obj.updated_at.isoformat() if obj.updated_at else ""])
        return response
    export_promos_csv.short_description = "Export selected promos as CSV"


class VoucherCodeAdmin(admin.ModelAdmin):
    list_display = ("id", "code", "promo", "activated", "reference", 
                    "created_at", "updated_at")
    list_filter = ("activated", "promo")
    search_fields = ("code", "promo__name")
    readonly_fields = ("created_at", "updated_at")
    list_select_related = ("promo",)
    actions = ("activate_codes", "deactivate_codes", "export_vouchercodes_csv")

    def activate_codes(self, request, queryset):
        updated = queryset.update(activated=True)
        self.message_user(request, f"{updated} voucher(s) marked as activated.")
    activate_codes.short_description = "Mark selected voucher codes as activated"

    def deactivate_codes(self, request, queryset):
        updated = queryset.update(activated=False)
        self.message_user(request, f"{updated} voucher(s) marked as deactivated.")
    deactivate_codes.short_description = "Mark selected voucher codes as deactivated"

    def export_vouchercodes_csv(self, request, queryset):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="vouchercodes.csv"'
        writer = csv.writer(response)
        writer.writerow(["id", "code", "promo_id", "promo_name", "activated", "reference", 
                         "created_at", "updated_at"])
        for obj in queryset.select_related("promo"):
            writer.writerow([obj.id, 
                             obj.code, 
                             obj.promo.id if obj.promo else "", 
                             obj.promo.name if obj.promo else "", 
                             obj.activated, 
                             obj.reference if obj.reference is not None else "", 
                             obj.created_at.isoformat() if obj.created_at else "", 
                             obj.updated_at.isoformat() if obj.updated_at else ""])
        return response
    export_vouchercodes_csv.short_description = "Export selected voucher codes as CSV"


admin.site.register(Promo, PromoAdmin)
admin.site.register(VoucherCode, VoucherCodeAdmin)
