from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import *
ROLE_CHOICES = [
     ('','Select Role'),
    ('PROFESSIONAL', 'Professional'),
    ('OWNER', 'Citizen'),
    ('MARKETER', 'Marketer'),
]

PLAN_CHOICES = [
    ('MARKETER_EXPORT', 'Exports (₹7999)'),
    ('MARKETER_EXPORT_PRO', 'Exports Pro (₹14999)'),
]

CATEGORY_CHOICES = [
    ('Plumber', 'Plumber'),
    ('Painter', 'Painter'),
    ('Electrician', 'Electrician'),
    ('Constructor', 'Constructor'),
    ('Centring', 'Centring'),
    ('Interior designer', 'Interior designer'),
    ('Architecture', 'Architecture'),
    ('Civil engineer', 'Civil engineer'),
    ('Tiles works', 'Tiles works'),
    ('Marble works', 'Marble works'),
    ('Grinate works', 'Grinate works'),
    ('Wood works', 'Wood works'),
    ('Glass works', 'Glass works'),
    ('Steel railing works', 'Steel railing works'),
    ('Carpenter', 'Carpenter'),
    ('Doozer works', 'Doozer works'),
    ('JCB works', 'JCB works'),
    ('Borewells', 'Borewells'),
    ('Material supplier', 'Material supplier'),
]

class UserRegisterForm(UserCreationForm):
    role = forms.ChoiceField(choices=ROLE_CHOICES)
    category = forms.ChoiceField(choices=CATEGORY_CHOICES, required=False)
    plan_type = forms.ChoiceField(choices=PLAN_CHOICES, required=False, widget=forms.RadioSelect(attrs={'class': 'plan-radio-select'}))
    description = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Description'}), required=False)
    location = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Location'}), required=False)
    experience = forms.IntegerField(required=False,widget=forms.NumberInput(attrs={'placeholder': 'Experience'}))
    referred_by_code = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Referral Code (Optional)'}), required=False)
    deals = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Deals (Optional)'}), required=False)
    profile_image_path = forms.ImageField(required=False, widget=forms.FileInput(attrs={'id': 'id_profile_image_path'}))

    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            'username', 'email', 'phone', 
            'role', 'category', 'plan_type', 'description', 'location',
            'experience', 'referred_by_code', 'deals', 'profile_image_path'
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        placeholders = {
            'username': 'Full Name',
            'email': 'Email',
            'phone': 'Phone Number',
            'password1': 'Password',
            'password2': 'Confirm Password',
        }
        for field_name, placeholder_text in placeholders.items():
            self.fields[field_name].widget.attrs['placeholder'] = placeholder_text
            self.fields[field_name].help_text = '' # Remove default help text
        
        # Make profile image label invisible as it's handled by the template
        self.fields['profile_image_path'].label = ""
        

class AddPropertyForm(forms.ModelForm):
    AMENITY_CHOICES = [
        ('Swimming Pool', 'Swimming Pool'),
        ('Gym', 'Gym'),
        ('Playground', 'Playground'),
        ('Park', 'Park'),
        ('Club House', 'Club House'),
    ]

    # New field for predefined amenities (checkboxes)
    predefined_amenities = forms.MultipleChoiceField(
        choices=AMENITY_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Select Amenities"
    )

    # New field for custom amenities (text input)
    custom_amenities_text = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Add other amenity (comma-separated)'}),
        required=False,
        label="Other Amenities"
    )

    class Meta:
        model = AddPropertyModel
        # Explicitly list all fields from the model that the form should handle.
        # This prevents conflicts with the non-model fields defined above.
        fields = [
            'look', 'selectProperty', 'projectName', 'extent', 'facing', 'roadSize',
            'units', 'dimensions', 'numberOfFloors', 'numberOfBHK', 'builtUpArea',
            'openArea', 'rentalIncome', 'floorNo', 'communityType', 'carpetArea',
            'landType', 'soilType', 'roadFacing', 'waterSource', 'unitType', 'zone',
            'developmentType', 'expectedAdvance', 'ratio', 'disputeDetails',
            'lookingToSell', 'problemDetails', 'actualPrice', 'salePrice', 'price',
            'reraApproved', 'approvalType', 'highlights', 'location', 'locationUrl',
            'image', 'video', 'document'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['look'].choices=AddPropertyModel.LOOKING_CHOICES
        self.fields['selectProperty'].choices=AddPropertyModel.PROPERTY_CHOICES
      
        # If an instance is being edited, populate predefined_amenities and custom_amenities_text
        if self.instance and self.instance.pk and self.instance.amenities:
            selected_predefined = []
            custom_amenities_list = []
            for amenity in self.instance.amenities:
                if amenity in dict(self.AMENITY_CHOICES):
                    selected_predefined.append(amenity)
                else:
                    custom_amenities_list.append(amenity)
            self.initial['predefined_amenities'] = selected_predefined
            self.initial['custom_amenities_text'] = ", ".join(custom_amenities_list)

    def save(self, user, commit=True):
        # Let the parent ModelForm save all the model fields first.
        # This is more robust and handles all fields from Step 2 correctly.
        instance = super().save(commit=False) 
        instance.user = user

        # Now, process the non-model amenity fields and update the instance.
        all_amenities = []
        if self.cleaned_data.get('predefined_amenities'):
            all_amenities.extend(self.cleaned_data['predefined_amenities'])
        if self.cleaned_data.get('custom_amenities_text'):
            custom_list = [a.strip() for a in self.cleaned_data['custom_amenities_text'].split(',') if a.strip()]
            all_amenities.extend(custom_list)

        if commit:
            instance.amenities = all_amenities # Assign just before the final save
            instance.save()

        return instance
    
    
# my requremt form

class FutureRequirementForm(forms.ModelForm):
    class Meta:
        model = FutureRequirement
        fields = '__all__'



from django import forms
from .models import User

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'phone',
            'category',
            'location',
            'deals',
            'experience',
            'description',
            'profile_image_path'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

from django import forms
from .models import MoveRequest

class MoveRequestForm(forms.ModelForm):
    class Meta:
        model = MoveRequest
        fields = '__all__'



class CompanyRegisterForm(UserCreationForm):

    company_name = forms.CharField(max_length=255, required=True)
    description = forms.CharField(required=False, widget=forms.Textarea)
    experience = forms.IntegerField(required=False, min_value=0)
    total_projects = forms.IntegerField(required=False, min_value=0)
    ongoing_projects = forms.IntegerField(required=False, min_value=0)
    completed_projects = forms.IntegerField(required=False, min_value=0)
    address = forms.CharField(max_length=255, required=True)
    contact_number = forms.CharField(max_length=15, required=True)

    wallpaper = forms.ImageField(required=False)
    logo = forms.ImageField(required=False)

    # These are NOT User model fields → must NOT be in Meta.fields
    plan = forms.CharField(required=True, widget=forms.HiddenInput())
    duration = forms.IntegerField(required=True)

    class Meta:
        model = User
        fields = [
            "username", "email", "password1", "password2",
            "company_name", "description", "experience",
            "total_projects", "ongoing_projects", "completed_projects",
            "address", "contact_number",
            "wallpaper", "logo"
        ]

    def clean_contact_number(self):
        num = self.cleaned_data["contact_number"]
        if not num.isdigit():
            raise forms.ValidationError("Contact number must be digits.")
        return num
    

class FranchiseForm(UserCreationForm):
    email = forms.EmailField(required=True)
    contact_number = forms.CharField(max_length=15, required=True)
    location = forms.CharField(max_length=255, required=False)
    radius = forms.IntegerField(required=False)
    description = forms.CharField(widget=forms.Textarea, required=False)
    experience = forms.IntegerField(required=False)
    profile_image = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "contact_number",
            "location",
            "radius",
            "description",
            "experience",
            "profile_image",
            "password1",
            "password2",
        ]

    def clean_contact_number(self):
        phone = self.cleaned_data["contact_number"]
        if not phone.isdigit():
            raise forms.ValidationError("Phone number must contain only digits.")
        return phone
    

class ReelsForm(forms.ModelForm):
  class Meta:
        model=Reels
        fields=['reel','description']
        





