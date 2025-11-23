from django.urls import path,include
from . import views
from django.contrib.auth.views import LogoutView 

app_name = 'prop'

urlpatterns = [
    path("login/register", views.register_user, name="register"),
    path("login/", views.login_user, name="login"),

    path('logout/', LogoutView.as_view(next_page='/login/'),name='logout'),
    path('', views.home, name='home'),
    path('add-property/', views.add_property, name='add_property'),
    # path('properties/', views.property_list, name='property_list'),
    #profile page
    path('user/<int:user_id>/', views.user_detail, name='user_detail'),

    path('all-users/', views.all_users, name="all_users"),

    path('properties/<str:prop>/', views.property_list, name='property_list'),
    path("get-property/<str:prop>/", views.get_Property, name="get_property"),
    path('property/<int:id>/]', views.property_detail, name='property_detail'),
    
    # franchise in home
    
    path("franchise/",views.franchise,name= "franchise"),
    #my requremt form
    path('require/', views.requirement_form, name="require"),

    path('profile/', views.profile , name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('user_uploades/',views.user_uploades, name='user_uploades'),
    path('referral/', views.referral, name='referral'),

    path('loan-form/', views.loan_form, name='loan_form'),

    path("contact/", views.contact_form_view, name="contact_form"),
    path("move-form/", views.move_form, name="move_form"),
    

    path("company-register/", views.company_register, name="company_register"),
    path("franchise-register/", views.franchise_register, name="franchise_register"),
    path("addproject/", views.add_project, name='add_project'),
    
    path("reelUpload",views.reels_upload,name='reelUpload'),
    path('getReel',views.get_reel,name='getReel'),
    path('likeReel/<int:id>',views.like_reel,name='likeReel'),
    path('comment/<int:id>/<str:comment>',views.comment_reel,name='commentReel')
]