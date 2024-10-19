from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegistroForm, LoginForm, MatriculaForm, FiltrarCursosForm, RecuperarContrasenaForm
from .models import Alumno, Usuario, Curso, CursoPrerrequisito, Boucher, Matricula
from django.utils import timezone
from .decorators import alumno_required, consejero_required, admin_required, admin_o_consejero_required
from django.db.models import Max
from django.http import HttpResponse
from django.template import Context
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.core.mail import EmailMessage
from django.conf import settings
from django.db import transaction
from django.db.models import Count, Q


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

def recuperar_contrasena(request):
    if request.method == 'POST':
        form = RecuperarContrasenaForm(request.POST)
        if form.is_valid():
            codigo = form.cleaned_data['codigo']
            dni = form.cleaned_data['dni']
            nueva_contrasena = form.cleaned_data['nueva_contrasena']

            try:
                alumno = Alumno.objects.get(codigo=codigo, dni=dni)
                usuario = alumno.usuario 

                usuario.set_password(nueva_contrasena)
                usuario.save()

                messages.success(request, 'La contraseña ha sido cambiada exitosamente.')
                return redirect('signin') 
            except Alumno.DoesNotExist:
                messages.error(request, 'Los datos ingresados no coinciden.')

    else:
        form = RecuperarContrasenaForm()

    return render(request, 'recuperar_contrasena.html', {'form': form})

@login_required
@alumno_required
def perfil(request, username):
    usuario = get_object_or_404(Usuario, username=username) 
    alumno = usuario.alumno
    return render(request, 'perfil.html', {'usuario': usuario, 'alumno': alumno})

@login_required
@alumno_required
def matricula(request):
    usuario = request.user
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
                boucher1 = Boucher.objects.create(
                    alumno=alumno,
                    numero_boucher=form_matricula.cleaned_data['numero_recibo1'],
                    monto=form_matricula.cleaned_data['monto_recibo1']
                )

                boucher2 = Boucher.objects.create(
                    alumno=alumno,
                    numero_boucher=form_matricula.cleaned_data['numero_recibo2'],
                    monto=form_matricula.cleaned_data['monto_recibo2']
                )

                matricula = Matricula.objects.create(
                    alumno=alumno,
                    plan=alumno.plan,
                    fecha_matricula=timezone.now()
                )
                matricula.cursos.set(Curso.objects.filter(id__in=cursos_seleccionados))
                matricula.boucher.add(boucher1, boucher2)  

                request.session['cursos_seleccionados'] = []
                messages.success(request, "Matrícula guardada con éxito.")

        elif 'curso_id' in request.POST:
            curso_id = request.POST.get('curso_id')
            curso = get_object_or_404(Curso, id=int(curso_id))
                # Verificar si el curso aún tiene cupos disponibles
            if curso.cupos_disponibles > 0:
                creditos_actuales = sum(curso.creditos for curso in Curso.objects.filter(id__in=cursos_seleccionados))

                if creditos_actuales + curso.creditos <= 44:
                    cursos_seleccionados.append(int(curso_id))
                    request.session['cursos_seleccionados'] = cursos_seleccionados
                else:
                    messages.error(request, "No puedes añadir más cursos. El límite es 44 créditos.")
            else:
                messages.error(request, "Este curso ya no tiene cupos disponibles.")


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
@alumno_required
def historial(request):
    usuario = request.user
    try:
        alumno = get_object_or_404(Alumno, codigo=usuario.alumno.codigo)
        matricula = Matricula.objects.filter(alumno=alumno).latest('fecha_matricula')
    except Matricula.DoesNotExist:
        matricula = None

    context = {
        'alumno': alumno,
        'matricula': matricula,
        'cursos': matricula.cursos.all() if matricula else [],
        'bouchers': matricula.boucher.all() if matricula else []
    }
    return render(request, 'historial.html', context)

@login_required
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
@admin_o_consejero_required
def ver_matricula(request, matricula_id):
    matricula = get_object_or_404(Matricula, id_matricula=matricula_id)
    cursos = matricula.cursos.all() 
    
    from_inscripciones = request.GET.get('from_inscripciones', False)

    return render(request, 'ver.html', {
        'matricula': matricula,
        'cursos': cursos,
        'from_inscripciones': from_inscripciones,
    })
    
@login_required
@alumno_required
def estado_matricula(request):
    usuario = request.user
    alumno = usuario.alumno
    matricula = Matricula.objects.filter(alumno=alumno).order_by('-fecha_matricula').first()
    return render(request, 'estado.html', {'matricula': matricula})

@login_required
@consejero_required
def aprobar_matricula(request, matricula_id):
    matricula = get_object_or_404(Matricula, id_matricula=matricula_id)

    if request.method == 'POST':
        mensaje_aprobacion = request.POST.get('mensaje_aprobacion', '').strip()
        if mensaje_aprobacion:
            try:
                with transaction.atomic():
                    matricula.estado = 'aprobado'
                    matricula.mensaje_aprobacion = mensaje_aprobacion 
                    matricula.save()

                    for curso in matricula.cursos.all():
                        if curso.cupos_disponibles > 0:
                            curso.cupos_disponibles -= 1
                            curso.save()
                        else:
                            raise ValueError(f"El curso {curso.nombre_curso} ya no tiene cupos disponibles.")
                            
                    messages.success(request, "Matrícula aprobada exitosamente.")
            except ValueError as e:
                messages.error(request, str(e))
                return render(request, 'ver.html', {
                    'matricula': matricula,
                    'error': str(e)
                })
        else:
            return render(request, 'ver.html', {
                'matricula': matricula,
                'error': 'Debes proporcionar un motivo de aprobación.'
            })
    return redirect('ver_matricula', matricula_id=matricula.id_matricula)

@login_required
@consejero_required
def rechazar_matricula(request, matricula_id):
    matricula = get_object_or_404(Matricula, id_matricula=matricula_id)

    if request.method == 'POST':
        mensaje_rechazo = request.POST.get('mensaje_rechazo', '').strip()

        if mensaje_rechazo:
            matricula.estado = 'rechazado'
            matricula.mensaje_rechazo = mensaje_rechazo
            matricula.save()
        else:
            return render(request, 'ver.html', {
                'matricula': matricula,
                'error': 'Debes proporcionar un motivo de rechazo.'
            })

    return redirect('ver_matricula', matricula_id=matricula.id_matricula)

@login_required
def detalles_matricula(request, matricula_id):
    matricula = get_object_or_404(Matricula, id_matricula=matricula_id)
    cursos = matricula.cursos.all() 
    total_creditos = sum(curso.creditos for curso in cursos)
    return render(request, 'detalles.html', {'matricula': matricula, 'cursos': cursos, 'total_creditos': total_creditos})

def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Constancia de matrícula 2024.pdf"'
    
    pisa_status = pisa.CreatePDF(html, dest=response)
    
    if pisa_status.err:
        return HttpResponse('Error al generar el PDF')
    return response

@login_required
def constancia_matricula(request, matricula_id):
    matricula = get_object_or_404(Matricula, id_matricula=matricula_id)
    cursos = matricula.cursos.all() 

    context = {
        'matricula': matricula,
        'cursos': cursos,
        'total_creditos': sum(course.creditos for course in cursos), 
    }

    return render_to_pdf('imprimir.html', context)

@login_required
def ver_constancia_matricula(request, matricula_id):
    matricula = get_object_or_404(Matricula, id_matricula=matricula_id)
    cursos = matricula.cursos.all() 
    total_creditos = sum(curso.creditos for curso in cursos)

    return render(request, 'imprimir.html', {'matricula': matricula, 'cursos': cursos, 'total_creditos': total_creditos})

@login_required
def send_pdf_email(request, matricula_id):
    matricula = get_object_or_404(Matricula, id_matricula=matricula_id)

    context = {
        'matricula': matricula,
        'cursos': matricula.cursos.all(),
        'total_creditos': sum(course.creditos for course in matricula.cursos.all()),
    }
    
    pdf = render_to_pdf('imprimir.html', context)  

    email = EmailMessage(
        subject='Constancia de Matrícula',
        body='Adjunto la constancia de matrícula.',
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[request.POST['correo']], 
    )

    email.attach('Constancia de matrícula 2024.pdf', pdf.content, 'application/pdf')
    email.send()

    return HttpResponse('Correo enviado exitosamente.')

@login_required
@admin_required
def inscripciones(request):
    matriculas_aprobadas = Matricula.objects.filter(estado='aprobado').select_related('alumno').order_by('-fecha_matricula')
    matriculas_rechazadas = Matricula.objects.filter(estado='rechazado').select_related('alumno').order_by('-fecha_matricula')
    matriculas_pendientes = Matricula.objects.filter(estado='pendiente').select_related('alumno').order_by('-fecha_matricula')
    
    context = {
        'matriculas_aprobadas': matriculas_aprobadas,
        'matriculas_rechazadas': matriculas_rechazadas,
        'matriculas_pendientes': matriculas_pendientes,
    }

    return render(request, 'inscripcion.html', context)

@admin_required
def reporte(request):
    matriculas_aprobadas = Matricula.objects.filter(estado='aprobado').select_related('alumno').order_by('-fecha_matricula')
    matriculas_rechazadas = Matricula.objects.filter(estado='rechazado').select_related('alumno').order_by('-fecha_matricula')
    matriculas_pendientes = Matricula.objects.filter(estado='pendiente').select_related('alumno').order_by('-fecha_matricula')

    conteo_por_anio = {
        anio: {
            'aprobadas': Matricula.objects.filter(alumno__anio=anio, estado='aprobado').count(),
            'rechazadas': Matricula.objects.filter(alumno__anio=anio, estado='rechazado').count(),
            'pendientes': Matricula.objects.filter(alumno__anio=anio, estado='pendiente').count()
        }
        for anio in range(1, 6)
    }

    total_aprobadas = matriculas_aprobadas.count()
    total_rechazadas = matriculas_rechazadas.count()
    total_pendientes = matriculas_pendientes.count()

    context = {
        'total_aprobadas': total_aprobadas,
        'total_rechazadas': total_rechazadas,
        'total_pendientes': total_pendientes,
        'conteo_por_anio': conteo_por_anio,
    }
    return render(request, 'reporte.html', context)
