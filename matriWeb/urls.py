from django.contrib import admin
from django.urls import path
from App import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name="home"),
    path('registro/', views.registro, name='registro'),
    path('signin/', views.signin, name="signin"),
    #path('signin_consejero/', views.signin_consejero, name='signin_consejero'),
    path('signout/', views.signout, name='signout'),
    path('usuario/<str:username>/', views.perfil, name='perfil'),
    path('matricula/', views.matricula, name='matricula'),
    path('historial/', views.historial, name='historial'),
    path('solicitud/', views.solicitud, name='solicitud'),
]
