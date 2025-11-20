from django.apps import AppConfig


class EliteInteriorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'elite_interior'

    
    def ready(self):
        import elite_interior.templatetags.extra_filters
        import elite_interior.templatetags.format_extras