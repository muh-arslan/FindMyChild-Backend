from django.apps import AppConfig


class LostchildrenConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "lostchildren"

    def ready(self):
        import lostchildren.signals
