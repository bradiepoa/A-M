from django.db import models
from django.utils import timezone
from ckeditor.fields import RichTextField
from datetime import datetime, timedelta
from django.contrib.auth.models import AbstractUser, Group, Permission
import uuid

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
    vendor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="coupons")  # Fixed typo 'vender' → 'vendor'
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
    start_date = models.DateTimeField(default=timezone.now)  # Start date using timezone-aware datetime
    end_date = models.DateTimeField(default=timezone.now() + timedelta(days=30))  # Expiry date

    def is_valid(self):
        """Check if the coupon is valid."""
        now = timezone.now()
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

    def increment_usage(self):
        """Increment the used_count when the coupon is applied."""
        if self.is_valid():
            self.used_count += 1
            self.save()

    def __str__(self):
        return f"{self.code} - {self.discount_value}{'%' if self.discount_type == 'percent' else ''} Off"


class Order(models.Model):
    ORDER_STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
        ("canceled", "Canceled"),
    ]

    PAYMENT_STATUS_CHOICES = [
        ("pending", "Pending"),
        ("completed", "Completed"),
        ("failed", "Failed"),
        ("refunded", "Refunded"),
    ]

    PAYMENT_METHOD_CHOICES = [
        ("credit_card", "Credit Card"),
        ("paypal", "PayPal"),
        ("bank_transfer", "Bank Transfer"),
        ("cod", "Cash on Delivery"),
    ]

    order_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)  # Unique order identifier
    payment_id = models.CharField(max_length=255, blank=True, null=True)  # Payment transaction ID
    vendor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="vendor_orders")  # Seller/vendor
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="customer_orders")  # Buyer/customer
    address = models.TextField()  # Shipping address
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)  # Total before additional costs
    shipping = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Shipping fee
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Tax amount
    service_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Platform/service fee
    initial_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Total before discount
    coupon = models.ForeignKey("Coupon", on_delete=models.SET_NULL, null=True, blank=True)  # Applied coupon
    saved = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Amount saved from discounts
    total = models.DecimalField(max_digits=10, decimal_places=2)  # Final total after discounts
    payment_status = models.CharField(
        max_length=20, choices=PAYMENT_STATUS_CHOICES, default="pending"
    )  # Payment status
    payment_method = models.CharField(
        max_length=20, choices=PAYMENT_METHOD_CHOICES, default="credit_card"
    )  # Payment method
    order_status = models.CharField(
        max_length=20, choices=ORDER_STATUS_CHOICES, default="pending"
    )  # Order processing status
    date = models.DateTimeField(default=timezone.now)  # Order creation date

    def calculate_totals(self):
        """Calculate order totals and apply any coupon discount."""
        self.initial_total = self.subtotal + self.shipping + self.tax + self.service_fee
        if self.coupon and self.coupon.is_valid():
            discounted_total = self.coupon.apply_discount(self.initial_total)
            self.saves = self.initial_total - discounted_total
            self.total = discounted_total
        else:
            self.total = self.initial_total
            self.saves = 0.00

    def save(self, *args, **kwargs):
        """Auto-calculate totals before saving."""
        self.calculate_totals()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order {self.order_id} - {self.customer.username} - {self.order_status}"



class OrderedItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="ordered_items")  # Link to Order
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE)  # Product variant being ordered
    product = models.ForeignKey(Product, on_delete=models.CASCADE)  # The product being ordered
    shipping_service = models.CharField(max_length=100, null=True, blank=True)  # Shipping service used
    tracking_id = models.CharField(max_length=255, null=True, blank=True)  # Tracking ID for shipment
    quantity = models.PositiveIntegerField(default=1)  # Quantity of the item ordered
    color = models.CharField(max_length=50, null=True, blank=True)  # Color of the product (if applicable)
    size = models.CharField(max_length=50, null=True, blank=True)  # Size of the product (if applicable)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price per unit of the variant
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)  # Price before shipping, tax, etc.
    shipping = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Shipping fee
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Tax amount
    total = models.DecimalField(max_digits=10, decimal_places=2)  # Total price after calculations
    initial_total = models.DecimalField(max_digits=10, decimal_places=2)  # Total before coupon discount

    item_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)  # Unique item identifier
    vendor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="ordered_items")  # Vendor of the product
    date = models.DateTimeField(default=timezone.now)  # Date when the item was added to the order

    def save(self, *args, **kwargs):
        """Automatically calculate totals before saving."""
        self.subtotal = self.price * self.quantity  # Calculate subtotal (price * quantity)
        self.initial_total = self.subtotal + self.shipping + self.tax  # Total before coupon
        self.total = self.initial_total  # Total after all calculations

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.variant.name} (x{self.quantity}) - {self.order.order_id}"

