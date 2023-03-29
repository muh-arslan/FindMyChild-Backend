import os
import shutil
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from .models import LostChild


@receiver(pre_delete, sender=LostChild)
def delete_child_images(sender, instance, **kwargs):
    # Building the path to the directory containing the child's images
    dir_path = os.path.join('media', 'lost_children_images', str(instance.id))

    # Deleting the directory and all its contents
    try:
        shutil.rmtree(dir_path)
    except FileNotFoundError:
        pass  # Directory doesn't exist, so no need to delete it
