from django.shortcuts import render
from .models import Property

def home(request):
    return render(request, 'core/home.html')


def property_list(request):
    properties = Property.objects.all()

    # Filters
    location = request.GET.get('location')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    min_acreage = request.GET.get('min_acreage')
    max_acreage = request.GET.get('max_acreage')

    if location:
        properties = properties.filter(location__icontains=location)
    if min_price:
        properties = properties.filter(price__gte=min_price)
    if max_price:
        properties = properties.filter(price__lte=max_price)
    if min_acreage:
        properties = properties.filter(acreage__gte=min_acreage)
    if max_acreage:
        properties = properties.filter(acreage__lte=max_acreage)

    return render(request, 'core/property_list.html', {'properties': properties})