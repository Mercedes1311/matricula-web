from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegistroForm, LoginForm, MatriculaForm, FiltrarCursosForm
from .models import Alumno, Usuario, Curso, CursoPrerrequisito, Boucher, Matricula
from django.utils import timezone
from .decorators import consejero_required
from django.db.models import Max
from django.http import HttpResponseForbidden

@login_required
def home(request):
    return render(request, "home.html")

def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            codigo = form.cleaned_data.get('codigo')

            try:
                alumno = Alumno.objects.get(codigo=codigo)
            except Alumno.DoesNotExist:
                messages.error(request, 'El código de alumno no existe.')
                return render(request, 'registro.html', {'form': form})

            usuario = form.save(commit=False)
            usuario.username = codigo
            usuario.alumno = alumno
            usuario.rol = 'alumno'
            usuario.save()
            
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=codigo, password=raw_password)
            login(request, user)
            messages.success(request, 'Registro exitoso.')
            return redirect('home')
    else:
        form = RegistroForm()
    return render(request, 'registro.html', {'form': form})

def signin(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home') 
    else:
        form = LoginForm()
    return render(request, 'signin.html', {'form': form} )

def signout(request):
    logout(request)
    return redirect('signin')

@login_required
def perfil(request, username):
    usuario = get_object_or_404(Usuario, username=username) 
    if usuario.rol == 'consejero':
        return redirect('home') 
    alumno = usuario.alumno
    return render(request, 'perfil.html', {'usuario': usuario, 'alumno': alumno})

@login_required
def matricula(request):
    usuario = request.user
    if usuario.rol == 'consejero':
        return redirect('home') 
    alumno = get_object_or_404(Usuario, username=usuario.username).alumno

    form_filtrar = FiltrarCursosForm()
    form_matricula = MatriculaForm()

    cursos_disponibles = []  
    cursos_seleccionados = request.session.get('cursos_seleccionados', []) 

    if request.method == 'POST':
        if 'filtrar_cursos' in request.POST:
            form_filtrar = FiltrarCursosForm(request.POST)
            if form_filtrar.is_valid():
                semestre_seleccionado = form_filtrar.cleaned_data['semestre']
                
                cursos_aprobados = CursoPrerrequisito.objects.filter(alumno=alumno).values_list('curso__codigo', flat=True)
                cursos_disponibles = Curso.objects.filter(anio=alumno.anio, semestre=semestre_seleccionado)

                cursos_a_excluir = []
                for curso in cursos_disponibles:
                    if curso.prerrequisito and curso.prerrequisito not in cursos_aprobados:
                        cursos_prerrequisitos = Curso.objects.filter(codigo=curso.prerrequisito)
                        if cursos_prerrequisitos.exists() and cursos_prerrequisitos.first().anio != alumno.anio:
                            cursos_a_excluir.append(curso.codigo)

                cursos_disponibles = cursos_disponibles.exclude(codigo__in=cursos_a_excluir).order_by('nombre_curso')

        elif 'guardar_matricula' in request.POST:
            form_matricula = MatriculaForm(request.POST)
            if form_matricula.is_valid():
                numero_recibo = form_matricula.cleaned_data['numero_recibo']
                monto_recibo = form_matricula.cleaned_data['monto_recibo']
                
                boucher = Boucher.objects.create(
                    alumno=alumno,
                    numero_boucher=numero_recibo,
                    monto=monto_recibo
                )
                matricula = Matricula.objects.create(
                    alumno=alumno,
                    boucher=boucher,
                    plan=alumno.plan,
                    fecha_matricula=timezone.now()
                )
                matricula.cursos.set(Curso.objects.filter(id__in=cursos_seleccionados))
                request.session['cursos_seleccionados'] = []
                messages.success(request, "Matrícula guardada con éxito.")

        elif 'curso_id' in request.POST:
            curso_id = request.POST.get('curso_id')
            if curso_id and int(curso_id) not in cursos_seleccionados:
                curso = get_object_or_404(Curso, id=int(curso_id))
                creditos_actuales = sum(curso.creditos for curso in Curso.objects.filter(id__in=cursos_seleccionados))

                if creditos_actuales + curso.creditos <= 22:
                    cursos_seleccionados.append(int(curso_id))
                    request.session['cursos_seleccionados'] = cursos_seleccionados
                else:
                    messages.error(request, "No puedes añadir más cursos. El límite es 22 créditos.")


        elif 'eliminar_curso_id' in request.POST:
            curso_id = request.POST.get('eliminar_curso_id')
            if curso_id and int(curso_id) in cursos_seleccionados:
                cursos_seleccionados.remove(int(curso_id))
                request.session['cursos_seleccionados'] = cursos_seleccionados


    cursos_en_canasta = Curso.objects.filter(id__in=cursos_seleccionados)
    creditos_actuales = sum(curso.creditos for curso in cursos_en_canasta)

    return render(request, 'matricula.html', {
        'form_filtrar': form_filtrar,
        'form_matricula': form_matricula,
        'alumno': alumno,
        'cursos_disponibles': cursos_disponibles,
        'cursos_seleccionados': cursos_en_canasta,
        'creditos_actuales': creditos_actuales,
    })

@login_required
def historial(request):
    usuario = request.user
    if usuario.rol == 'consejero':
        return redirect('home')
    alumno = get_object_or_404(Alumno, codigo=usuario.alumno.codigo)
    matricula = Matricula.objects.filter(alumno=alumno).latest('fecha_matricula')

    context = {
        'alumno': alumno,
        'matricula': matricula,
        'cursos': matricula.cursos.all() if matricula else [],  
        'boucher': matricula.boucher if matricula else None
    }
    return render(request, 'historial.html', context)

@consejero_required
def solicitud(request):
    matriculas = Matricula.objects.filter(
        id_matricula__in=Matricula.objects.values('alumno').annotate(ultima_matricula=Max('id_matricula')).values('ultima_matricula')
    ).select_related('alumno').order_by('-fecha_matricula')

    context = {
        'matriculas': matriculas
    }

    return render(request, 'solicitud.html', context)

@login_required
@consejero_required
def ver_matricula(request, id_matricula):
    matricula = get_object_or_404(Matricula, id_matricula=id_matricula)
    cursos = matricula.cursos.all()  # Obtener los cursos de la matrícula

    return render(request, 'ver.html', {
        'matricula': matricula,
        'cursos': cursos,
    })
    
# Función para renderizar el estado de matrícula
def estado_matricula(request):

    usuario = request.user
    
    # Verificar si el usuario tiene el rol de consejero
    if usuario.rol == 'consejero':
        return redirect('home')  # Redirigir al home si es consejero
    
    # Obtener el alumno vinculado al usuario
    alumno = usuario.alumno
    
    # Buscar la última matrícula del alumno
    matricula = Matricula.objects.filter(alumno=alumno).order_by('-fecha_matricula').first()

    # Renderizar el estado de la matrícula
    return render(request, 'estado.html', {'matricula': matricula})

def aprobar_matricula(request, matricula_id):
    # Obtener la matrícula por su ID
    matricula = get_object_or_404(Matricula, id_matricula=matricula_id)

    if request.method == 'POST':
        # Obtener el mensaje de aprobación del formulario
        mensaje_aprobacion = request.POST.get('mensaje_aprobacion', '').strip()

        # Verifica que haya un mensaje de aprobación antes de aprobar
        if mensaje_aprobacion:
            matricula.estado = 'aprobado'
            matricula.mensaje_aprobacion = mensaje_aprobacion  # Guardar el mensaje de aprobación
            
            # Guardar los cambios en la matrícula
            matricula.save()
        else:
            # Si no hay mensaje, puedes agregar una lógica para manejar el error
            return render(request, 'ver.html', {
                'matricula': matricula,
                'error': 'Debes proporcionar un motivo de aprobación.'
            })

    # Redirigir a la misma página o a una página de confirmación
    return redirect('ver_matricula', id_matricula=matricula.id_matricula)

def rechazar_matricula(request, matricula_id):
    matricula = get_object_or_404(Matricula, id_matricula=matricula_id)

    if request.method == 'POST':
        mensaje_rechazo = request.POST.get('mensaje_rechazo', '').strip()

        # Verifica que haya un mensaje de rechazo antes de rechazar
        if mensaje_rechazo:
            matricula.estado = 'rechazado'
            matricula.mensaje_rechazo = mensaje_rechazo
            matricula.save()
        else:
            # Si no hay mensaje, puedes agregar una lógica para manejar el error
            return render(request, 'ver.html', {
                'matricula': matricula,
                'error': 'Debes proporcionar un motivo de rechazo.'
            })

    return redirect('ver_matricula', matricula_id=matricula.id_matricula)

def detalles_matricula(request, id_matricula):
    matricula = get_object_or_404(Matricula, id_matricula=id_matricula)
    cursos = matricula.cursos.all() 
    total_creditos = sum(curso.creditos for curso in cursos)
    return render(request, 'detalles.html', {'matricula': matricula, 'cursos': cursos, 'total_creditos': total_creditos})

