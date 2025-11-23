from django.db import models

# Create your models here.
from django.db import models
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from django.db.models import Max
import random
import string
from django.conf import settings
from django.db import models

class Property(models.Model):
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # links to your ClientUser model
        on_delete=models.CASCADE,
        related_name="lucky_properties",null=True,  # allow existing rows without client
    blank=True
    )
    luck_id = models.CharField(max_length=100, unique=True, blank=True, null=True)
    owner_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    alternate_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField()
    address_url = models.URLField(blank=True, null=True)
    description = models.TextField()
    ticket_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_tickets = models.IntegerField()
    available_tickets = models.PositiveIntegerField(blank=True, null=True)  # 👈 Add this line
    property_value = models.DecimalField(max_digits=15, decimal_places=2)
    active = models.BooleanField(default=True)
    image = models.ImageField(upload_to='property_images/')
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Set available_tickets from total_tickets on first save
        if self.available_tickets is None:
            self.available_tickets = self.total_tickets

        # Generate luck_id only once when the object is first created
        if not self.luck_id:
            base = ''.join(ch for ch in self.owner_name.lower() if ch.isalpha())
            if not base:
                base = 'owner'
            count = Property.objects.filter(luck_id__startswith=base).count()
            next_num = 1001 + count
            self.luck_id = f"{base}{next_num}"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.luck_id} - {self.owner_name}"
    @property
    def tickets_sold(self):
       return self.total_tickets - (self.available_tickets or 0)
    @property
    def tickets_available(self):
      return self.available_tickets or self.total_tickets




class PropertyImage(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="property_images/")
    caption = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"Image for {self.property.luck_id}"
        
class Buyer(models.Model):
    COUNTRY_CODES = [
        ('1', '🇺🇸 USA / Canada (+1)'),
        ('44', '🇬🇧 UK (+44)'),
        ('91', '🇮🇳 India (+91)'),
        ('61', '🇦🇺 Australia (+61)'),
        ('971', '🇦🇪 UAE (+971)'),
    ]

    full_name = models.CharField(max_length=150)
    mobile = models.CharField(max_length=20, unique=True)
    whatsapp_no = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    area_city = models.CharField(max_length=200)
    district = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country_code = models.CharField(
        max_length=5,
        choices=COUNTRY_CODES,
        default='91'
    )

    def __str__(self):
        return f"{self.full_name} ({self.mobile})"

import random
import string
from django.db import models
from django.utils.text import slugify

import random, string
from django.db import models

class Purchase(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("VERIFIED", "Verified"),
        ("REJECTED", "Rejected"),
    ]

    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="purchases")
    buyer = models.ForeignKey(Buyer, on_delete=models.CASCADE, related_name="purchases")
    ticket_price = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=200, blank=True, unique=True)
    payment_screenshot = models.ImageField(upload_to="payments/")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="PENDING")
    created_at = models.DateTimeField(auto_now_add=True)
    ticket_code = models.CharField(max_length=50, blank=True, null=True)  # ✅ single ticket ID

    def save(self, *args, **kwargs):
        if not self.ticket_code:
            # generate format: <luck_id>-tick<4-digit>
            random_id = ''.join(random.choices(string.digits, k=4))
            self.ticket_code = f"{self.property.luck_id}-tick{random_id}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.ticket_code} - {self.buyer.full_name}"

    def save(self, *args, **kwargs):
        if not self.ticket_code:
            # generate format: <luck_id>-tick<4-digit>
            random_id = ''.join(random.choices(string.digits, k=4))
            self.ticket_code = f"{self.property.luck_id}-tick{random_id}"
        super().save(*args, **kwargs)






from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

# ✅ Common User Manager
class UserManager(BaseUserManager):
    def create_user(self, phone, password=None, **extra_fields):
        if not phone:
            raise ValueError("Phone number is required")
        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password=None, **extra_fields):
        extra_fields.setdefault('is_admin', True)
        return self.create_user(phone, password, **extra_fields)


# ✅ Admin User
class AdminUser(AbstractBaseUser):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, unique=True)
    is_admin = models.BooleanField(default=False)

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['email', 'name']

    objects = UserManager()

    def __str__(self):
        return f"{self.name} ({self.phone})"


# ✅ Client User
class ClientUser(AbstractBaseUser):
    username = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, unique=True)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['username']

    objects = UserManager()

    def __str__(self):
        return self.username
