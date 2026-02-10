from django.apps import AppConfig


class PromoinConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.promoin'

    def ready(self):
        # import signals to register handlers
        import apps.promoin.signals  # noqa