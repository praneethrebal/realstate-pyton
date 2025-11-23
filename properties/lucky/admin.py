from django.contrib import admin
from django.utils.html import format_html
import urllib.parse

from .models import Property, PropertyImage, Buyer, Purchase


# ---------- PROPERTY ADMIN ----------
@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = (
        "luck_id",
        "owner_name",
        "ticket_price",
        "total_tickets",
        "available_tickets",
        "property_value",
        "active",
    )
    search_fields = ("luck_id", "owner_name", "address")
    list_filter = ("active",)
    readonly_fields = ("luck_id",)

    def available_tickets(self, obj):
        sold = sum(p.quantity for p in obj.purchases.all())
        return obj.total_tickets - sold


# ---------- PROPERTY IMAGE ADMIN ----------
@admin.register(PropertyImage)
class PropertyImageAdmin(admin.ModelAdmin):
    list_display = ("property", "caption")

from django.contrib import admin
from .models import Buyer

@admin.register(Buyer)
class BuyerAdmin(admin.ModelAdmin):
    list_display = ("full_name", "mobile", "whatsapp_no", "country_code", "district", "state")
    search_fields = ("full_name", "mobile", "whatsapp_no")



# ---------- PURCHASE ADMIN ----------

import urllib.parse
from django.contrib import admin
from django.utils.html import format_html
from .models import Property, Buyer, Purchase


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = (
        "ticket_code",
        "property",
        "buyer",
        "ticket_price",
        "status",
        "created_at",
        "send_whatsapp_button",
    )
    list_filter = ("status", "created_at")
    search_fields = ("buyer__mobile", "transaction_id", "property__luck_id")
    readonly_fields = ("ticket_code", "created_at")

    actions = ["mark_verified", "mark_rejected"]

    # ✅ WhatsApp send button (auto formats message)
    def send_whatsapp_button(self, obj):
        if not obj.buyer.whatsapp_no:
            return "—"

        number = obj.buyer.whatsapp_no.replace(" ", "").replace("+", "")
        property_name = obj.property.owner_name
        property_value = f"₹{obj.property.property_value:,.0f}"
        image_url = obj.property.image.url if obj.property.image else ""
        luck_id = obj.property.luck_id
        ticket_id = obj.ticket_code
        name = obj.buyer.full_name

        # 📩 Dynamic WhatsApp message per status
        if obj.status == "VERIFIED":
            message = (
                f"🎉 Hi {name}!\n"
                f"Your ticket has been VERIFIED ✅\n\n"
                f"🏠 Property: *{property_name}*\n"
                f"💰 Value: {property_value}\n"
                f"🎫 Luck ID: {luck_id}\n"
                f"🎟️ Ticket ID: {ticket_id}\n"
                f"🖼️ Image: {image_url}\n\n"
                f"Thank you for participating in our Lucky Property Draw! 🌟"
            )
        elif obj.status == "REJECTED":
            message = (
                f"⚠️ Hi {name},\n"
                f"Unfortunately, your ticket *{ticket_id}* for property *{property_name}* "
                f"(Luck ID: {luck_id}) has been *REJECTED*.\n\n"
                f"If you believe this is a mistake, please contact support."
            )
        else:
            message = (
                f"⏳ Hi {name},\n"
                f"Your ticket *{ticket_id}* for property *{property_name}* "
                f"(Luck ID: {luck_id}) is currently *PENDING* verification.\n\n"
                f"We’ll notify you once it’s verified!"
            )

        encoded_msg = urllib.parse.quote(message)
        url = f"https://wa.me/91{number}?text={encoded_msg}"

        return format_html(
            f'<a class="button" href="{url}" target="_blank">📩 Send WhatsApp</a>'
        )

    send_whatsapp_button.short_description = "Send Message"

    # ✅ Mark Verified Action
    def mark_verified(self, request, queryset):
        queryset.update(status="VERIFIED")
        self.message_user(request, "✅ Selected purchases marked as VERIFIED")

    # ✅ Mark Rejected Action
    def mark_rejected(self, request, queryset):
        queryset.update(status="REJECTED")
        self.message_user(request, "❌ Selected purchases marked as REJECTED")

    mark_verified.short_description = "Mark selected as VERIFIED"
    mark_rejected.short_description = "Mark selected as REJECTED"


# listings/admin.py
from django.contrib import admin
from .models import AdminUser, ClientUser

@admin.register(AdminUser)
class AdminUserAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'is_admin')
    search_fields = ('name', 'email', 'phone')
    list_filter = ('is_admin',)

@admin.register(ClientUser)
class ClientUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'phone', 'is_active')
    search_fields = ('username', 'email', 'phone')
    list_filter = ('is_active',)

@property
def is_admin(self):
    return self.role == 'admin'

@property
def is_client(self):
    return self.role == 'client'
