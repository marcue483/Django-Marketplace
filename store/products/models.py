from django.db import models
from django.urls import reverse
from django.utils import timezone
from decimal import Decimal
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill
from django.contrib.auth.models import User

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('category-detail', kwargs={'slug': self.slug})

class Product(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products', null=True, blank=True)
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2) # This will be the base price
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    image_thumbnail = ImageSpecField(
        source='image',
        processors=[ResizeToFill(300, 300)],
        format='JPEG',
        options={'quality': 90}
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('product-detail', kwargs={'pk': self.pk})

    def get_active_discount(self):
        """Checks for an active discount for this product."""
        now = timezone.now().date()
        active_discount = self.discounts.filter(
            is_active=True,
            start_date__lte=now,
            end_date__gte=now
        ).order_by('-discount_percentage').first() # Get the best discount if multiple overlap
        return active_discount

    @property
    def on_sale(self):
        return self.get_active_discount() is not None

    @property
    def display_price(self):
        """Returns the discounted price if a discount is active, otherwise the original price."""
        active_discount = self.get_active_discount()
        if active_discount:
            discount_amount = (self.price * active_discount.discount_percentage) / Decimal(100)
            return (self.price - discount_amount).quantize(Decimal('0.01'))
        return self.price

class Discount(models.Model):
    product = models.ForeignKey(Product, related_name='discounts', on_delete=models.CASCADE)
    name = models.CharField(max_length=255, help_text="e.g., Summer Sale, Clearance")
    discount_percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        help_text="Percentage discount (e.g., 10.00 for 10% off)"
    )
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.discount_percentage}% off {self.product.name})"

    class Meta:
        ordering = ['-start_date', '-discount_percentage']
        # Prevent overlapping discounts for the same product if desired, though current logic picks best
        # unique_together = [('product', 'start_date', 'end_date')] 
