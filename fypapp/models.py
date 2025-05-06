from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.conf import settings
from django.utils.timezone import now  
from django.utils.html import mark_safe

# ---------------- Custom User Manager ----------------
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)

# ---------------- Custom User Model ----------------
class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    username = None  
    USERNAME_FIELD = "email"  
    REQUIRED_FIELDS = []  

    objects = CustomUserManager()

    def __str__(self):
        return self.email

# ---------------- Category Model ----------------
class Category(models.Model):
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to="cat_imgs/", null=True, blank=True)

    class Meta:
        verbose_name_plural = '1. Categories'

    def image_tag(self):
        return mark_safe('<img src="%s" width="50" height="50" />' % (self.image.url))

    def __str__(self):
        return self.title

# ---------------- Brands Model ----------------
class Brands(models.Model):  
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to="category_images/", null=True, blank=True)

    class Meta:
        verbose_name_plural = "2. Brands"

    def image_tag(self):
        return mark_safe('<img src="%s" width="150" height="150" />' % (self.image.url))    

    def __str__(self):
        return self.title

# ---------------- Products Model ----------------
class Products(models.Model): 
    image = models.ImageField(upload_to='product-images/')
    title = models.CharField(max_length=100, unique=True)
    slug = models.CharField(max_length=400)
    processor = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    brand = models.ForeignKey(Brands, on_delete=models.CASCADE)
    status = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    is_new = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "3. Products"

    def __str__(self):
        return self.title

    def image_tag(self):
        return mark_safe('<img src="%s" width="50" height="50" />' % (self.image.url))
    
# trending products


# ---------------- Ram Model ----------------
class Ram(models.Model):
    ram = models.CharField(max_length=50)

    class Meta:
        verbose_name_plural = "4. Ram"

    def __str__(self):
        return self.ram

# ---------------- Storage Model ----------------
class Storage(models.Model):
    storage = models.CharField(max_length=50)

    class Meta:
        verbose_name_plural = "5. Storage"

    def __str__(self):
        return self.storage

# ---------------- Product Attribute Model -------------------
class ProductAttribute(models.Model):
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    ram = models.ForeignKey(Ram, on_delete=models.CASCADE)
    storage = models.ForeignKey(Storage, on_delete=models.CASCADE)
    price = models.IntegerField()

    class Meta:
        verbose_name_plural = "6. Products Attribute"

    def __str__(self):
        return f"{self.product.title} ({self.ram.ram} | {self.storage.storage})"

# ---------------- Cart Model ----------------

class Cart(models.Model):
    # Use settings.AUTH_USER_MODEL instead of directly referencing User
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product_id = models.IntegerField()  # or ForeignKey to Product
    attribute_id = models.IntegerField()  # or ForeignKey to Attribute
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - Product {self.product_id} - Attr {self.attribute_id}"

class CartItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)  # Made nullable
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    attribute = models.ForeignKey(ProductAttribute, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        ram = self.attribute.ram.ram if self.attribute else "No Attribute"
        storage = self.attribute.storage.storage if self.attribute else "No Storage"
        return f"{self.quantity} x {self.product.title} ({ram} | {storage})"

# ---------------- Wishlist Model ----------------
class WishlistItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    attribute = models.ForeignKey(ProductAttribute, on_delete=models.SET_NULL, null=True, blank=True)
    added_at = models.DateTimeField(default=now)

    class Meta:
        unique_together = ('user', 'product', 'attribute')  # optional but nice to avoid duplicates

    def __str__(self):
        ram = self.attribute.ram.ram if self.attribute else "No RAM"
        storage = self.attribute.storage.storage if self.attribute else "No Storage"
        return f"{self.user.email} - {self.product.title} ({ram} | {storage})"

# ---------------- Payment Model -----------------
from django.db import models
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()

class Payment(models.Model):
    PAYMENT_METHODS = [
        ('card', 'Credit/Debit Card'),
        ('bank', 'Bank Transfer'),
        ('wallet', 'Wallet'),
        ('cod', 'Cash on Delivery'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('failed', 'Failed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    transaction_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} | {self.method} | {self.status}"