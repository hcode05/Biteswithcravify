from django.db.models.signals import post_save,pre_save
from django.dispatch import receiver
from .models import User, UserProfile

# ✅ Signal logic placed at bottom and linked properly
@receiver(post_save, sender=User)
def post_save_create_profile_receiver(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
        print('UserProfile created for', instance.username)
    else:
        try:
            instance.userprofile.save()
            print('UserProfile updated for', instance.username)
        except UserProfile.DoesNotExist:
            UserProfile.objects.create(user=instance)
            print('UserProfile created later for', instance.username)

@receiver(pre_save, sender=User)
def pre_save_user_profile_receiver(sender, instance, **kwargs):
    print(instance.username, 'is being saved')