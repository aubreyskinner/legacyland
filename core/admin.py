from django.contrib import admin
from .models import Agent
from .models import Property, PropertyImage
# Register your models here.
admin.site.register(Agent)
admin.site.register(Property)
admin.site.register(PropertyImage)