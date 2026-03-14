from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import UserProfile
from expenses.models import Category

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwarga):
    if created:
        #Create profile
        UserProfile.objects.create(user=instance)

        #Create default categories
        default_category = [
            {'name': 'Food', 'icon': '🍔'},
            {'name': 'Travel', 'icon': '✈️'},
            {'name': 'Rent', 'icon': '🏠'},
            {'name': 'Health', 'icon': '💊'},
            {'name': 'Entertainment', 'icon': '🎬'},
            {'name': 'Shopping', 'icon': '🛍️'},
            {'name': 'Salary', 'icon': '💼'},
            {'name': 'Other', 'icon': '📦'},
        ]

        for cat in default_category:
            Category.objects.create(
                user=instance,
                name=cat['name'],
                icon=cat['icon']
            )

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'userprofile'):
        instance.userprofile.save()