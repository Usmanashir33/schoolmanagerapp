from django.db.models.signals import pre_save, post_save,post_delete
from django.dispatch import receiver
from authUser.models import User
from .models import Director
from school.models import ActivityLog, School,SchoolPermission, SchoolRole

# update director 
@receiver(post_save, sender=Director) 
def update_director_user(sender, instance, **kwargs):
    if instance.user_id:
        user = instance.user
        
        user.username=instance.email
        user.first_name=instance.first_name
        user.last_name=instance.last_name
        user.middle_name = instance.middle_name
        user.email = instance.email
        user.phone_number = instance.phone
        user.role = instance.role
        user.gender = instance.gender
        user.save()

# # create permissions for director when school is created
@receiver(post_save, sender=SchoolPermission) 
def create_director_permission_settings(sender, instance, created ,**kwargs):
    if created :
        director = instance.school.director
        if (
                director and
                director.user and
                director.user.school_role and
                director.user.school_role.name == "Director"
            ):
            director.user.school_role.permissions.add(instance)
            director.user.save()
            
# if permission is deleted 
@receiver(post_delete, sender=SchoolPermission)
def remove_director_permission_settings(  sender,  instance,  **kwargs): 
    director = instance.school.director

    if (
        director and
        director.user and
        director.user.school_role and
        director.user.school_role.name == "Director"
    ):

        director.user.school_role.permissions.remove(
            instance
        )