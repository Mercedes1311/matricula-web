import os
import django

# Configuración para el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'matriWeb.settings')
django.setup()

from App.models import Usuario, Consejero
from django.contrib.auth.hashers import make_password

# Datos para 5 consejeros y sus usuarios
consejeros_data = [
    {"username": "consejero1", "password": "consejero123", "first_name": "Carlos", "last_name": "Pérez", "email": "consejero1@unfv.edu.pe", "dni": "12345678"},
    {"username": "consejero2", "password": "consejero123", "first_name": "María", "last_name": "Gómez", "email": "consejero2@unfv.edu.pe", "dni": "23456789"},
    {"username": "consejero3", "password": "consejero123", "first_name": "Luis", "last_name": "Ramírez", "email": "consejero3@unfv.edu.pe", "dni": "34567890"},
    {"username": "consejero4", "password": "consejero123", "first_name": "Ana", "last_name": "Fernández", "email": "consejero4@unfv.edu.pe", "dni": "45678901"},
    {"username": "consejero5", "password": "consejero123", "first_name": "Juan", "last_name": "López", "email": "consejero5@unfv.edu.pe", "dni": "56789012"},
]

# Crear registros de Usuario y Consejero
for consejero_data in consejeros_data:
    # Crear usuario
    usuario, created = Usuario.objects.get_or_create(
        username=consejero_data["username"],
        defaults={
            "first_name": consejero_data["first_name"],
            "last_name": consejero_data["last_name"],
            "email": consejero_data["email"],
            "password": make_password(consejero_data["password"]),
            "rol": "consejero"
        }
    )
    
    if created:
        # Si el usuario fue creado, crear el consejero correspondiente
        consejero, consejero_created = Consejero.objects.get_or_create(
            usuario=usuario,
            defaults={
                "dni": consejero_data["dni"]
            }
        )
        
        if consejero_created:
            print(f"Consejero y usuario creados: {usuario.username}")
        else:
            print(f"El consejero con DNI {consejero_data['dni']} ya existe.")
    else:
        print(f"El usuario {consejero_data['username']} ya existe.")

""" def run():
    # Creamos 5 usuarios y consejeros
    for consejero_data in consejeros_data:
        # Crear usuario
        usuario = Usuario.objects.create_user(
            username=consejero_data['username'],
            email=consejero_data['email'],
            password=consejero_data['password'],
            rol='consejero'
        )
        
        # Crear consejero asociado al usuario
        consejero = Consejero.objects.create(
            usuario=usuario,
            dni=consejero_data['dni']
        )
        
        print(f"Consejero {usuario.username} con DNI {consejero.dni} creado.") """
