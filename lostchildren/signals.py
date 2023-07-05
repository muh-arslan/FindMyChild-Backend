import os
import shutil
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from .models import LostChild, FoundChild


def delete_child_images(instance, child_type):
    # Building the path to the directory containing the child's images
    dir_path = os.path.join(
        'media', f'Children/{child_type}_children_images', str(instance.id))

    # Deleting the directory and all its contents
    try:
        shutil.rmtree(dir_path)
    except FileNotFoundError:
        pass  # Directory doesn't exist, so no need to delete it
def delete_child_image(filePath):
    # Building the path to the directory containing the child's images
    # dir_path = os.path.join('media', f'Children/{child_type}_children_images', str(instance.id))

    # Building the path to the file to be deleted
    file_path = os.path.join(filePath)
    print(file_path)
    # Deleting the file
    try:
        os.remove(filePath)
    except OSError:
        # Handle any exceptions that occur during file deletion
        pass


@receiver(pre_delete, sender=LostChild)
def delete_lost_child_images(sender, instance, **kwargs):
    delete_child_images(instance, 'lost')


@receiver(pre_delete, sender=FoundChild)
def delete_found_child_images(sender, instance, **kwargs):
    delete_child_images(instance, 'found')
