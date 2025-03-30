from django.db import models
from django.utils import timezone
from ckeditor.fields import RichTextField
from datetime import datetime, timedelta
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


class Cart(models.Model):
    cart_id = models.CharField(max_length=255, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="carts")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    size = models.CharField(max_length=50) 
    color = models.CharField(max_length=50) 
    qty = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    shipping = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    date = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        """Automatically calculate subtotal and total before saving."""
        self.subtotal = self.price * self.qty
        self.total = self.subtotal + self.shipping + self.tax
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Cart {self.cart_id} - {self.user if self.user else 'Guest'} - {self.product.name}"


class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)  # Unique coupon code (e.g., "SAVE10")
    discount_type = models.CharField(
        max_length=10,
        choices=[("fixed", "Fixed Amount"), ("percent", "Percentage")],
        default="percent",
    )  # Whether it's a percentage or fixed discount
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)  # Amount or percentage of discount
    min_order_value = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Minimum cart total to apply
    max_discount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Max discount cap (for percentage)
    usage_limit = models.PositiveIntegerField(default=1)  # Number of times this coupon can be used
    used_count = models.PositiveIntegerField(default=0)  # Number of times it has been used
    is_active = models.BooleanField(default=True)  # Whether the coupon is currently active
    start_date = models.DateTimeField(default=datetime.now)  # When the coupon starts
    end_date = models.DateTimeField(default=datetime.now() + timedelta(days=30))  # Expiry date

    def is_valid(self):
        """Check if the coupon is valid."""
        now = datetime.now()
        return (
            self.is_active
            and self.start_date <= now <= self.end_date
            and self.used_count < self.usage_limit
        )

    def apply_discount(self, total_amount):
        """Apply discount to a given total."""
        if not self.is_valid():
            return total_amount  # No discount if the coupon is invalid

        if self.discount_type == "percent":
            discount = (self.discount_value / 100) * total_amount
            if self.max_discount:
                discount = min(discount, self.max_discount)  # Apply max discount cap if set
        else:  # Fixed discount
            discount = self.discount_value

        return max(total_amount - discount, 0)  # Ensure total doesn't go below 0

    def __str__(self):
        return f"{self.code} - {self.discount_value}{'%' if self.discount_type == 'percent' else ''} Off"


