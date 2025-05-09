from django.shortcuts import render
from .models import Property
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from .models import Agent
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from .models import CartItem
from django.views.decorators.http import require_POST
import stripe
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import redirect
from django.views import View

stripe.api_key = settings.STRIPE_SECRET_KEY

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

def contact_agent(request, agent_id):
    agent = get_object_or_404(Agent, id=agent_id)

    if request.method == "POST":
        # Process form (simplified for now)
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        message = request.POST.get("message")
        # You'd send an email, save to database, etc. here

        return render(request, 'core/contact_success.html', {"agent": agent})

    return render(request, 'core/contact_agent.html', {"agent": agent})

from django.core.mail import send_mail
from django.shortcuts import render, get_object_or_404
from .models import Agent

def contact_agent(request, agent_id):
    agent = get_object_or_404(Agent, id=agent_id)

    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        message = request.POST.get("message")

        full_message = f"""
You have a new contact from Legacy Land Company:

Name: {name}
Email: {email}
Phone: {phone}

Message:
{message}
        """

        send_mail(
            subject=f"New message from {name}",
            message=full_message,
            from_email='legacylandinformation@gmail.com',  # Must match settings
            recipient_list=[agent.email],
            fail_silently=False,
        )

        return render(request, 'core/contact_success.html', {"agent": agent})

    return render(request, 'core/contact_agent.html', {"agent": agent})

def become_agent(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        experience = request.POST.get("experience")
        message = request.POST.get("message")

        full_message = f"""
New agent application:

Name: {name}
Email: {email}
Phone: {phone}

Experience:
{experience}

Message:
{message}
        """

        send_mail(
            subject=f"Agent Application from {name}",
            message=full_message,
            from_email=email,
            recipient_list=['office@legacylandcompany.org'],
            fail_silently=False,
        )

        return render(request, 'core/become_agent_success.html')

    return render(request, 'core/become_agent.html')

def book_meeting(request):
    agents = Agent.objects.all()

    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        agent_id = request.POST.get("agent")
        meeting_type = request.POST.get("meeting_type")
        date = request.POST.get("date")
        time = request.POST.get("time")
        notes = request.POST.get("notes")

        selected_agent = Agent.objects.get(id=agent_id)

        message = f"""
New Meeting Request:

Name: {name}
Email: {email}
Preferred Meeting Type: {meeting_type}
Date: {date}
Time: {time}

Notes:
{notes}
        """

        send_mail(
            subject=f"Meeting Request from {name}",
            message=message,
            from_email=email,
            recipient_list=[selected_agent.email, 'office@legacylandcompany.org'],
            fail_silently=False,
        )

        return render(request, 'core/book_meeting_success.html')

    return render(request, 'core/book_meeting.html', {'agents': agents})

def signup_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'core/signup.html', {'form': form})

@require_POST
@login_required
def add_to_cart(request, property_id):
    prop = get_object_or_404(Property, id=property_id)
    option = int(request.POST.get("financing_option"))

    CartItem.objects.create(
        user=request.user,
        property=prop,
        financing_option=option
    )
    return redirect('view_cart')

@login_required
def view_cart(request):
    cart_items = CartItem.objects.filter(user=request.user)

    total_due_today = 0
    for item in cart_items:
        if item.financing_option == 1:
            total_due_today += item.property.down_payment_1 or 0
        elif item.financing_option == 2:
            total_due_today += item.property.down_payment_2 or 0
        elif item.financing_option == 3:
            total_due_today += item.property.down_payment_3 or 0

    return render(request, 'core/cart.html', {
        'cart_items': cart_items,
        'total_due_today': total_due_today,
        'STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLIC_KEY,  # ✅ this is critical
    })


@login_required
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, user=request.user)
    item.delete()
    return redirect('view_cart')

@login_required
def checkout(request):
    # Placeholder: Implement payment logic or success page later
    return render(request, 'core/checkout_success.html')

class CreateCheckoutSessionView(View):
    def post(self, request, *args, **kwargs):
        # Step 1: Recalculate cart total for this user
        cart_items = CartItem.objects.filter(user=request.user)  # Adjust to your model

        if not cart_items.exists():
            return JsonResponse({'error': 'Cart is empty'}, status=400)
        print("Cart items:", cart_items)
        for item in cart_items:
             print("Item:", item, "Down payment:", item.get_down_payment_amount())

        # Assume you already calculate `total_due_today` in your view_cart
        total_due_today = sum(item.get_down_payment_amount() for item in cart_items)

        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': 'Property Purchase',
                        },
                        'unit_amount': int(total_due_today * 100),  # 💰 convert to cents
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url='http://127.0.0.1:8000/success/',
                cancel_url='http://127.0.0.1:8000/cancel/',
            )
            return JsonResponse({'id': checkout_session.id})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        
def success_view(request):
    return render(request, 'core/checkout_success.html')

def cancel_view(request):
    return render(request, 'core/checkout_cancel.html')