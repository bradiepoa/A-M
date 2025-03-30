from django.db import models
from django.utils import timezone
from ckeditor.fields import RichTextField 
from django.contrib.auth.models import AbstractUser, Group, Permission

class User(AbstractUser):
    ROLE_CHOICES = (
        ("customer", "Customer"),
        ("vendor", "Vendor"),
        ("healer", "Healer"),
        ("doctor", "Doctor"),
        ("herbalist", "Herbalist"),
        ("non", "Non"),
    )
    username = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="non")

    groups = models.ManyToManyField(Group, related_name="custom_user_groups", blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name="custom_user_permissions", blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["role"]

    def __str__(self):
        return f"{self.email} ({self.role})"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="profiles",blank=True)
    full_name = models.CharField(max_length=255)
    mobile = models.CharField(max_length=255)
    
    def __str__(self):
        return self.user.username
    def save(self, *args, **kwargs):
        if not self.full_name:
            self.full_name = self.user.username
        super(Profile, self).save(*args, **kwargs)
    

class Category(models.Model):
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to="category", blank=True)

    def __str__(self):
        return self.title

class Product(models.Model):
    STATUS = (
        ("published", "Published"),
        ("draft", "Draft"),
    )

    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to="products", blank=True)
    description = RichTextField()  # Corrected CKEditor field
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    regular_price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)  # Fixed max_digits

    stock = models.PositiveIntegerField(default=0, blank=True)
    shipping = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    status = models.CharField(choices=STATUS, max_length=50, default="published")
    feature = models.BooleanField(default=False, verbose_name="Marketplace featured")

    vendor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)  # Fixed typo

    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name


class Variant(models.Model):  # Fix inheritance
    product = models.ForeignKey(
        "Product",on_delete=models.CASCADE, related_name="variants")
    name = models.CharField(max_length=1000, verbose_name="Variant name")

    def items(self):
        return self.variant_items.all()

    def __str__(self):
        return self.name

class VariantItem(models.Model):
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE, related_name="variant_items")
    title = models.CharField(max_length=255, verbose_name="Title")
    content = models.CharField(max_length=255, verbose_name="Content")

    def __str__(self):
        return self.title

