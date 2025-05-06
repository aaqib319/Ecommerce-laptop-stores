import django
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fyp.settings")  # Replace with your actual project name
django.setup()

from fypapp.models import WishlistItem, ProductAttribute

# Loop through WishlistItems with missing attributes
for item in WishlistItem.objects.filter(attribute__isnull=True):
    default_attribute = ProductAttribute.objects.filter(product=item.product).first()

    if default_attribute:
        item.attribute = default_attribute
        item.save(update_fields=["attribute"])  
        print(f"✅ Updated: {item.product.title} -> {default_attribute}")
    else:
        print(f"⚠️ No matching attribute found for {item.product.title}")

