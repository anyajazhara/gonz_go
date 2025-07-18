from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model

# Create your models here.
class FoodStall(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    slug = models.SlugField(unique=True)
    image = models.ImageField(upload_to='stalls/', blank=True)
    qr_code = models.ImageField(upload_to="stall_qrcodes/", blank=True, null=True)
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        default=None,
        related_name='owned_stalls'
    )

    def __str__(self):
        return self.name
    
class MenuCategory(models.Model):
    stall = models.ForeignKey(FoodStall, on_delete=models.CASCADE, related_name='categories')
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = "Menu categories"

    def __str__(self):
        return f"{self.name} ({self.stall.name})"
    
class MenuItem(models.Model):
    category = models.ForeignKey(MenuCategory, on_delete=models.CASCADE, related_name='items')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return self.name
    
class MenuOption(models.Model):
    item = models.ForeignKey('MenuItem', on_delete=models.CASCADE, related_name='options')
    name = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return f"{self.item.name} - {self.name} (₱{self.price})"
    
class Order(models.Model):
    stall = models.ForeignKey(FoodStall, on_delete=models.CASCADE, related_name="orders")
    placed_at = models.DateTimeField(auto_now_add=True)
    eta = models.TimeField("ETA at Gonz")
    total = models.DecimalField(max_digits=10, decimal_places=2)
    receipt = models.ImageField(upload_to="order_receipts/")
    customer_name = models.CharField(max_length=200, blank=True)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="orders")
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending'
    )

    def __str__(self):
        return f"Order #{self.id} at {self.stall.name} ({self.placed_at.strftime('%Y-%m-%d %H:%M')})"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    item_name = models.CharField(max_length=255)
    option_name = models.CharField(max_length=255, blank=True)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.item_name} ({self.option_name}) x{self.quantity}"