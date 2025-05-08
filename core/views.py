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


@login_required
def add_to_cart(request, property_id):
    prop = get_object_or_404(Property, id=property_id)
    CartItem.objects.get_or_create(user=request.user, property=prop)
    return redirect('view_cart')

@login_required
def view_cart(request):
    cart_items = CartItem.objects.filter(user=request.user)
    return render(request, 'core/cart.html', {'cart_items': cart_items})
