from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import random
import re

# ===== Enum Classes =====

class Role(models.TextChoices):
    OWNER = 'OWNER', 'Owner'
    MARKETER = 'MARKETER', 'Marketer'
    PROFESSIONAL = 'PROFESSIONAL', 'Professional'
    COMPANY = 'COMPANY', 'Company'
    FRANCHISE = 'FRANCHISE', 'Franchise'


class PlanType(models.TextChoices):
    MARKETER_EXPORT = 'MARKETER_EXPORT', 'Marketer Export'
    MARKETER_EXPORT_PRO = 'MARKETER_EXPORT_PRO', 'Marketer Export Pro'
    PROFESSIONAL_SINGLE = 'PROFESSIONAL_SINGLE', 'Professional Single'
    COMPANY_NORMAL = 'COMPANY_NORMAL', 'Company Normal'
    COMPANY_PRO = 'COMPANY_PRO', 'Company Pro'


class CompanySubscriptionType(models.TextChoices):
    NORMAL = 'NORMAL', 'Normal'
    PRO = 'PRO', 'Pro'


class MarketingSubscriptionType(models.TextChoices):
    EXPORT = 'EXPORT', 'Export'
    EXPORT_PRO = 'EXPORT_PRO', 'Export Pro'


# ===== User Model =====

class User(AbstractUser):
    # Unique fields
    phone = models.CharField(max_length=15, unique=True, null=True, blank=True)
    email = models.EmailField(unique=True)

    # Core profile fields
    category = models.CharField(max_length=100, null=True, blank=True)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.PROFESSIONAL)
    plan_type = models.CharField(max_length=30, choices=PlanType.choices, null=True, blank=True)

    # Optional details
    description = models.TextField(null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    experience = models.IntegerField(null=True, blank=True)
    user_referral_code = models.CharField(max_length=50, null=True, blank=True, unique=True, help_text="This user's own unique referral code.")
    referred_by_code = models.CharField(max_length=50, null=True, blank=True, help_text="The referral code used by the user during registration.")
    deals = models.CharField(max_length=255, null=True, blank=True)

    radius = models.IntegerField(null=True, blank=True, default=5)

    # ===== Image fields =====
    # profile_image_name = models.CharField(max_length=255, null=True, blank=True)
    profile_image_path = models.ImageField(upload_to='profile_images/', default='images/Default_profile_picture.jpeg', null=True, blank=True)
    # profile_image_type = models.CharField(max_length=50, null=True, blank=True)

    # company_logo_name = models.CharField(max_length=255, null=True, blank=True)
    company_logo_path = models.ImageField(upload_to='company_logos/', null=True, blank=True)
    company_wallpaper_path = models.ImageField(upload_to='company_wallpapers/', null=True, blank=True)
  

    # ===== Company Details =====
    company_name = models.CharField(max_length=255, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    logo_url = models.CharField(max_length=255, null=True, blank=True)

    # ===== Metrics =====
    click = models.BigIntegerField(default=0)
    leads = models.BigIntegerField(default=0)

    total_projects = models.IntegerField(null=True, blank=True)
    ongoing_projects = models.IntegerField(null=True, blank=True)
    completed_projects = models.IntegerField(null=True, blank=True)

    # ===== Contact Info =====
    contact_number = models.CharField(max_length=15, null=True, blank=True)
    selected_duration = models.IntegerField(default=1)

    # ===== Dates =====
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    company_subscription_start_date = models.DateField(null=True, blank=True)
    company_subscription_end_date = models.DateField(null=True, blank=True)
    marketer_subscription_start_date = models.DateField(null=True, blank=True)
    marketer_subscription_end_date = models.DateField(null=True, blank=True)
    professionals_subscription_start_date = models.DateField(null=True, blank=True)
    professionals_subscription_end_date = models.DateField(null=True, blank=True)

    # ===== Subscription Types =====
    company_subscription_type = models.CharField(
        max_length=50,
        choices=CompanySubscriptionType.choices,
        null=True,
        blank=True
    )
    marketing_subscription_type = models.CharField(
        max_length=50,
        choices=MarketingSubscriptionType.choices,
        null=True,
        blank=True
    )
    professionals_subscription_type = models.CharField(
        max_length=50,
        choices=MarketingSubscriptionType.choices,
        null=True,
        blank=True
    )

    # ===== Utility =====
    def __str__(self):
        return self.username or "Unnamed User"

    @property
    def plan_price(self):
        prices = {
            'MARKETER_EXPORT': 7999,
            'MARKETER_EXPORT_PRO': 14999,
            'PROFESSIONAL_SINGLE': 4999,
            'COMPANY_NORMAL': 14999,
            'COMPANY_PRO': 19999,
        }
        return prices.get(self.plan_type, 0)

    # ===== Referral Code Generation =====
    def _generate_referral_code(self):
        """Generates a unique referral code based on ID and role."""
        id_part = str(self.id)
        role_part = (self.role[:2].upper() if self.role else "XX")
        name_clean = re.sub(r'[^A-Za-z0-9]', '', self.username or '')
        name_part = name_clean[:3].upper() if name_clean else "USR"
        random_part = str(random.randint(1000, 9999))
        return f"{role_part}{id_part}{name_part}{random_part}"

    def save(self, *args, **kwargs):
        # Save the user instance first, especially to get an ID for new users.
        super().save(*args, **kwargs)
        # If it's a new user and they don't have a referral code yet, generate one.
        if not self.user_referral_code and self.pk:
            self.user_referral_code = self._generate_referral_code()
            # Update only the referral code field to avoid recursion
            User.objects.filter(pk=self.pk).update(user_referral_code=self.user_referral_code)

class AddPropertyModel(models.Model):
    LOOKING_CHOICES = [
        ('Sell', 'Sell'),
        ('Rent', 'Rent'),
    ]

    PROPERTY_CHOICES = [
        ('Plot', 'Plot'),
        ('House', 'House'),
        ('Flat', 'Flat'),
        ('Villa', 'Villa'),
        ('Farm', 'Farm'),
        ('Lands', 'Lands'),
        ('Developmentlands', 'Developmentlands'),
        ('Disputelands', 'Disputelands'),
        ('Commerciallands', 'Commerciallands'),
    ]

    projectName = models.CharField(max_length=255, null=True, blank=True)
    extent = models.FloatField(null=True, blank=True)
    facing = models.CharField(max_length=100, null=True, blank=True)
    roadSize = models.CharField(max_length=100, null=True, blank=True)
    units = models.CharField(max_length=50, null=True, blank=True)
    dimensions = models.CharField(max_length=255, null=True, blank=True)
    numberOfFloors = models.IntegerField(null=True, blank=True)
    numberOfBHK = models.IntegerField(null=True, blank=True)
    builtUpArea = models.FloatField(null=True, blank=True)
    openArea = models.FloatField(null=True, blank=True)
    rentalIncome = models.FloatField(null=True, blank=True)
    floorNo = models.IntegerField(null=True, blank=True)
    communityType = models.CharField(max_length=255, null=True, blank=True)
    carpetArea = models.FloatField(null=True, blank=True)
    landType = models.CharField(max_length=255, null=True, blank=True)
    soilType = models.CharField(max_length=255, null=True, blank=True)
    roadFacing = models.BooleanField(default=False)
    waterSource = models.CharField(max_length=255, null=True, blank=True)
    unitType = models.CharField(max_length=255, null=True, blank=True)
    zone = models.CharField(max_length=255, null=True, blank=True)
    developmentType = models.CharField(max_length=255, null=True, blank=True)
    expectedAdvance = models.FloatField(null=True, blank=True)
    ratio = models.CharField(max_length=255, null=True, blank=True)
    disputeDetails = models.TextField(null=True, blank=True)
    lookingToSell = models.BooleanField(default=False)
    problemDetails = models.TextField(null=True, blank=True)
    actualPrice = models.FloatField(null=True, blank=True)
    salePrice = models.FloatField(null=True, blank=True)
    price = models.FloatField(default=0)
    status = models.CharField(max_length=20, default="Available")

    look = models.CharField(max_length=20, choices=LOOKING_CHOICES, null=True, blank=True)
    selectProperty = models.CharField(max_length=50, choices=PROPERTY_CHOICES, null=True, blank=True)

    reraApproved = models.BooleanField(default=False)
    approvalType = models.CharField(max_length=255, null=True, blank=True)
    amenities = models.JSONField(default=list, blank=True)
    highlights = models.TextField(null=True, blank=True)

    propertyId = models.BigIntegerField(null=True, blank=True)
    is_notSold = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)

    verifiedBy = models.ForeignKey(User, related_name='verified_properties',
    on_delete=models.SET_NULL, null=True, blank=True)

    location = models.CharField(max_length=255, null=True, blank=True)
    locationUrl = models.TextField(null=True, blank=True)
    is_verifiedproperty = models.BooleanField(default=False)

    user = models.ForeignKey(User, related_name='properties', on_delete=models.CASCADE)

    # Add direct file fields to the model
    image = models.ImageField(upload_to='property_images/', null=True, blank=True)
    video = models.FileField(upload_to='property_videos/', null=True, blank=True)
    document = models.FileField(upload_to='property_documents/', null=True, blank=True)

    def __str__(self):
        return f"{self.projectName} - {self.selectProperty}"



# franchise Form
class FranchiseApplication(models.Model):
    full_name = models.CharField(max_length=100, null=False, blank=False)
    email = models.EmailField(null=False, blank=False)
    contact = models.CharField(max_length=20, null=False, blank=False) 
    location = models.CharField(max_length=100, null=False, blank=False)
    experience = models.TextField(blank=True, null=True)
    reason = models.TextField(blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def _str_(self):
        return f"{self.full_name} - {self.location}"
    

    
class FranchiseProperty(models.Model):
    property = models.ForeignKey(AddPropertyModel, on_delete=models.CASCADE)

    # Store Property ID separately as requested
    property_id_number = models.IntegerField(null=True, blank=True)

    franchise = models.ForeignKey(User, on_delete=models.CASCADE)

    reviews = models.TextField(null=True, blank=True)
    amount = models.FloatField(null=True, blank=True)
    verified_location = models.CharField(max_length=200, null=True, blank=True)
    video_file = models.FileField(upload_to="verification_videos/", null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Verification for Property {self.property_id_number}"
    

    
    
class FutureRequirement(models.Model):
    property_type = models.CharField(max_length=100)
    extent = models.CharField(max_length=100)
    bhk_type = models.CharField(max_length=50)
    facing = models.CharField(max_length=50)
    budget = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    approval_type = models.CharField(max_length=100)
    project_name = models.CharField(max_length=150)
    company_name = models.CharField(max_length=150)
    created_at = models.DateTimeField(auto_now_add=True)  # 👈 important

    def _str_(self):
        return f"{self.property_type} - {self.city}"
    


# move request*************

class MoveRequest(models.Model):
    customer_name = models.CharField(max_length=100)
    number = models.CharField(max_length=20)
    alternate_number = models.CharField(max_length=20, blank=True, null=True)
    service_type = models.CharField(max_length=50)
    from_location = models.CharField(max_length=255)
    to_location = models.CharField(max_length=255)
    from_floor = models.CharField(max_length=50, blank=True, null=True)
    to_floor = models.CharField(max_length=50, blank=True, null=True)
    men_power = models.CharField(max_length=50, blank=True, null=True)
    vehicle_type = models.CharField(max_length=50, blank=True, null=True)
    additional_info = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer_name} ({self.service_type})"
    

    from django.db import models

class ContactForm(models.Model):
    customer_name = models.CharField(max_length=100)
    number = models.CharField(max_length=15)
    alternate_number = models.CharField(max_length=15, blank=True, null=True)
    renovation_type = models.CharField(max_length=100)
    location = models.CharField(max_length=255)
    additional_info = models.TextField(blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer_name} - {self.renovation_type}"

    # loan application

    
class LoanApplication(models.Model):
    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    dob = models.DateField()
    street_address = models.CharField(max_length=255)
    unit = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    loan_amount = models.DecimalField(max_digits=10, decimal_places=2)
    loan_purpose = models.CharField(max_length=100)
    application_date = models.DateField()
    employment_status = models.CharField(max_length=50)
    realtor = models.CharField(max_length=10)
    credit_score = models.CharField(max_length=50)
    agree = models.BooleanField(default=False)
    submitted_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} - {self.loan_purpose}"
    
    
    # add project**********
class AddProject(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    plan_type = models.CharField(max_length=50, choices=PlanType.choices, null=True, blank=True)

    project_name = models.CharField(max_length=100)
    type_of_project = models.CharField(max_length=100)
    project_location = models.CharField(max_length=200)
    location_url = models.CharField(max_length=300)
    number_of_units = models.CharField(max_length=100)
    available_units = models.CharField(max_length=100)
    available_facing = models.CharField(max_length=100)
    available_sizes = models.CharField(max_length=100)

    rera_approved = models.BooleanField(null=True, blank=True)
    select_amenities = models.CharField(max_length=255, null=True, blank=True)
    highlights = models.CharField(max_length=100)
    type_of_approval = models.CharField(max_length=100)
    total_project_area = models.CharField(max_length=100)
    contact_info = models.IntegerField()
    pricing = models.IntegerField()

    image = models.ImageField(upload_to='project_image/', null=True, blank=True)
    video = models.FileField(upload_to='project_video/', null=True, blank=True)
    document = models.FileField(upload_to='project_docs/', null=True, blank=True)

    def __str__(self):
        return self.project_name



class ProjectImage(models.Model):
    project = models.ForeignKey(AddProject, related_name="extra_images", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="project_extra/")

    def __str__(self):
        return f"Image for {self.project.project_name}"
    


class SavedProperty(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    property = models.ForeignKey(AddPropertyModel, on_delete=models.CASCADE)
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "property")

    def _str_(self):
        return f"{self.user.username} saved {self.property.title}"
    


    # companny contact
 
class ContactMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=150)
    email = models.EmailField(max_length=150, null=True, blank=True)
    requirement = models.CharField(max_length=255, null=True, blank=True)
    message = models.TextField(null=True, blank=True)
    cid = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "company_contact"

    def __str__(self):
        return self.name
    


class Reels(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    reel=models.FileField(upload_to='reels/',null=True,blank=True)
    description=models.CharField(max_length=50)
    likeCount=models.IntegerField(default=0)
    commentCount=models.IntegerField(default=0)
    shareCount=models.IntegerField(default=0)
class Comment(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    reel=models.ForeignKey(Reels,on_delete=models.CASCADE)
    comment=models.CharField(max_length=255)
    created_at=models.DateTimeField(auto_now_add=True)
    def _str_(self):
        return self.comment
    





 
    
    


    


    