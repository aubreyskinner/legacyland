"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from core.views import create_checkout_session, success_view, cancel_view
from django.urls import path
from core import views as core_views
from core import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', core_views.home, name='home'),
    path('properties/', core_views.property_list, name='property_list'),
    path('contact-agent/<int:agent_id>/', views.contact_agent, name='contact_agent'),
    path('become-an-agent/', views.become_agent, name='become_agent'),
    path('book-meeting/', views.book_meeting, name='book_meeting'),
    path('add-to-cart/<int:property_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    path('remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('terms/', TemplateView.as_view(template_name='core/terms.html'), name='terms'),
    path('success/', success_view, name='checkout_success'),
    path('cancel/', cancel_view, name='checkout_cancel'),
    path('verify-and-checkout/<int:cart_id>/', views.verify_and_checkout, name='verify_and_checkout'),
    path('create-checkout-session/<int:cart_id>/', views.create_checkout_session, name='create_checkout_session'),


]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)