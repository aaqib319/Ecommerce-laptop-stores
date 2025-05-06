import os
import subprocess
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.staticfiles.storage import ManifestStaticFilesStorage

@receiver(post_save)
def auto_collectstatic(sender, **kwargs):
    if isinstance(sender, ManifestStaticFilesStorage):
        print("Running collectstatic automatically...")
        subprocess.run(["python", "manage.py", "collectstatic", "--noinput"])


from django.db.models.signals import post_save
from django.dispatch import receiver
from fypapp.models import WishlistItem, ProductAttribute

@receiver(post_save, sender=WishlistItem)
def update_wishlist_attribute(sender, instance, **kwargs):
    if instance.attribute is None:
        default_attribute = ProductAttribute.objects.filter(product=instance.product).first()
        if default_attribute:
            instance.attribute = default_attribute
            instance.save(update_fields=["attribute"])

