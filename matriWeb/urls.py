from django.contrib import admin
from django.urls import path, include
from App import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name="home"),
    path('registro/', views.registro, name='registro'),
    path('signin/', views.signin, name="signin"),
    path('signout/', views.signout, name='signout'),
    path('usuario/<str:username>/', views.perfil, name='perfil'),
]
