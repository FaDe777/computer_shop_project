from django.dispatch.dispatcher import receiver

from .models import *

@receiver(pre_delete,sender=UserCustom)
def avatar_delete(sender,instance,**kwargs):
    instance.avatar.delete()

@receiver(pre_save, sender=UserCustom)
def delete_old_image(sender, instance, **kwargs):
    if instance.pk:
        existing_image = UserCustom.objects.get(pk=instance.pk)
        print(instance.avatar)
        print(existing_image.avatar)
        if instance.avatar and existing_image.avatar != instance.avatar:
            existing_image.avatar.delete()

@receiver(pre_save,sender=Components)
def ggg(sender,instance,**kwargs):
    if instance.quantity <= 0:
        instance.in_stock = False
    else:
        instance.in_stock = True