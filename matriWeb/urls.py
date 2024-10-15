from django.contrib import admin
from django.urls import path
from App import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name="home"),
    path('registro/', views.registro, name='registro'),
    path('signin/', views.signin, name="signin"),
    path('signout/', views.signout, name='signout'),
    path('recuperar-contrasena/', views.recuperar_contrasena, name='recuperar_contrasena'),
    path('usuario/<str:username>/', views.perfil, name='perfil'),
    path('matricula/', views.matricula, name='matricula'),
    path('historial/', views.historial, name='historial'),
    path('solicitud/', views.solicitud, name='solicitud'),
    path('ver-matricula/<int:matricula_id>/', views.ver_matricula, name='ver_matricula'),
    path('estado-matricula/', views.estado_matricula, name='estado_matricula'),
    path('aprobar-matricula/<int:matricula_id>/', views.aprobar_matricula, name='aprobar_matricula'),
    path('rechazar-matricula/<int:matricula_id>/', views.rechazar_matricula, name='rechazar_matricula'),
    path('detalles-matricula/<int:matricula_id>/', views.detalles_matricula, name='detalles_matricula'),
    path('descargar-pdf/<int:matricula_id>/', views.constancia_matricula, name='descargar_pdf'),
    path('ver_constancia_matricula/<int:matricula_id>/', views.ver_constancia_matricula, name='ver_constancia_matricula'),
    path('enviar_pdf/<int:matricula_id>/', views.send_pdf_email, name='enviar_pdf'),
    path('inscripciones/', views.inscripciones, name='inscripciones'),
]
