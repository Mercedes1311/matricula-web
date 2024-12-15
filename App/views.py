from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegistroForm, LoginForm, MatriculaForm, FiltrarCursosForm, RecuperarContrasenaForm
from .models import Alumno, Usuario, Curso, CursoPrerrequisito, Boucher, Matricula, BoucherBanco
from .decorators import alumno_required, administrador_required
from django.utils import timezone
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
                numero_recibo1 = form_matricula.cleaned_data['numero_recibo1']
                numero_recibo2 = form_matricula.cleaned_data['numero_recibo2']
                
                boucher1 = BoucherBanco.objects.filter(
                    codigo_boucher=numero_recibo1, 
                    codigo_alumno=alumno.codigo
                ).first()

                boucher2 = BoucherBanco.objects.filter(
                    codigo_boucher=numero_recibo2,
                    codigo_alumno=alumno.codigo
                ).first()

                if not boucher1 or not boucher2:
                    messages.error(request, "Uno o ambos bouchers son inválidos o no pertenecen al alumno.")
                else:
                    boucher1_nuevo = Boucher.objects.create(
                        alumno=alumno,
                        numero_boucher=boucher1.codigo_boucher,
                        monto=boucher1.monto
                    )

                    boucher2_nuevo = Boucher.objects.create(
                        alumno=alumno,
                        numero_boucher=boucher2.codigo_boucher,
                        monto=boucher2.monto
                    )

                    # Crear la matrícula y asignarla como aprobada
                    matricula = Matricula.objects.create(
                        alumno=alumno,
                        plan=alumno.plan,
                        fecha_matricula=timezone.now(),
                        estado='aprobado'  # Estado aprobado sin necesidad de consejero
                    )
                    matricula.cursos.set(Curso.objects.filter(id__in=cursos_seleccionados))
                    matricula.boucher.add(boucher1_nuevo, boucher2_nuevo)  

                    request.session['cursos_seleccionados'] = []
                    return redirect('historial')

        elif 'curso_id' in request.POST:
            curso_id = request.POST.get('curso_id')
            curso = get_object_or_404(Curso, id=int(curso_id))
            
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
@administrador_required
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
@administrador_required
def inscripciones(request):
    matriculas_aprobadas = Matricula.objects.filter(estado='aprobado').select_related('alumno').order_by('-fecha_matricula')

    context = {
        'matriculas_aprobadas': matriculas_aprobadas,
    }

    return render(request, 'inscripcion.html', context)

@administrador_required
def reporte(request):
    # Solo contar y mostrar las matrículas aprobadas
    matriculas_aprobadas = Matricula.objects.filter(estado='aprobado').select_related('alumno').order_by('-fecha_matricula')

    # Solo contar las matrículas aprobadas
    total_aprobadas = matriculas_aprobadas.count()

    # Conteo por año solo para matrículas aprobadas
    conteo_por_anio = {
        anio: {
            'aprobadas': Matricula.objects.filter(alumno__anio=anio, estado='aprobado').count(),
        }
        for anio in range(1, 6)
    }

    context = {
        'total_aprobadas': total_aprobadas,
        'conteo_por_anio': conteo_por_anio,
    }
    
    return render(request, 'reporte.html', context)
