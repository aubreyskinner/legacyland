from django.shortcuts import render
from .models import Property
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from .models import Agent
from django.utils import timezone
from django.core.files.base import ContentFile
import base64
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
import stripe
from django.conf import settings
from django.http import JsonResponse
from django.core.mail import EmailMessage



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

@require_POST
def add_to_cart(request, property_id):
    prop = get_object_or_404(Property, id=property_id)
    option = int(request.POST.get("financing_option"))

    CartItem.objects.create(
        property=prop,
        financing_option=option,
        session_key=request.session.session_key or request.session.save() or request.session.session_key
    )
    return redirect('view_cart')



def view_cart(request):
    session_key = request.session.session_key or request.session.save() or request.session.session_key
    cart_items = CartItem.objects.filter(session_key=session_key)

    total_due_today = 0
    for item in cart_items:
        total_due_today += item.get_down_payment_amount()

    return render(request, 'core/cart.html', {
        'cart_items': cart_items,
        'total_due_today': total_due_today,
        'STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLIC_KEY,
    })


def remove_from_cart(request, item_id):
    session_key = request.session.session_key or request.session.save() or request.session.session_key
    item = get_object_or_404(CartItem, id=item_id, session_key=session_key)
    item.delete()
    return redirect('view_cart')



def checkout(request):
    # Placeholder: Implement payment logic or success page later
    return render(request, 'core/checkout_success.html')

@require_POST
def create_checkout_session(request, cart_id):
    cart_item = get_object_or_404(CartItem, id=cart_id)

    amount = cart_item.get_down_payment_amount()

    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': cart_item.property.title,
                    },
                    'unit_amount': int(amount * 100),
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url='http://127.0.0.1:8000/success/',
            cancel_url='http://127.0.0.1:8000/cancel/',
            metadata={
                'buyer_name': cart_item.buyer_name,
                'property_id': cart_item.property.id
            }
        )
        return JsonResponse({'id': checkout_session.id})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

        
def success_view(request):
    return render(request, 'core/checkout_success.html')

def cancel_view(request):
    return render(request, 'core/checkout_cancel.html')

@require_POST
def verify_and_checkout(request, cart_id):
    cart_item = get_object_or_404(CartItem, id=cart_id)

    cart_item.buyer_name = request.POST.get('buyer_name')
    cart_item.buyer_email = request.POST.get('buyer_email')
    cart_item.buyer_phone = request.POST.get('buyer_phone')
    cart_item.agreed_to_terms = bool(request.POST.get('agree_terms'))

    # New: typed signature, IP, timestamp
    cart_item.typed_signature = request.POST.get('typed_signature')
    cart_item.signature_ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR'))
    cart_item.signature_timestamp = timezone.now()

    # Handle ID document upload
    uploaded_file = request.FILES.get('id_document')
    if uploaded_file:
        cart_item.id_document = uploaded_file

    # Optional: Handle base64 canvas signature (if ever restored)
    signature_data_url = request.POST.get('signature_data')
    if signature_data_url:
        try:
            format, imgstr = signature_data_url.split(';base64,')
            ext = format.split('/')[-1]
            signature_file = ContentFile(base64.b64decode(imgstr), name=f'signature_{cart_item.id}.{ext}')
            cart_item.signature_image = signature_file
        except Exception:
            pass  # Fail silently if base64 is malformed

    cart_item.save()

    # Email notification
    body = f"""
Successfully submitted buyer verification information:

Name: {cart_item.buyer_name}
Email: {cart_item.buyer_email}
Phone: {cart_item.buyer_phone}
Property: {cart_item.property.title}
Option: {cart_item.financing_option}

Digital Signature: {cart_item.typed_signature}
Signed At: {cart_item.signature_timestamp}
IP Address: {cart_item.signature_ip}
    """

    email = EmailMessage(
        subject=f"Buyer Verification: {cart_item.buyer_name}",
        body=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=['office@legacylandcompany.org'],
        cc=[cart_item.buyer_email] if cart_item.buyer_email else []
    )

    if uploaded_file:
        uploaded_file.seek(0)
        email.attach(uploaded_file.name, uploaded_file.read(), uploaded_file.content_type)

    if cart_item.signature_image:
        with open(cart_item.signature_image.path, 'rb') as f:
            email.attach(cart_item.signature_image.name, f.read(), 'image/png')

    email.send(fail_silently=False)

    # ✅ Stripe checkout
    stripe.api_key = settings.STRIPE_SECRET_KEY

    checkout_session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'usd',
                'unit_amount': int(cart_item.get_down_payment_amount() * 100),
                'product_data': {
                    'name': cart_item.property.title,
                },
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url=request.build_absolute_uri('/success/'),
        cancel_url=request.build_absolute_uri('/cancel/'),
        metadata={
            'buyer_name': cart_item.buyer_name,
            'property_id': cart_item.property.id
        }
    )

    return redirect(checkout_session.url)


def process(request):
    return render(request, 'core/process.html')

def contact(request):
    return render(request, 'core/contact.html')
