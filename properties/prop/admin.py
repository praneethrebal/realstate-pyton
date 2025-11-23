from django.contrib import admin
from .models import FranchiseApplication, FutureRequirement, Reels, User, AddPropertyModel,LoanApplication,ContactForm,MoveRequest,AddProject

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_referral_code','username', 'email', 'phone', 'role', 'plan_type', 'click', 'leads')
    search_fields = ('username', 'email', 'phone', 'company_name')
    list_filter = ('role', 'plan_type', 'created_at')

@admin.register(AddPropertyModel)
class AddPropertyModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'projectName', 'selectProperty', 'user', 'is_verified', 'image', 'video', 'document')
    search_fields = ('projectName', 'selectProperty', 'user__username')
    list_filter = ('selectProperty', 'is_verified', 'look')
    
# franchis form
@admin.register(FranchiseApplication)
class FranchiseApplicationAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email", "contact", "location", "submitted_at")
    search_fields = ("full_name", "email", "location")
    
# my requremnt form
@admin.register(FutureRequirement)
class FutureRequirementAdmin(admin.ModelAdmin):
    list_display = (
        "property_type",
        "city",
        "state",
        "budget",
        "location",
    )
    list_filter = ("city", "state", "approval_type")
    search_fields = (
        "property_type",
        "city",
        "state",
        "budget",
        "project_name",
        "company_name",
    )


admin.site.register(MoveRequest)
admin.site.register(ContactForm)
admin.site.register(LoanApplication)
admin.site.register(AddProject)
admin.site.register(Reels)