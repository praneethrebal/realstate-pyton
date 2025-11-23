from django import forms
from .models import Property, PropertyImage, Buyer, Purchase

class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        exclude = ['luck_id', 'available_tickets', 'created_at']

class PropertyImageForm(forms.ModelForm):
    class Meta:
        model = PropertyImage
        fields = ['image', 'caption']

class BuyerForm(forms.ModelForm):
    class Meta:
        model = Buyer
        exclude = []

class PurchaseForm(forms.ModelForm):
    class Meta:
        model = Purchase
        fields = ['property', 'buyer', 'transaction_id', 'payment_screenshot']


from django import forms
from .models import Property

class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = [
            'owner_name', 'phone_number', 'alternate_number', 'address', 'address_url',
            'description', 'ticket_price', 'total_tickets', 'property_value', 'active', 'image'
        ]
