from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('create/', views.create_website, name='create_website'),
    path('edit/<int:pk>/', views.edit_website, name='edit_website'),
    path('delete/<int:pk>/', views.delete_website, name='delete_website'),
    path('s/<slug:slug>/', views.public_site, name='public_site'),
    path('profile/', views.profile_view, name='profile'),
    path('change-password/', views.change_password, name='change_password'),
    path('pricing/', views.pricing, name='pricing'),
    path('buy/<str:plan>/', views.buy_plan, name='buy_plan'),
    path('my-orders/', views.my_orders, name='my_orders'),
]