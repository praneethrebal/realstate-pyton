from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import FutureRequirementForm, ReelsForm, UserRegisterForm,CompanyRegisterForm,FranchiseForm,AddPropertyForm
from django.contrib.auth import login, authenticate
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import  get_object_or_404
from .models import Comment, LoanApplication, AddProject,AddPropertyModel, FranchiseApplication, Reels, Role,User
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse



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
            return redirect("login") 
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
            return redirect('home') # Redirect to a valid URL name like 'home'
        else:
            # If the form is not valid, print the errors to the console for debugging.
            # This will show which fields are failing validation.
            print(form.errors.as_json())
    else:
        form = AddPropertyForm()
    return render(request, 'add_property.html', {'form': form})



# dash bord 

def home(request):
    marketing_experts = User.objects.filter(role=Role.MARKETER)[:4]
    featured_companies = User.objects.filter(role=Role.COMPANY)[:4]
    professionals = User.objects.filter(role=Role.PROFESSIONAL)[:4]

    return render(request, "home.html", {
        "marketing_experts": marketing_experts,
        "featured_companies": featured_companies,
        "professionals": professionals,
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
    category = request.GET.get("category", "company")  # default

    if category == "marketer":
        users = User.objects.filter(role=Role.MARKETER)
    elif category == "professional":
        users = User.objects.filter(role=Role.PROFESSIONAL)
    else:
        users = User.objects.filter(role=Role.COMPANY)

    return render(request, "all_users.html", {
        "users": users,
        "category": category
    })

    
    
# franchise in home

def franchise(request):
    if request.method == "POST":
        full_name = request.POST.get("full_name")
        email = request.POST.get("email")
        contact = request.POST.get("contact")
        location = request.POST.get("location")
        experience = request.POST.get("experience")
        reason = request.POST.get("reason")

        FranchiseApplication.objects.create(
            full_name=full_name,
            email=email,
            contact=contact,
            location=location,
            experience=experience,
            reason=reason,
        )

        messages.success(request, "Application submitted successfully!")
        return render(request, "franchise.html", {"success": True})

    return render(request, "franchise.html")

# my requrement form
def requirement_form(request):
    if request.method == 'POST':
        form = FutureRequirementForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your requirement has been submitted successfully!')
            return redirect('require')  # URL name defined in urls.py
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

  
    location = request.GET.get("location")
    is_verified = request.GET.get("verified")
    min_price = request.GET.get("min_price")
    max_price = request.GET.get("max_price")
    road_facing = request.GET.get("road")
    look = request.GET.get("look")

   
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
            return redirect('profile')  # redirect back to profile page
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
            
            # Set fields that are not part of the form's main fields
            user.role = "COMPANY"
            user.phone = form.cleaned_data["contact_number"]
            
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

            # Now, save the user instance. This single call will:
            # 1. Save the user to the database.
            # 2. Save the logo and wallpaper files to their respective directories 
            #    ('company_logos/' and 'company_wallpapers/').
            user.save()

            messages.success(request, "Company registered successfully!")
            return redirect("login")
        else:
            # If the form is not valid, Django will automatically add error messages
            # to the form object, which will be displayed on the template.
            messages.error(request, "Please correct the errors below.")

    else:
        form = CompanyRegisterForm()

    return render(request, "company_register.html", {"form": form})


# franchise register**********************

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

            user.save()

            messages.success(request, "Franchise registered successfully! Please login.")
            return redirect("login")

        messages.error(request, "Please correct the errors below.")

    else:
        form = FranchiseForm()

    return render(request, "franchise_register.html", {"form": form})


# addproject-------

def add_project(request):
    if request.method == "POST":
        project_name = request.POST.get("project_name")
        type_of_project = request.POST.get("type_of_project")
        project_location = request.POST.get("project_location")  # FIXED
        location_url = request.POST.get("location_url")          # FIXED
        number_of_units = request.POST.get("number_of_units")    # FIXED
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

        # Files should come from request.FILES — not POST
        imgae = request.FILES.get("imgae")
        video = request.FILES.get("video")
        document = request.FILES.get("document")

        AddProject.objects.create(
            project_name=project_name,
            type_of_project=type_of_project,
            project_location=project_location,   # NOW VALID
            location_url=location_url,
            number_of_units=number_of_units,
            available_units=available_units,
            available_facing=available_facing,
            available_sizes=available_sizes,
            rera_approved=rera_approved,   # <-- must be here
            select_amenities=amenities,   # ← Now this variable is defined
            highlights=highlights,
            type_of_approval=type_of_approval,
            total_project_area=total_project_area,
            contact_info=contact_info,
            pricing=pricing,
            imgae=imgae,
            video=video,
            document=document,
        )

        messages.success(request, "Application submitted successfully")
        return redirect("home")

    return render(request, "add_project.html")


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

def get_reel(req):
    reels=Reels.objects.all()
    print(reels.values())
    return render(req,'reelViewer.html',{'data':reels})

def like_reel(req,id):
    reel=Reels.objects.get(id=id)
    reel.likeCount=reel.likeCount+1
    reel.save()
    return JsonResponse({"status": "success", "likes": reel.likeCount})
def comment_reel(req,id,comment):
    reel=Reels.objects.get(id=id)
    new_comment=Comment.objects.create(
        user=req.user,
        reel=reel,
        comment=comment
    )
    return JsonResponse({"status": "success", "comment": reel.commentCount})
    
