from django.shortcuts import render

# Create your views here.
from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, get_object_or_404, redirect
from .models import Property, PropertyImage, Buyer, Purchase
from .forms import BuyerForm, PurchaseForm, PropertyImageForm, PropertyForm
from django.db import transaction
from django.contrib import messages

def index(request):
    properties = Property.objects.filter(active=True).order_by('-created_at')
    # paginate 9 per page (3x3)
    from django.core.paginator import Paginator
    paginator = Paginator(properties, 9)
    page = request.GET.get('page', 1)
    props_page = paginator.get_page(page)
    return render(request, "listings/index.html", {"properties": props_page})

def property_detail(request, pk):
    prop = get_object_or_404(Property, pk=pk)
    images = prop.images.all()
    if request.method == "POST":
        buyer_form = BuyerForm(request.POST)
        purchase_form = PurchaseForm(request.POST, request.FILES)
        if buyer_form.is_valid() and purchase_form.is_valid():
            with transaction.atomic():
                buyer = buyer_form.save()
                purchase = purchase_form.save(commit=False)
                purchase.property = prop
                purchase.buyer = buyer
                purchase.ticket_price = prop.ticket_price
                # check availability
                if prop.available_tickets < purchase.quantity:
                    messages.error(request, "Not enough tickets available.")
                    return redirect(request.path)
                # reduce available tickets and save
                prop.available_tickets = prop.available_tickets - purchase.quantity
                prop.save()
                purchase.save()
            messages.success(request, "Purchase submitted. Payment verification pending.")
            return redirect("purchase_success", pk=purchase.pk)
    else:
        buyer_form = BuyerForm()
        purchase_form = PurchaseForm()
    context = {"property": prop, "images": images, "buyer_form": buyer_form, "purchase_form": purchase_form}
    return render(request, "listings/property_detail.html", context)

def purchase_success(request, pk):
    purchase = get_object_or_404(Purchase, pk=pk)
    return render(request, "listings/purchase_success.html", {"purchase": purchase})


from django.contrib.auth.decorators import login_required

from django.shortcuts import render, redirect
from .models import Property
from .forms import PropertyForm

# Create Property View
def create_property(request):
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES)
        if form.is_valid():
            # The model's save() method will automatically generate the luck_id.
            form.save()
            print("sucess")
            return redirect('lucky:property_list')  # redirect to all properties page
        else:
            # If the form is not valid, print errors to the console for debugging
            print(form.errors)
    else:
        form = PropertyForm()
    return render(request, 'listings/create_property.html', {'form': form})

from django.http import HttpResponse
def property_list(request):
    properties = Property.objects.all().order_by('-created_at')
    return render(request, 'listings/property_list.html', {'properties': properties})
    
    
def purchase_success(request, pk):
    purchase = get_object_or_404(Purchase, pk=pk)
    return render(request, "listings/purchase_success.html", {"purchase": purchase})


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Property, Buyer, Purchase
from .forms import PurchaseForm
import random, string
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Property, Buyer, Purchase
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Property, Buyer, Purchase

def buy_ticket(request, pk):
    property = get_object_or_404(Property, pk=pk)  # fetch by ID

    if request.method == "POST":
        full_name = request.POST.get("full_name")
        mobile = request.POST.get("mobile")
        whatsapp_no = request.POST.get("whatsapp_no")
        email = request.POST.get("email")
        area_city = request.POST.get("area_city")
        district = request.POST.get("district")
        state = request.POST.get("state")
        postal_code = request.POST.get("postal_code")
        transaction_id = request.POST.get("transaction_id")
        payment_screenshot = request.FILES.get("payment_screenshot")

        buyer, _ = Buyer.objects.get_or_create(
            mobile=mobile,
            defaults={
                "full_name": full_name,
                "whatsapp_no": whatsapp_no,
                "email": email,
                "area_city": area_city,
                "district": district,
                "state": state,
                "postal_code": postal_code,
            }
        )

        purchase = Purchase.objects.create(
            property=property,
            buyer=buyer,
            ticket_price=property.ticket_price,
            transaction_id=transaction_id,
            payment_screenshot=payment_screenshot,
            status="PENDING",
        )

        # Optional: reduce available tickets
        if hasattr(property, "total_tickets"):
            property.total_tickets = max(property.total_tickets - 1, 0)
            property.save()

        messages.success(
            request,
            f"✅ Thank you {buyer.full_name}! Your ticket ID ({purchase.ticket_code}) "
            f"has been submitted for verification."
        )
        return redirect("lucky:purchase_success", pk=purchase.pk)

    return render(request, "listings/buy_ticket.html", {"property": property})


from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Sum
from .models import Property, Purchase


def admin_dashboard(request):
    # Total number of properties
    total_properties = Property.objects.count()

    # Total tickets sold (sum of quantities from all purchases)
    total_tickets_sold = Purchase.objects.aggregate(total=Sum('quantity'))['total'] or 0

    # Total sales amount from VERIFIED purchases
    total_sales = Purchase.objects.filter(status='VERIFIED').aggregate(
        total=Sum('ticket_price')
    )['total'] or 0

    # Fetch all properties to show in table/list
    properties = Property.objects.all()

    context = {
        "total_properties": total_properties,
        "total_tickets_sold": total_tickets_sold,
        "total_sales": total_sales,
        "properties": properties,
    }
    return render(request, "listings/dashboard.html", context)


def admin_dashboard(request):
    total_properties = Property.objects.count()
    total_tickets_sold = Purchase.objects.count()  # ✅ count total purchases (tickets)
    total_sales = (
        Purchase.objects.filter(status='VERIFIED')
        .aggregate(total=Sum('ticket_price'))['total'] or 0
    )

    properties = Property.objects.all()
    purchases = Purchase.objects.select_related('property', 'buyer').order_by('-created_at')

    context = {
        "total_properties": total_properties,
        "total_tickets_sold": total_tickets_sold,
        "total_sales": total_sales,
        "properties": properties,
        "purchases": purchases,
    }
    return render(request, "listings/dashboard.html", context)




def verify_purchase(request, purchase_id):
    purchase = get_object_or_404(Purchase, id=purchase_id)
    purchase.status = 'VERIFIED'
    purchase.save()
    messages.success(request, f"{purchase.buyer.full_name}'s purchase has been verified ✅")
    return redirect('admin_dashboard')




from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login
from .models import AdminUser, ClientUser


# ✅ Admin Register
def admin_register(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        password = request.POST.get("password")
        confirm = request.POST.get("confirm")

        if password != confirm:
            messages.error(request, "Passwords do not match.")
        elif AdminUser.objects.filter(phone=phone).exists():
            messages.error(request, "Phone already registered.")
        else:
            admin = AdminUser.objects.create_user(
                phone=phone, email=email, name=name, password=password
            )
            messages.success(request, "Admin registered successfully! Please log in.")
            return redirect("admin_login")
    return render(request, "listings/admin_register.html")


# ✅ Admin Login
def admin_login(request):
    if request.method == "POST":
        phone = request.POST.get("phone")
        password = request.POST.get("password")
        user = authenticate(request, username=phone, password=password)
        if user is not None:
            print("sucess")
            login(request, user)
            return redirect("admin_dashboard")
        print("fail")
        messages.error(request, "Invalid phone or password.")
    return render(request, "listings/admin_login.html")

from django.contrib import messages
from django.shortcuts import redirect
from .models import ClientUser

def client_register(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        username = request.POST.get('username')
        password = request.POST.get('password')

        if ClientUser.objects.filter(email=email).exists():
            messages.error(request, "This email is already registered.")
            return redirect('client_register')

        if ClientUser.objects.filter(phone=phone).exists():
            messages.error(request, "This phone number is already registered.")
            return redirect('client_register')

        user = ClientUser.objects.create_user(phone=phone, email=email, username=username, password=password)
        return redirect('client_login')

    return render(request, 'listings/client_register.html')



from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages

def client_login(request):
    if request.user.is_authenticated:
        return redirect('client_dashboard')

    if request.method == 'POST':
        phone = request.POST.get('phone')
        password = request.POST.get('password')

        user = authenticate(request, phone=phone, password=password)

        if user is not None:
            login(request, user)
            return redirect('client_dashboard')
        else:
            messages.error(request, "Invalid phone or password.")
            return render(request, 'listings/client_login.html')

    return render(request, 'listings/client_login.html')




from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Property


def client_dashboard(request):
    user = request.user

    # Handle property posting
    if request.method == "POST":
        owner_name = request.POST.get("owner_name")
        property_value = request.POST.get("property_value")
        total_tickets = request.POST.get("total_tickets")
        ticket_price = request.POST.get("ticket_price")
        image = request.FILES.get("image")

        # Generate a unique luck_id (example)
        from django.utils.crypto import get_random_string
        luck_id = owner_name.lower().replace(" ", "")[:5] + get_random_string(4).upper()

        # Create the Property instance
        Property.objects.create(
            owner_name=owner_name,
            property_value=property_value,
            total_tickets=total_tickets,
            ticket_price=ticket_price,
            image=image,
            luck_id=luck_id,
            client=user  # This links the property to the logged-in user (ClientUser)
        )

        messages.success(request, "✅ Property posted successfully!")
        return redirect("client_dashboard")

    # Fetch all properties posted by the logged-in client
    properties = Property.objects.filter(client=user)
    total_tickets = sum([p.total_tickets for p in properties])
    sold_tickets = sum([p.tickets_sold for p in properties])

    context = {
        "properties": properties,
        "total_tickets": total_tickets,
        "sold_tickets": sold_tickets,
    }
    return render(request, "listings/client_dashboard.html", context)


from django.contrib.auth import logout
from django.shortcuts import redirect

def client_logout(request):
    logout(request)
    return redirect('client_login')  # redirect to login page after logout
