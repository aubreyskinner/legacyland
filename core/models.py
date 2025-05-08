from django.db import models
from django.contrib.auth.models import User

class Property(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    acreage = models.DecimalField(max_digits=7, decimal_places=2)
    term_years = models.IntegerField(help_text="Number of years for financing")
    monthly_payment = models.DecimalField(max_digits=10, decimal_places=2)
    
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
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.property.title}"