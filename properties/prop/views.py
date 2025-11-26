from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import FutureRequirementForm, UserRegisterForm,CompanyRegisterForm,FranchiseForm,AddPropertyForm
from django.contrib.auth import login, authenticate
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import  get_object_or_404
from .models import *
from django.contrib.auth.decorators import login_required




def register_user(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST, request.FILES)
        if form.is_valid():
            # Manually set plan_type based on role for correctness
            role = form.cleaned_data.get('role')
            
            # We modify the instance before it's saved
            user_instance = form.save(commit=False)
            if role == 'PROFESSIONAL':
                user_instance.plan_type = 'PROFESSIONAL_SINGLE'
            elif role == 'MARKETER':
                # Set subscription start and end dates for marketers
                start_date = timezone.now().date()
                user_instance.marketer_subscription_start_date = start_date
                user_instance.marketer_subscription_end_date = start_date + relativedelta(months=user_instance.selected_duration)
            user_instance.save() # Now save the instance with the correct plan_type
            form.save_m2m() # Important for saving related data, including files

            username = form.cleaned_data.get('username')
            messages.success(request, f"Account created for {username}! You can now log in.")
            return redirect("prop:login") 
    else:
        form = UserRegisterForm()
    return render(request, "register.html", {"form": form})

def login_user(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}.")
                return redirect("prop:home") # Redirect to a home/dashboard page
            else:
                messages.error(request,"Invalid username or password.")
        else:
            messages.error(request,"Invalid username or password.")
    form = AuthenticationForm()
    return render(request=request, template_name="login.html", context={"login_form": form})



#=================
# property adding
#=================




@login_required
def add_property(request):
    if request.method == "POST":
        form = AddPropertyForm(request.POST, request.FILES)
        if form.is_valid():
            # Pass the logged-in user to the form's custom save method.
            # The form now handles assigning the user and saving.
           
            form.save(user=request.user)
            return redirect('prop:home') # Redirect to a valid URL name like 'home'
        else:
            # If the form is not valid, print the errors to the console for debugging.
            # This will show which fields are failing validation.
            print(form.errors.as_json())
    else:
        form = AddPropertyForm()
    return render(request, 'add_property.html', {'form': form})



# dash bord 
# def home(request):
#     # Regular users (exclude Pro plan users)
#     marketing_experts = User.objects.filter(
#         role=Role.MARKETER, 
#     ).exclude(plan_type=PlanType.MARKETER_EXPORT_PRO)[:4]

#     featured_companies = User.objects.filter(
#         role=Role.COMPANY,
#     ).exclude(plan_type=PlanType.COMPANY_PRO)[:4]

#     professionals = User.objects.filter(role=Role.PROFESSIONAL)[:4]

#     # Pro users
#     marketing_experts_pro = User.objects.filter(plan_type=PlanType.MARKETER_EXPORT_PRO)[:4]
#     featured_companies_pro = User.objects.filter(plan_type=PlanType.COMPANY_PRO)[:4]

#     # Latest projects
#     projects = AddProject.objects.all().order_by('-id')[:4]

#     return render(request, "home.html", {
#         "marketing_experts": marketing_experts,
#         "featured_companies": featured_companies,
#         "professionals": professionals,
#         "marketing_experts_pro": marketing_experts_pro,
#         "featured_companies_pro": featured_companies_pro,
#         "projects": projects,
#     })

from django.shortcuts import render
from .models import AddProject, User, Role, PlanType

def home(request):
    # Regular users (exclude Pro plan users)
    marketing_experts = User.objects.filter(
        role=Role.MARKETER
    ).exclude(plan_type=PlanType.MARKETER_EXPORT_PRO)[:4]

    featured_companies = User.objects.filter(
        role=Role.COMPANY
    ).exclude(plan_type=PlanType.COMPANY_PRO)[:4]

    professionals = User.objects.filter(role=Role.PROFESSIONAL)[:4]

    # Pro users
    marketing_experts_pro = User.objects.filter(plan_type=PlanType.MARKETER_EXPORT_PRO)[:4]
    featured_companies_pro = User.objects.filter(plan_type=PlanType.COMPANY_PRO)[:4]

    # ⭐ FIXED: Filter based on project.plan_type (NOT type_of_project)
    normal_projects = AddProject.objects.filter(
        plan_type=PlanType.COMPANY_NORMAL
    ).order_by('-id')[:4]

    pro_projects = AddProject.objects.filter(
        plan_type=PlanType.COMPANY_PRO
    ).order_by('-id')[:4]

    return render(request, "home.html", {
        "marketing_experts": marketing_experts,
        "featured_companies": featured_companies,
        "professionals": professionals,
        "marketing_experts_pro": marketing_experts_pro,
        "featured_companies_pro": featured_companies_pro,
        "normal_projects": normal_projects,
        "pro_projects": pro_projects,
    })


# from django.shortcuts import render
# from .models import AddProject

# def all_projects(request):
#     projects = AddProject.objects.all()  # base queryset


#     # Get filter values from GET
#     project_name = request.GET.get("name", "")
#     location = request.GET.get("location", "")

#     # Apply filters
#     if project_name:
#         projects = projects.filter(project_name__icontains=project_name)
#     if location:
#         projects = projects.filter(project_location__icontains=location)

#     # Pass to template
#     context = {
#         "projects": projects,
#         "name": project_name,
#         "location": location,
#     }

#     return render(request, "all_projects.html", context)


def all_projects(request):
    category = request.GET.get("category")
    name = request.GET.get("name", "")
    location = request.GET.get("location", "")

    qs = AddProject.objects.all()

    # Name filter
    if name:
        qs = qs.filter(project_name__icontains=name)

    # Location filter
    if location:
        qs = qs.filter(project_location__icontains=location)

    # Category filter based on project plan type (FIXED)
    if category == "pro":
        qs = qs.filter(plan_type=PlanType.COMPANY_PRO)
    elif category == "normal":
        qs = qs.filter(plan_type=PlanType.COMPANY_NORMAL)

    return render(request, "all_projects.html", {
        "projects": qs,
        "category": category,
        "name": name,
        "location": location,
    })


#property listings 
# def property_filter(request):
#     properties = Property.objects.all()
#     categories = [c[0] for c in Property.CATEGORY_CHOICES]

#     selected_category = request.GET.get("category")
#     prop_id = request.GET.get("id")
#     location = request.GET.get("location")
#     min_price = request.GET.get("min")
#     max_price = request.GET.get("max")
#     type_filter = request.GET.get("type")

#     if selected_category:
#         properties = properties.filter(category=selected_category)
#     if prop_id:
#         properties = properties.filter(id=prop_id)
#     if location:
#         properties = properties.filter(location__icontains=location)
#     if min_price:
#         properties = properties.filter(price__gte=min_price)
#     if max_price:
#         properties = properties.filter(price__lte=max_price)
#     if type_filter in ("Sale", "Rent"):
#         properties = properties.filter(type=type_filter)

#     return render(request, "filter.html", {
#         "properties": properties,
#         "categories": categories,
#         "selected_category": selected_category,
#     })


#user Profile



def user_detail(request, user_id):
    user = get_object_or_404(User, id=user_id)

    qs = AddPropertyModel.objects.filter(user=user)

    total_count = qs.count()
    sold_count = qs.filter(is_notSold=True).count()
    pending_count = qs.filter(is_notSold=False).count()

    return render(request, "user_detail.html", {
        "u": user,
        "sold": sold_count,
        "pending": pending_count,
        "total": total_count,
    })


def all_users(request):
    category = request.GET.get("category", "company")  # default category

    # Prepare empty lists
    marketer_export = marketer_export_pro = company_normal = company_pro = professional_users = None

    # Base query based on role + plan type
    if category in ["marketer", "marketer_pro"]:
        # Separate plan types
        marketer_export_pro = User.objects.filter(role=Role.MARKETER, plan_type=PlanType.MARKETER_EXPORT_PRO)
        marketer_export = User.objects.filter(role=Role.MARKETER, plan_type=PlanType.MARKETER_EXPORT)
    elif category in ["company", "company_pro"]:
        company_pro = User.objects.filter(role=Role.COMPANY, plan_type=PlanType.COMPANY_PRO)
        company_normal = User.objects.filter(role=Role.COMPANY).exclude(plan_type=PlanType.COMPANY_PRO)
    elif category == "professional":
        professional_users = User.objects.filter(role=Role.PROFESSIONAL)

    # ------------------- Filters -------------------
    name = request.GET.get("name", "")
    user_category = request.GET.get("user_category", "")
    experience = request.GET.get("experience", "")

    def apply_filters(queryset):
        if name:
            queryset = queryset.filter(username__icontains=name)
        if user_category:
            queryset = queryset.filter(category__icontains=user_category)
        if experience:
            queryset = queryset.filter(experience__icontains=experience)
        return queryset

    marketer_export = apply_filters(marketer_export) if marketer_export else None
    marketer_export_pro = apply_filters(marketer_export_pro) if marketer_export_pro else None
    company_normal = apply_filters(company_normal) if company_normal else None
    company_pro = apply_filters(company_pro) if company_pro else None
    professional_users = apply_filters(professional_users) if professional_users else None

    # ------------------- Render -------------------
    return render(request, "all_users.html", {
        "category": category,
        "filters": {
            "name": name,
            "user_category": user_category,
            "experience": experience,
        },
        "marketer_export": marketer_export,
        "marketer_export_pro": marketer_export_pro,
        "company_normal": company_normal,
        "company_pro": company_pro,
        "professional_users": professional_users,
    })

    
# franchise in home

from .forms import FranchiseApplicationForm

def franchise(request):
    if request.method == "POST":
        form = FranchiseApplicationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Form submitted successfully!")
            return render(request, "franchise.html", {"form": FranchiseApplicationForm(), "success": True})
    else:
        form = FranchiseApplicationForm()

    return render(request, "franchise.html", {"form": form})



# my requrement form
def requirement_form(request):
    if request.method == 'POST':
        form = FutureRequirementForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your requirement has been submitted successfully!')
            return redirect('prop:require')  # URL name defined in urls.py
        else:
            print("Form errors:", form.errors)  # Debugging help in terminal
    else:
        form = FutureRequirementForm()
    return render(request, 'require.html', {'form': form})



# def profile(req):
#     data=req.user
#     print(data)
#     return HttpResponse(data)


@login_required
def profile(req):
    data = req.user
    count = AddPropertyModel.objects.filter(user=data).count()

    return render(req, 'profile.html', {
        "data": data,
        "upload_count": count
    })

# @login_required
# def profile(req):
#     data = req.user
#     count = AddPropertyModel.objects.filter(user=data).count()

#     return render(req, 'profile.html', {
#         "data": data,
#         "upload_count": count
#     })



# propertry list

from django.http import HttpResponse
# @login_required
# def property_list(request):
#     properties = AddPropertyModel.objects.filter(user=request.user)
#     return render(request, 'property_list.html', {"properties": properties})
def get_Property(req,prop):
    a=AddPropertyModel.objects.filter(selectProperty=prop)
    print(a)
    
    return HttpResponse(a)
    
    


@login_required
def property_list(request, prop):
   
    properties = AddPropertyModel.objects.filter(selectProperty=prop, is_notSold=False)

    name=request.GET.get("name")
    location = request.GET.get("location")
    is_verified = request.GET.get("verified")
    min_price = request.GET.get("min_price")
    max_price = request.GET.get("max_price")
    road_facing = request.GET.get("road")
    look = request.GET.get("look")

    if name:
       properties=properties.filter(projectName__icontains=name)
    if location:
        properties = properties.filter(location__icontains=location)
    if is_verified in ['1', '0']:
        properties = properties.filter(is_verified=(is_verified == '1'))
    if min_price:
        properties = properties.filter(price__gte=min_price)
    if max_price:
        properties = properties.filter(price__lte=max_price)
    if road_facing:
        properties = properties.filter(facing=road_facing) 
    if look in ['Sell', 'Rent']:
        properties = properties.filter(look=look)

    return render(request, "property_list.html", {"data": properties})


def property_detail(request, id):
    data = AddPropertyModel.objects.get(id=id)
    return render(request, "property_detail.html", {"item": data})




# edit----------


from .forms import UserProfileForm


def edit_profile(request):
    user = request.user  # currently logged-in user
    if request.method == "POST":
        form = UserProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()  # <-- updates the database
            return redirect('prop:profile')  # redirect back to profile page
    form = UserProfileForm(instance=user)
    return render(request, 'edit_profile.html', {'form': form})

def user_uploades(req):
    p= req.user
    D = AddPropertyModel.objects.filter(user = p)
    

    # D= User.objects.filter(AddPropertyModel = upload)

    return render(req, "user_uploades.html",{"D":D})


def referral(req):
    a = req.user
    m = a.user_referral_code   # your referral code

    print("Referral Code:", m)

    s = User.objects.filter(referred_by_code=m)   # your queryset

    return render(req, "referral.html", {"s": s})



# move form************
from .forms import MoveRequestForm
@login_required


def move_form(request):
    if request.method == "POST":
        form = MoveRequestForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, "move_form.html", {
                "form": MoveRequestForm(),
                "success": True
            })
    else:
        form = MoveRequestForm()

    return render(request, "move_form.html", {"form": form})


from django.shortcuts import render
from .models import ContactForm
@login_required
def contact_form_view(request):
    success = False
    if request.method == "POST":
        customer_name = request.POST.get("customer_name")
        number = request.POST.get("number")
        alternate_number = request.POST.get("alternate_number")
        renovation_type = request.POST.get("renovation_type")
        location = request.POST.get("location")
        additional_info = request.POST.get("additional_info")

        ContactForm.objects.create(
            customer_name=customer_name,
            number=number,
            alternate_number=alternate_number,
            renovation_type=renovation_type,
            location=location,
            additional_info=additional_info,
        )
        success = True

    return render(request, "contact_form.html", {"success": success})

    # loan form*************
@login_required

def loan_form(request):
    if request.method == 'POST':
        data = LoanApplication(
            full_name=request.POST.get('full_name'),
            email=request.POST.get('email'),
            phone=request.POST.get('phone'),
            dob=request.POST.get('dob'),
            street_address=request.POST.get('street_address'),
            unit=request.POST.get('unit'),
            city=request.POST.get('city'),
            state=request.POST.get('state'),
            zip_code=request.POST.get('zip_code'),
            loan_amount=request.POST.get('loan_amount'),
            loan_purpose=request.POST.get('loan_purpose'),
            application_date=request.POST.get('application_date'),
            employment_status=request.POST.get('employment_status'),
            realtor=request.POST.get('realtor'),
            credit_score=request.POST.get('credit_score'),
            agree=('agree' in request.POST)
        )
        data.save()
        messages.success(request, "✅ Loan Application submitted successfully!")
        return redirect('loan_form')
    return render(request, 'loan_form.html')


# company register********************
def company_register(request):

    if request.method == "POST":
        form = CompanyRegisterForm(request.POST, request.FILES)

        if form.is_valid():
            user = form.save(commit=False)
            user.role = Role.COMPANY
            # Set fields that are not part of the form's main fields
            user.company_subscription_type = form.cleaned_data["plan"]
            

            # Handle subscription dates
            duration = form.cleaned_data["duration"]
            plan = form.cleaned_data["plan"]
            start_date = timezone.now().date()
            end_date = start_date + relativedelta(months=duration)
            user.company_subscription_type = plan
            user.selected_duration = duration
            user.company_subscription_start_date = start_date
            user.company_subscription_end_date = end_date

            # Manually assign the uploaded files from the form's cleaned_data
            # to the correct model fields before saving.
            user.company_logo_path = form.cleaned_data.get('logo')
            user.company_wallpaper_path = form.cleaned_data.get('wallpaper')
            if plan == "NORMAL":
                user.plan_type = PlanType.COMPANY_NORMAL
            else:
                user.plan_type = PlanType.COMPANY_PRO


            # Now, save the user instance. This single call will:
            # 1. Save the user to the database.
            # 2. Save the logo and wallpaper files to their respective directories 
            #    ('company_logos/' and 'company_wallpapers/').
            user.save()

            messages.success(request, "Company registered successfully!")
            return redirect("prop:login")
        else:
            # If the form is not valid, Django will automatically add error messages
            # to the form object, which will be displayed on the template.
            messages.error(request, "Please correct the errors below.")

    else:
        form = CompanyRegisterForm()

    return render(request, "company_register.html", {"form": form})

from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from django.core.files.storage import default_storage
from .models import User,ContactMessage
from .forms import CompanyRegisterForm


@login_required
def company_profile_view(request, user_id=None):

    if user_id:  # Visitor
        profile_user = User.objects.get(id=user_id)
    else:        # Owner
        profile_user = request.user

    if request.method == "POST" and request.user == profile_user:
        profile_user.company_name = request.POST.get("company_name")
        profile_user.email = request.POST.get("email")
        profile_user.address = request.POST.get("address")
        profile_user.contact_number = request.POST.get("contact_number")
        profile_user.experience = request.POST.get("experience")
        profile_user.total_projects = request.POST.get("total_projects")
        profile_user.ongoing_projects = request.POST.get("ongoing_projects")
        profile_user.completed_projects = request.POST.get("completed_projects")

        if request.FILES.get("company_logo_path"):
            logo_file = request.FILES["company_logo_path"]
            logo_path = default_storage.save(f"company_logo/{logo_file.name}", logo_file)
            profile_user.company_logo_path = logo_path

        if request.FILES.get("company_wallpaper_path"):
            wall_file = request.FILES["company_wallpaper_path"]
            wallpaper_path = default_storage.save(f"company_wallpaper/{wall_file.name}", wall_file)
            profile_user.company_wallpaper_path = wallpaper_path

        profile_user.save()
        messages.success(request, "Profile Updated Successfully!")
        return redirect("prop:company_profile")

    # Increase views only for visitors
    if request.user != profile_user:
        profile_user.click = profile_user.click + 1 if profile_user.click else 1
        profile_user.save()

    is_owner = (request.user == profile_user)

    contact_count = ContactMessage.objects.filter(cid=str(profile_user.id)).count()
    projects = AddPropertyModel.objects.filter(user=profile_user)

    return render(request, "company_profile.html", {
        "profile_user": profile_user,
        "contact_count": contact_count,
        "projects": projects,
        "is_owner": is_owner,
    })


@login_required
def delete_project(request, id):
    project = AddPropertyModel.objects.get(id=id, user=request.user)
    project.delete()
    messages.success(request, "Project deleted successfully!")
    return redirect("prop:company_profile")

@login_required
def mark_sold(request, id):
    project = AddPropertyModel.objects.get(id=id, user=request.user)
    project.status = "Sold"
    project.save()
    messages.success(request, "Project marked as sold!")
    return redirect("prop:company_profile")

@login_required
def delete_reel(request, id):
    reel = reel.objects.get(id=id, user=request.user)
    reel.delete()
    messages.success(request, "Reel deleted successfully!")
    return redirect("prop:company_profile")

 
# Contact Form Submit
def contact_submit(request):
    if request.method == "POST":
        ContactMessage.objects.create(
            user=request.user if request.user.is_authenticated else None,
            name=request.POST.get("contact_name"),
            email=request.POST.get("email"),
            requirement=request.POST.get("requirement"),
            message=request.POST.get("message"),
            cid=request.POST.get("contact_id"),
        )
        messages.success(request, "Message Sent Successfully!")
        return redirect(request.META.get("HTTP_REFERER", "company_profile"))

    return redirect(request.META.get("HTTP_REFERER", "company_profile"))


# franchise register**********************
from django.db import IntegrityError
from django.contrib import messages

def franchise_register(request):
    if request.method == "POST":
        form = FranchiseForm(request.POST, request.FILES)

        if form.is_valid():
            user = form.save(commit=False)

            user.phone = form.cleaned_data["contact_number"]
            user.location = form.cleaned_data["location"]
            user.experience = form.cleaned_data["experience"]
            user.role = "FRANCHISE"

            if form.cleaned_data.get("profile_image"):
                user.profile_image_path = form.cleaned_data["profile_image"]

            try:
                user.save()  # <-- Catch error here

                messages.success(request, "Franchise registered successfully! Please login.")
                return redirect("prop:login")

            except IntegrityError:
                # Add error on the phone field
                form.add_error("contact_number", "This phone number is already registered.")
                messages.error(request, "Please correct the errors below.")

        else:
            messages.error(request, "Please correct the errors below.")

    else:
        form = FranchiseForm()

    return render(request, "franchise_register.html", {"form": form})

# =============================
# FRANCHISE PROFILE & EDIT
# =============================
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import FranchiseProperty
@login_required
def franchise_profile(request):
    if request.user.role != "FRANCHISE":
        return redirect("prop:home")

    user_location = request.user.location

    assigned_properties = AddPropertyModel.objects.filter(
        location=user_location,
        is_verified=False
    )

    verified_properties = AddPropertyModel.objects.filter(
        location=user_location,
        is_verified=True
    )

    return render(request, "franchise_profile.html", {
        "profile": request.user,

        "assigned": assigned_properties.count(),
        "pending": assigned_properties.count(),
        "verified": verified_properties.count(),

        "properties": assigned_properties,
        "verified_properties": verified_properties,
        "not_verified_properties": assigned_properties,
    })



@login_required
def franchise_edit(request):
    user = request.user

    if request.method == "POST":
        errors = {}
        form_data = request.POST.copy()

        email = request.POST.get("email", "").strip()
        contact_number = request.POST.get("contact_number", "").strip()
        location = request.POST.get("location", "").strip()
        radius = request.POST.get("radius", "").strip()
        experience = request.POST.get("experience", "").strip()
        description = request.POST.get("description", "").strip()

        # ===== REQUIRED VALIDATION =====
        if not email:
            errors["email"] = "Email is required."
        if not contact_number:
            errors["contact_number"] = "Contact number is required."
        if not location:
            errors["location"] = "Location is required."
        if not radius:
            errors["radius"] = "Radius is required."
        if not experience:
            errors["experience"] = "Experience is required."
        if not description:
            errors["description"] = "Description is required."

        # If ANY errors ➝ return modal with errors
        if errors:
            return render(request, "franchise_profile.html", {
                "profile": user,
                "errors": errors,
                "form_data": form_data,
                "assigned": user.total_projects,
                "pending": user.ongoing_projects,
                "verified": user.completed_projects,
                "show_modal": True,   
            })

        # ===== SAVE VALID DATA =====
        user.email = email
        user.contact_number = contact_number
        user.location = location
        user.radius = int(radius)
        user.experience = int(experience)
        user.description = description

        if request.FILES.get("profile_image"):
            user.profile_image_path = request.FILES["profile_image"]

        user.save()

        return redirect("prop:franchise_profile")

    return redirect("prop:franchise_profile")

@login_required
def verify_property(request):
    if request.method == "POST":

        property_id = request.POST.get("property_id")
        reviews = request.POST.get("reviews")
        amount = request.POST.get("amount")
        verified_location = request.POST.get("verified_location")
        video_file = request.FILES.get("video_file")

        try:
            prop = AddPropertyModel.objects.get(id=property_id)
        except AddPropertyModel.DoesNotExist:
            return redirect("prop:franchise_profile")

        # Create record in FranchiseProperty table
        FranchiseProperty.objects.create(
            property=prop,
            property_id_number=prop.id,      # <-- here we store ID
            franchise=request.user,
            reviews=reviews,
            amount=amount,
            verified_location=verified_location,
            video_file=video_file,
        )

        # Mark property verified
        prop.is_verified = True
        prop.save()

        return redirect("prop:franchise_profile")






# addproject-------
def add_project(request):
    # Only company users can add projects
    if not request.user.is_authenticated or request.user.role != "COMPANY":
        messages.error(request, "Only company users can add projects.")
        return redirect("prop:home")

    if request.method == "POST":
        project_name = request.POST.get("project_name")
        type_of_project = request.POST.get("type_of_project")
        project_location = request.POST.get("project_location")
        location_url = request.POST.get("location_url")
        number_of_units = request.POST.get("number_of_units")
        available_units = request.POST.get("available_units")
        available_facing = request.POST.get("available_facing")
        available_sizes = request.POST.get("available_sizes")

        rera_approved_value = request.POST.get("rera_approved")

        if rera_approved_value == "True":
            rera_approved = True
        elif rera_approved_value == "False":
            rera_approved = False
        else:
            rera_approved = None

        amenities_list = request.POST.getlist("select_amenities")
        amenities = ",".join(amenities_list)

        highlights = request.POST.get("highlights")
        type_of_approval = request.POST.get("type_of_approval")
        total_project_area = request.POST.get("total_project_area")
        contact_info = request.POST.get("contact_info")
        pricing = request.POST.get("pricing")

        image = request.FILES.get("image")
        video = request.FILES.get("video")
        document = request.FILES.get("document")

        # ⭐ IMPORTANT: store company user + plan type ⭐
        AddProject.objects.create(
            user=request.user,
            plan_type=request.user.plan_type,  # COMPANY_NORMAL or COMPANY_PRO

            project_name=project_name,
            type_of_project=type_of_project,
            project_location=project_location,
            location_url=location_url,
            number_of_units=number_of_units,
            available_units=available_units,
            available_facing=available_facing,
            available_sizes=available_sizes,
            rera_approved=rera_approved,
            select_amenities=amenities,
            highlights=highlights,
            type_of_approval=type_of_approval,
            total_project_area=total_project_area,
            contact_info=contact_info,
            pricing=pricing,
            image=image,
            video=video,
            document=document,
        )

        messages.success(request, "Project added successfully")
        return redirect("prop:home")

    return render(request, "add_project.html")

def project_detail(request, id):
    project = AddProject.objects.get(id=id)

    images = []

    # main image
    if project.image:
        images.append(project.image.url)

    # extra images
    extra = project.extra_images.all()
    for img in extra:
        images.append(img.image.url)

    return render(request, "project_detail.html", {"project": project, "images": images})




from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import AddPropertyModel, SavedProperty


@login_required
def saved_properties(request):
    saved_list = SavedProperty.objects.filter(user=request.user)
    return render(request, "saved_properties.html", {"saved_list": saved_list})


def save_property(request, property_id):
    property_obj = AddPropertyModel.objects.get(id=property_id)

    saved, created = SavedProperty.objects.get_or_create(
        user=request.user,
        property=property_obj
    )

    if not created:
        saved.delete()
        return JsonResponse({"status": "removed"})

    return JsonResponse({"status": "saved"})



#otp
import time
import random
import urllib.parse
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

API_KEY = "bGxMnkR7nUa3DpPDGdqhUg"
SENDER_ID = "WDPROP"
TEMPLATE_ID = "1007692442675920680"
PE_ID = "1001053976927196733"
SMS_URL = "https://cloud.smsindiahub.in/api/mt/SendSMS"

otp_storage = {}  # temporary

@csrf_exempt
def send_otp(request):
    phone = request.GET.get("phone")

    if not phone:
        return JsonResponse({"error": "Phone number required"}, status=400)

    otp = "%06d" % random.randint(0, 999999)
    otp_storage[phone] = {"otp": otp, "timestamp": time.time()}

    # MUST MATCH EXACT DLT TEMPLATE
    message = (
        f"Your OTP for verification with Weekdays Properties is {otp}. "
        "Please do not share this code with anyone. It is valid for 10 minutes."
    )

    params = {
        "APIKey": API_KEY,
        "senderid": SENDER_ID,
        "channel": "Trans",
        "DCS": 0,
        "flashsms": 0,
        "number": "91" + phone,
        "text": message,   # RAW MESSAGE (NO URL ENCODE)
        "DLTTemplateId": TEMPLATE_ID,
        "route": "0",
        "PEId": PE_ID
    }

    response = requests.get(SMS_URL, params=params)

    print("SMSIndiaHub Response:", response.text)

    return JsonResponse({
        "status": response.status_code,
        "response": response.text,
        "otp": otp
    })


@csrf_exempt
def verify_otp(request):
    phone = request.GET.get("phone")
    otp = request.GET.get("otp")

    if not phone or not otp:
        return JsonResponse({"error": "Phone and OTP required"}, status=400)

    data = otp_storage.get(phone)

    if not data:
        return JsonResponse({"error": "OTP expired or not sent"}, status=400)

    if time.time() - data["timestamp"] > 600:
        otp_storage.pop(phone)
        return JsonResponse({"error": "OTP expired"}, status=400)

    if otp != data["otp"]:
        return JsonResponse({"error": "Invalid OTP"}, status=400)

    otp_storage.pop(phone)
    return JsonResponse({"message": "OTP Verified"})



from .forms import ReelsForm

def reels_upload(req):
    user=req.user
    f=ReelsForm()
    if req.method=="POST":
        f=ReelsForm(req.POST,req.FILES)
        if f.is_valid():
            reel=f.save(commit=False)
            reel.user=user
            reel.save()
            return redirect("prop:home")
    return render(req,"reels_upload.html",{"f":f})

import random 
def get_reel(req):
    # reels=Reels.objects.all()
    reels = list(Reels.objects.all())  # fetch all reels
    random.shuffle(reels)   
    
    
    return render(req,'reelViewer.html',{'data':reels})

def like_reel(req, id):
    reel = Reels.objects.get(id=id)

    # Get liked reels list from session
    liked_reels = req.session.get("liked_reels", [])

    if id in liked_reels:
        # UNLIKE
        reel.likeCount -= 1
        liked_reels.remove(id)
        liked = False
    else:
        # LIKE
        reel.likeCount += 1
        liked_reels.append(id)
        liked = True

    # Save back to session
    req.session["liked_reels"] = liked_reels

    reel.save()

    return JsonResponse({
        "status": "success",
        "liked": liked,
        "likes": reel.likeCount
    })


def comment_reel(req,id,comment):
    reel=Reels.objects.get(id=id)
    new_comment=Comment.objects.create(
        user=req.user,
        reel=reel,
        comment=comment
    )
    return JsonResponse({"status": "success", "comment": reel.commentCount})

def getAllComments(request, id):
    try:
        reel = Reels.objects.get(id=id)
        # Select only the fields needed and convert to list
        comments = Comment.objects.filter(reel=reel).values(
            'id', 'comment', 'user__username', 'created_at'
        )
        comments_list = list(comments)  # ✅ Convert QuerySet to list
        return JsonResponse({"status": "success", "comments": comments_list}, safe=False)
    except Reels.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Reel not found"}, status=404)




# views.py
from django.shortcuts import render, get_object_or_404
from .models import Reels

def reel_viewer(request):
    u=request.user
    reels=Reels.objects.filter(user=u)
    return render(request,'all_reels.html',{'reel':reels})



from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from .models import Reels

def delete_reel(request, pk):
    if request.method == "POST":
        reel = get_object_or_404(Reels, id=pk)
        reel.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)


from django.urls import reverse
from urllib.parse import urlencode

def search(req):
    # If it's a GET request → show the search box page
    if req.method == "GET":
        return render(req, "search_box.html")

    # If it's POST → process search
    cat = req.POST.get('search-cat') or "All"
    btn = (req.POST.get('search-input') or "").strip()

    query = {}
    if btn:
        query['name'] = btn

    prop = cat if cat else "All"

    url = reverse('prop:property_list', args=[prop])
    if query:
        url = f"{url}?{urlencode(query)}"

    return redirect(url)


