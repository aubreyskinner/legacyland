from django.db import models
from django.contrib.auth.models import User

class Property(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=100)
    acreage = models.DecimalField(max_digits=7, decimal_places=2)

    # Option 1
    term_years_1 = models.IntegerField(blank=True, null=True)
    monthly_payment_1 = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    down_payment_1 = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    total_price_1 = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    interest_1 = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    financing_note_1=models.TextField(blank=True, help_text="Optional custom financing message")
    # Option 2
    term_years_2 = models.IntegerField(blank=True, null=True)
    monthly_payment_2 = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    down_payment_2 = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    total_price_2 = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    interest_2 = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    financing_note_2=models.TextField(blank=True, help_text="Optional custom financing message")

    # Option 3
    term_years_3 = models.IntegerField(blank=True, null=True)
    monthly_payment_3 = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    down_payment_3 = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    total_price_3 = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    interest_3 = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    financing_note_3=models.TextField(blank=True, help_text="Optional custom financing message")

    def __str__(self):
        return self.title


class PropertyImage(models.Model):
    property = models.ForeignKey(Property, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='property_images/')

    def __str__(self):
        return f"Image for {self.property.title}"

class Agent(models.Model):
    name = models.CharField(max_length=100)
    title = models.CharField(max_length=100, default="Land Specialist")
    bio = models.TextField()
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    photo = models.ImageField(upload_to='agent_photos/')
    
    def __str__(self):
        return self.name
    
class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    financing_option = models.IntegerField(choices=[(1, 'Option 1'), (2, 'Option 2'), (3, 'Option 3')])

    def __str__(self):
        return f"{self.user.username} - {self.property.title} (Option {self.financing_option})"
