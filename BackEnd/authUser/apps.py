from django.apps import AppConfig



class AuthuserConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'authUser'
    
    def ready(self):
        import authUser.signals  # load signals
