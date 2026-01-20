from django.apps import AppConfig


class TeacherConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'teacher'

    def ready(self):
        import teacher.signals  # Import signals to ensure they are registered