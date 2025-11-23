# listings/urls.py
from django.urls import path
from . import views

app_name = 'lucky'

urlpatterns = [
    path("", views.index, name="index"),
    path("purchase/success/<int:pk>/", views.purchase_success, name="purchase_success"),
    path("property/create/", views.create_property, name="create_property"),  # optional
    path('property/<int:pk>/', views.property_detail, name='property_detail'),
    path('create/', views.create_property, name='create_property'),
    path("property/list/", views.property_list, name='property_list'),
    path('property/<int:pk>/buy/', views.buy_ticket, name='buy_ticket'),  # <-- fixed
    path('verify/<int:purchase_id>/', views.verify_purchase, name='verify_purchase'),
    path("purchase/success/<int:pk>/", views.purchase_success, name="purchase_success"),



    # Admin
    path("owner/register/", views.admin_register, name="admin_register"),
    path("owner/login/", views.admin_login, name="admin_login"),
    path("owner/dashboard/", views.admin_dashboard, name="admin_dashboard"),


    # Client
    path("client/register/", views.client_register, name="client_register"),
    path("client/login/", views.client_login, name="client_login"),
    path("client/dashboard/", views.client_dashboard, name="client_dashboard"),
    path('client/logout/', views.client_logout, name='client_logout'),
]
