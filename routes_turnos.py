"""
Rutas para la gestión de turnos y horarios.

Este módulo proporciona las vistas y controladores para:
- Gestionar turnos (creación, modificación, eliminación)
- Visualizar el calendario de horarios
- Asignar turnos a empleados
- Gestionar ausencias de empleados
- Visualizar estadísticas de turnos
"""

from flask import (Blueprint, render_template, redirect, url_for, request,
                 flash, jsonify, abort, current_app, g, send_file)
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

import os
from datetime import datetime, date, time, timedelta
import io
import json
import calendar
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side

from app import db
from models import Company, Employee, User, Activity, Role
from models_turnos import (
    Turno, Horario, Ausencia, RequisitoPersonal, PlantillaHorario, 
    DetallePlantilla, AsignacionPlantilla, PreferenciaDisponibilidad,
    HistorialCambios, TipoTurno, TipoAusencia
)
from forms_turnos import (
    TurnoForm, HorarioForm, AusenciaForm, PlantillaHorarioForm,
    DetallePlantillaForm, AsignacionPlantillaForm, AsignacionMasivaForm,
    FiltroCalendarioForm, EliminarHorarioForm, PreferenciaDisponibilidadForm,
    RequisitoPersonalForm
)
from utils import log_activity, get_company_or_404
from sqlalchemy import or_, and_, extract, func, case, literal_column

# Crear el blueprint de turnos
turnos_bp = Blueprint('turnos', __name__, url_prefix='/turnos')

def init_app(app):
    """Inicializa el blueprint de turnos en la aplicación Flask."""
    app.register_blueprint(turnos_bp)

# Funciones auxiliares
def get_semana_actual():
    """Obtiene la fecha del lunes de la semana actual."""
    today = date.today()
    # El lunes es 0, domingo es 6
    dias_al_lunes = today.weekday()
    return today - timedelta(days=dias_al_lunes)

def get_rango_semana(fecha_base):
    """
    Calcula el rango de fechas para una semana, empezando en lunes.
    
    Args:
        fecha_base: Una fecha dentro de la semana deseada.
        
    Returns:
        Tupla con (fecha_inicio, fecha_fin) representando lunes y domingo.
    """
    # Asegurarse de que tenemos un objeto date
    if isinstance(fecha_base, str):
        fecha_base = datetime.strptime(fecha_base, '%Y-%m-%d').date()
        
    # Calcular el lunes (inicio de semana)
    dias_al_lunes = fecha_base.weekday()
    inicio_semana = fecha_base - timedelta(days=dias_al_lunes)
    
    # Calcular el domingo (fin de semana)
    fin_semana = inicio_semana + timedelta(days=6)
    
    return inicio_semana, fin_semana

def puede_ver_empresa(company_id):
    """
    Verifica si el usuario actual puede ver la empresa especificada.
    
    Args:
        company_id: ID de la empresa a verificar.
        
    Returns:
        Boolean indicando si tiene acceso.
    """
    if current_user.is_admin:
        return True
        
    # Obtener las empresas del usuario
    if not current_user.companies:
        return False
        
    # Verificar si la empresa solicitada está en las empresas del usuario
    return any(str(company.id) == str(company_id) for company in current_user.companies)

def get_nombre_mes(mes):
    """Obtiene el nombre del mes en español."""
    nombres_meses = [
        "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
        "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
    ]
    try:
        return nombres_meses[mes - 1]
    except IndexError:
        return "Mes desconocido"

def get_nombre_dia(dia):
    """Obtiene el nombre del día en español."""
    nombres_dias = [
        "Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"
    ]
    try:
        return nombres_dias[dia]
    except IndexError:
        return "Día desconocido"

# Rutas de turnos
@turnos_bp.route('/dashboard/<int:company_id>')
@login_required
def dashboard(company_id):
    """Muestra el panel de control del sistema de turnos."""
    # Verificar acceso a la empresa
    company = get_company_or_404(company_id)
    if not puede_ver_empresa(company_id):
        abort(403)
    
    # Obtener estadísticas
    num_turnos = Turno.query.filter_by(company_id=company_id).count()
    
    # Empleados de la empresa
    empleados = Employee.query.filter_by(company_id=company_id, is_active=True).all()
    num_empleados = len(empleados)
    
    # Turnos activos en la semana actual
    hoy = date.today()
    lunes, domingo = get_rango_semana(hoy)
    
    horarios_semana = (Horario.query
                      .join(Turno)
                      .join(Employee)
                      .filter(
                          Turno.company_id == company_id,
                          Horario.fecha.between(lunes, domingo)
                      )
                      .count())
    
    # Ausencias activas
    ausencias_activas = (Ausencia.query
                         .join(Employee)
                         .filter(
                             Employee.company_id == company_id,
                             Ausencia.fecha_inicio <= hoy,
                             Ausencia.fecha_fin >= hoy
                         )
                         .count())
    
    # Últimos cambios en horarios
    cambios_recientes = (HistorialCambios.query
                        .join(Horario)
                        .join(Turno)
                        .filter(Turno.company_id == company_id)
                        .order_by(HistorialCambios.fecha_cambio.desc())
                        .limit(5)
                        .all())
    
    # Próximos días con más turnos asignados
    proximas_fechas_concurridas = db.session.query(
        Horario.fecha,
        func.count(Horario.id).label('num_turnos')
    ).join(Turno).join(Employee).filter(
        Turno.company_id == company_id,
        Horario.fecha >= hoy,
        Horario.fecha <= hoy + timedelta(days=30)
    ).group_by(Horario.fecha).order_by(
        func.count(Horario.id).desc()
    ).limit(5).all()
    
    return render_template(
        'turnos/dashboard.html',
        company=company,
        num_turnos=num_turnos,
        num_empleados=num_empleados,
        horarios_semana=horarios_semana,
        ausencias_activas=ausencias_activas,
        cambios_recientes=cambios_recientes,
        proximas_fechas_concurridas=proximas_fechas_concurridas,
        lunes=lunes,
        domingo=domingo
    )

@turnos_bp.route('/calendario/<int:company_id>')
@login_required
def calendario(company_id):
    """Muestra el calendario de turnos."""
    # Verificar acceso a la empresa
    company = get_company_or_404(company_id)
    if not puede_ver_empresa(company_id):
        abort(403)
    
    # Obtener la semana a mostrar (por defecto la semana actual)
    fecha_semana = request.args.get('semana')
    
    if fecha_semana:
        try:
            fecha_semana = datetime.strptime(fecha_semana, '%Y-%m-%d').date()
        except ValueError:
            fecha_semana = get_semana_actual()
    else:
        fecha_semana = get_semana_actual()
    
    # Calcular inicio y fin de semana
    inicio_semana, fin_semana = get_rango_semana(fecha_semana)
    
    # Calcular semana anterior y siguiente
    semana_anterior = inicio_semana - timedelta(days=7)
    semana_siguiente = inicio_semana + timedelta(days=7)
    
    # Obtener empleados de la empresa
    empleados = Employee.query.filter_by(company_id=company_id, is_active=True).order_by(Employee.nombre).all()
    
    # Obtener turnos de la empresa
    turnos = Turno.query.filter_by(company_id=company_id, is_active=True).all()
    
    # Obtener horarios para la semana
    horarios = (Horario.query
               .join(Turno)
               .join(Employee)
               .filter(
                   Turno.company_id == company_id,
                   Horario.fecha.between(inicio_semana, fin_semana),
                   Employee.is_active == True
               )
               .all())
    
    # Preparar los datos para el calendario
    datos_calendario = {}
    
    for empleado in empleados:
        datos_calendario[empleado.id] = {
            'empleado': empleado,
            'dias': {}
        }
        
        # Inicializar los días de la semana
        for i in range(7):
            fecha_actual = inicio_semana + timedelta(days=i)
            datos_calendario[empleado.id]['dias'][fecha_actual] = []
            
    # Añadir horarios a los días correspondientes
    for horario in horarios:
        if horario.employee_id in datos_calendario:
            datos_calendario[horario.employee_id]['dias'][horario.fecha].append(horario)
    
    # Obtener ausencias activas en esta semana
    ausencias = (Ausencia.query
                .join(Employee)
                .filter(
                    Employee.company_id == company_id,
                    Employee.is_active == True,
                    or_(
                        and_(Ausencia.fecha_inicio <= fin_semana, Ausencia.fecha_fin >= inicio_semana)
                    )
                )
                .all())
    
    # Preparar datos de ausencias
    datos_ausencias = {}
    for ausencia in ausencias:
        if ausencia.employee_id not in datos_ausencias:
            datos_ausencias[ausencia.employee_id] = []
        datos_ausencias[ausencia.employee_id].append(ausencia)
    
    # Preparar datos de fechas para la vista
    dias_semana = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    
    dias_semana_fechas = []
    for i in range(7):
        dias_semana_fechas.append(inicio_semana + timedelta(days=i))
    
    # Formulario para eliminar un horario
    eliminar_form = EliminarHorarioForm()
    
    # Obtener nombres de meses en español
    meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", 
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    
    return render_template(
        'turnos/calendario.html',
        company=company,
        datos_calendario=datos_calendario,
        datos_ausencias=datos_ausencias,
        inicio_semana=inicio_semana,
        fin_semana=fin_semana,
        semana_anterior=semana_anterior,
        semana_siguiente=semana_siguiente,
        dias_semana=dias_semana,
        dias_semana_fechas=dias_semana_fechas,
        today=date.today(),
        turnos=turnos,
        eliminar_form=eliminar_form,
        meses=meses
    )

@turnos_bp.route('/turnos/<int:company_id>')
@login_required
def listar_turnos(company_id):
    """Muestra la lista de tipos de turnos para una empresa."""
    # Verificar acceso a la empresa
    company = get_company_or_404(company_id)
    if not puede_ver_empresa(company_id):
        abort(403)
        
    # Obtener todos los turnos de la empresa
    turnos = Turno.query.filter_by(company_id=company_id).order_by(Turno.nombre).all()
    
    # Estadísticas de uso de turnos
    estadisticas = {}
    for turno in turnos:
        # Contar cuántos horarios usan este turno
        num_usos = Horario.query.filter_by(turno_id=turno.id).count()
        estadisticas[turno.id] = {
            'usos': num_usos,
            'horas_efectivas': turno.horas_efectivas
        }
        
    return render_template(
        'turnos/listar_turnos.html',
        company=company,
        turnos=turnos,
        estadisticas=estadisticas
    )

@turnos_bp.route('/turnos/<int:company_id>/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_turno(company_id):
    """Crea un nuevo tipo de turno."""
    # Verificar acceso a la empresa
    company = get_company_or_404(company_id)
    if not puede_ver_empresa(company_id):
        abort(403)
        
    form = TurnoForm()
    form.company_id.data = company_id
    
    if form.validate_on_submit():
        # Convertir el tipo de enum de string a objeto TipoTurno
        tipo_turno = TipoTurno[form.tipo.data]
        
        turno = Turno(
            nombre=form.nombre.data,
            tipo=tipo_turno,
            hora_inicio=form.hora_inicio.data,
            hora_fin=form.hora_fin.data,
            color=form.color.data,
            descanso_inicio=form.descanso_inicio.data,
            descanso_fin=form.descanso_fin.data,
            descripcion=form.descripcion.data,
            company_id=company_id
        )
        
        db.session.add(turno)
        db.session.commit()
        
        log_activity(f"Creado nuevo turno: {turno.nombre}")
        flash(f'Turno {turno.nombre} creado correctamente.', 'success')
        return redirect(url_for('turnos.listar_turnos', company_id=company_id))
        
    return render_template(
        'turnos/form_turno.html',
        company=company,
        form=form,
        turno=None
    )

@turnos_bp.route('/turnos/<int:company_id>/editar/<int:turno_id>', methods=['GET', 'POST'])
@login_required
def editar_turno(company_id, turno_id):
    """Edita un tipo de turno existente."""
    # Verificar acceso a la empresa
    company = get_company_or_404(company_id)
    if not puede_ver_empresa(company_id):
        abort(403)
        
    # Obtener el turno o devolver 404
    turno = Turno.query.filter_by(id=turno_id, company_id=company_id).first_or_404()
    
    form = TurnoForm(obj=turno)
    form.company_id.data = company_id
    
    # Asignar valor del enum al formulario (solo para GET)
    if request.method == 'GET':
        form.tipo.data = turno.tipo.name
    
    if form.validate_on_submit():
        # Convertir el tipo de enum de string a objeto TipoTurno
        tipo_turno = TipoTurno[form.tipo.data]
        
        turno.nombre = form.nombre.data
        turno.tipo = tipo_turno
        turno.hora_inicio = form.hora_inicio.data
        turno.hora_fin = form.hora_fin.data
        turno.color = form.color.data
        turno.descanso_inicio = form.descanso_inicio.data
        turno.descanso_fin = form.descanso_fin.data
        turno.descripcion = form.descripcion.data
        
        db.session.commit()
        
        log_activity(f"Editado turno: {turno.nombre}")
        flash(f'Turno {turno.nombre} actualizado correctamente.', 'success')
        return redirect(url_for('turnos.listar_turnos', company_id=company_id))
        
    return render_template(
        'turnos/form_turno.html',
        company=company,
        form=form,
        turno=turno
    )

@turnos_bp.route('/turnos/<int:company_id>/eliminar/<int:turno_id>', methods=['POST'])
@login_required
def eliminar_turno(company_id, turno_id):
    """Elimina un tipo de turno."""
    # Verificar acceso a la empresa
    company = get_company_or_404(company_id)
    if not puede_ver_empresa(company_id):
        abort(403)
        
    # Obtener el turno o devolver 404
    turno = Turno.query.filter_by(id=turno_id, company_id=company_id).first_or_404()
    
    # Verificar si el turno está en uso
    num_usos = Horario.query.filter_by(turno_id=turno_id).count()
    if num_usos > 0:
        flash(f'No se puede eliminar el turno {turno.nombre} porque está asignado a {num_usos} horarios.', 'danger')
        return redirect(url_for('turnos.listar_turnos', company_id=company_id))
    
    # Eliminar el turno
    db.session.delete(turno)
    db.session.commit()
    
    log_activity(f"Eliminado turno: {turno.nombre}")
    flash(f'Turno {turno.nombre} eliminado correctamente.', 'success')
    return redirect(url_for('turnos.listar_turnos', company_id=company_id))

@turnos_bp.route('/horarios/<int:company_id>/asignar', methods=['GET', 'POST'])
@login_required
def asignar_horario(company_id):
    """Asigna un turno a un empleado en una fecha específica."""
    # Verificar acceso a la empresa
    company = get_company_or_404(company_id)
    if not puede_ver_empresa(company_id):
        abort(403)
        
    # Preparar el formulario
    form = HorarioForm()
    
    # Obtener todos los empleados activos de la empresa
    empleados = Employee.query.filter_by(company_id=company_id, is_active=True).order_by(Employee.nombre).all()
    form.employee_id.choices = [(e.id, f"{e.nombre} {e.apellidos}") for e in empleados]
    
    # Obtener todos los turnos activos de la empresa
    turnos = Turno.query.filter_by(company_id=company_id, is_active=True).order_by(Turno.nombre).all()
    form.turno_id.choices = [(t.id, t.nombre) for t in turnos]
    
    # Valores predeterminados para el formulario
    if request.method == 'GET':
        # Si se proporciona fecha en la URL, usar esa fecha
        fecha_param = request.args.get('fecha')
        if fecha_param:
            try:
                form.fecha.data = datetime.strptime(fecha_param, '%Y-%m-%d').date()
            except ValueError:
                form.fecha.data = date.today()
        else:
            form.fecha.data = date.today()
            
        # Si se proporciona empleado en la URL, seleccionarlo
        employee_id_param = request.args.get('employee_id')
        if employee_id_param and any(e.id == int(employee_id_param) for e in empleados):
            form.employee_id.data = int(employee_id_param)
    
    if form.validate_on_submit():
        # Verificar si ya existe un horario para este empleado en esta fecha
        horario_existente = Horario.query.filter_by(
            employee_id=form.employee_id.data,
            fecha=form.fecha.data
        ).first()
        
        if horario_existente:
            # Actualizar el horario existente
            horario_existente.turno_id = form.turno_id.data
            horario_existente.notas = form.notas.data
            db.session.commit()
            
            # Registrar el cambio en el historial
            historial = HistorialCambios(
                horario_id=horario_existente.id,
                user_id=current_user.id,
                tipo_cambio="modificacion",
                descripcion=f"Modificado turno de {horario_existente.employee.nombre} para el {form.fecha.data}"
            )
            db.session.add(historial)
            db.session.commit()
            
            log_activity(f"Modificado horario para empleado {horario_existente.employee.nombre} en fecha {form.fecha.data}")
            flash(f'Turno para {horario_existente.employee.nombre} actualizado correctamente.', 'success')
        else:
            # Crear un nuevo horario
            horario = Horario(
                employee_id=form.employee_id.data,
                turno_id=form.turno_id.data,
                fecha=form.fecha.data,
                notas=form.notas.data
            )
            db.session.add(horario)
            db.session.commit()
            
            # Obtener el empleado para el mensaje
            empleado = Employee.query.get(form.employee_id.data)
            
            # Registrar el cambio en el historial
            historial = HistorialCambios(
                horario_id=horario.id,
                user_id=current_user.id,
                tipo_cambio="creacion",
                descripcion=f"Asignado turno a {empleado.nombre} para el {form.fecha.data}"
            )
            db.session.add(historial)
            db.session.commit()
            
            log_activity(f"Asignado horario para empleado {empleado.nombre} en fecha {form.fecha.data}")
            flash(f'Turno para {empleado.nombre} asignado correctamente.', 'success')
        
        # Redireccionar a la vista de calendario
        return redirect(url_for('turnos.calendario', company_id=company_id, semana=form.fecha.data))
        
    return render_template(
        'turnos/form_horario.html',
        company=company,
        form=form
    )

@turnos_bp.route('/horarios/<int:company_id>/eliminar', methods=['POST'])
@login_required
def eliminar_horario(company_id):
    """Elimina un horario asignado."""
    # Verificar acceso a la empresa
    company = get_company_or_404(company_id)
    if not puede_ver_empresa(company_id):
        abort(403)
        
    form = EliminarHorarioForm()
    
    if form.validate_on_submit():
        horario_id = form.horario_id.data
        
        # Obtener el horario
        horario = Horario.query.get_or_404(horario_id)
        
        # Verificar que el horario pertenece a la empresa correcta
        if horario.turno.company_id != company_id:
            abort(403)
            
        # Guardar información para el mensaje
        empleado_nombre = horario.employee.nombre
        fecha = horario.fecha
        
        # Registrar el cambio en el historial antes de eliminar
        historial = HistorialCambios(
            horario_id=None,  # El horario ya no existirá
            user_id=current_user.id,
            tipo_cambio="eliminacion",
            descripcion=f"Eliminado turno de {empleado_nombre} para el {fecha}"
        )
        db.session.add(historial)
        
        # Eliminar el horario
        db.session.delete(horario)
        db.session.commit()
        
        log_activity(f"Eliminado horario para empleado {empleado_nombre} en fecha {fecha}")
        flash(f'Turno para {empleado_nombre} en fecha {fecha} eliminado correctamente.', 'success')
        
        # Redireccionar a la vista de calendario
        return redirect(url_for('turnos.calendario', company_id=company_id, semana=fecha))
    
    # Si hay un error en el formulario
    flash('Error al procesar la solicitud de eliminación.', 'danger')
    return redirect(url_for('turnos.calendario', company_id=company_id))

@turnos_bp.route('/api/turno/<int:turno_id>')
@login_required
def api_turno_detalle(turno_id):
    """API para obtener detalles de un turno."""
    turno = Turno.query.get_or_404(turno_id)
    
    # Verificar acceso a la empresa
    if not puede_ver_empresa(turno.company_id):
        abort(403)
        
    return jsonify({
        'id': turno.id,
        'nombre': turno.nombre,
        'tipo': turno.tipo.value,
        'hora_inicio': turno.hora_inicio.strftime('%H:%M'),
        'hora_fin': turno.hora_fin.strftime('%H:%M'),
        'color': turno.color,
        'horas_efectivas': turno.horas_efectivas
    })

@turnos_bp.route('/horarios/<int:company_id>/masivo', methods=['GET', 'POST'])
@login_required
def asignar_horario_masivo(company_id):
    """Asigna turnos a múltiples empleados o en un rango de fechas."""
    # Verificar acceso a la empresa
    company = get_company_or_404(company_id)
    if not puede_ver_empresa(company_id):
        abort(403)
        
    # Preparar el formulario
    form = AsignacionMasivaForm()
    
    # Obtener todos los empleados activos de la empresa
    empleados = Employee.query.filter_by(company_id=company_id, is_active=True).order_by(Employee.nombre).all()
    form.employees.choices = [(e.id, f"{e.nombre} {e.apellidos}") for e in empleados]
    
    # Obtener todos los turnos activos de la empresa
    turnos = Turno.query.filter_by(company_id=company_id, is_active=True).order_by(Turno.nombre).all()
    form.turno_id.choices = [(t.id, t.nombre) for t in turnos]
    
    # Valores predeterminados para el formulario
    if request.method == 'GET':
        form.fecha_inicio.data = date.today()
        form.fecha_fin.data = date.today() + timedelta(days=6)  # Una semana por defecto
        form.dias_semana.data = [0, 1, 2, 3, 4]  # L-V por defecto
    
    if form.validate_on_submit():
        # Obtener los datos del formulario
        fecha_inicio = form.fecha_inicio.data
        fecha_fin = form.fecha_fin.data
        dias_semana = form.dias_semana.data
        turno_id = form.turno_id.data
        employee_ids = form.employees.data
        notas = form.notas.data
        
        # Contador de horarios creados
        horarios_creados = 0
        horarios_actualizados = 0
        
        # Iterar por cada día en el rango
        fecha_actual = fecha_inicio
        while fecha_actual <= fecha_fin:
            # Verificar si el día de la semana está seleccionado
            if fecha_actual.weekday() in dias_semana:
                # Para cada empleado seleccionado
                for employee_id in employee_ids:
                    # Verificar si ya existe un horario
                    horario_existente = Horario.query.filter_by(
                        employee_id=employee_id,
                        fecha=fecha_actual
                    ).first()
                    
                    if horario_existente:
                        # Actualizar el horario existente
                        horario_existente.turno_id = turno_id
                        horario_existente.notas = notas
                        
                        # Registrar el cambio en el historial
                        historial = HistorialCambios(
                            horario_id=horario_existente.id,
                            user_id=current_user.id,
                            tipo_cambio="modificacion",
                            descripcion=f"Modificado turno en asignación masiva para {horario_existente.employee.nombre} - {fecha_actual}"
                        )
                        db.session.add(historial)
                        
                        horarios_actualizados += 1
                    else:
                        # Crear un nuevo horario
                        horario = Horario(
                            employee_id=employee_id,
                            turno_id=turno_id,
                            fecha=fecha_actual,
                            notas=notas
                        )
                        db.session.add(horario)
                        horarios_creados += 1
            
            # Avanzar al siguiente día
            fecha_actual += timedelta(days=1)
        
        # Guardar cambios en la base de datos
        db.session.commit()
        
        log_activity(f"Asignación masiva de horarios: {horarios_creados} creados, {horarios_actualizados} actualizados")
        flash(f'Asignación masiva completada: {horarios_creados} nuevos horarios creados y {horarios_actualizados} actualizados.', 'success')
        
        # Redireccionar a la vista de calendario
        return redirect(url_for('turnos.calendario', company_id=company_id, semana=fecha_inicio))
        
    return render_template(
        'turnos/form_horario_masivo.html',
        company=company,
        form=form
    )

@turnos_bp.route('/ausencias/<int:company_id>')
@login_required
def listar_ausencias(company_id):
    """Muestra la lista de ausencias para una empresa."""
    # Verificar acceso a la empresa
    company = get_company_or_404(company_id)
    if not puede_ver_empresa(company_id):
        abort(403)
        
    # Filtrar por tipo de ausencia
    tipo = request.args.get('tipo')
    # Filtrar por estado (aprobado/pendiente)
    estado = request.args.get('estado')
    # Filtrar por rango de fechas
    fecha_inicio = request.args.get('fecha_inicio')
    fecha_fin = request.args.get('fecha_fin')
    
    # Construir la consulta base
    query = (Ausencia.query
            .join(Employee)
            .filter(Employee.company_id == company_id))
    
    # Aplicar filtros
    if tipo:
        try:
            tipo_enum = TipoAusencia[tipo]
            query = query.filter(Ausencia.tipo == tipo_enum)
        except KeyError:
            pass
    
    if estado:
        if estado == 'aprobado':
            query = query.filter(Ausencia.aprobado == True)
        elif estado == 'pendiente':
            query = query.filter(Ausencia.aprobado == False)
    
    if fecha_inicio:
        try:
            fecha_inicio_dt = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
            query = query.filter(Ausencia.fecha_fin >= fecha_inicio_dt)
        except ValueError:
            pass
    
    if fecha_fin:
        try:
            fecha_fin_dt = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
            query = query.filter(Ausencia.fecha_inicio <= fecha_fin_dt)
        except ValueError:
            pass
    
    # Ordenar por fecha de inicio (más reciente primero)
    ausencias = query.order_by(Ausencia.fecha_inicio.desc()).all()
    
    return render_template(
        'turnos/listar_ausencias.html',
        company=company,
        ausencias=ausencias,
        tipos_ausencia=TipoAusencia
    )

@turnos_bp.route('/ausencias/<int:company_id>/nueva', methods=['GET', 'POST'])
@login_required
def nueva_ausencia(company_id):
    """Registra una nueva ausencia para un empleado."""
    # Verificar acceso a la empresa
    company = get_company_or_404(company_id)
    if not puede_ver_empresa(company_id):
        abort(403)
        
    # Preparar el formulario
    form = AusenciaForm()
    
    # Obtener todos los empleados activos de la empresa
    empleados = Employee.query.filter_by(company_id=company_id, is_active=True).order_by(Employee.nombre).all()
    form.employee_id.choices = [(e.id, f"{e.nombre} {e.apellidos}") for e in empleados]
    
    # Valores predeterminados para el formulario
    if request.method == 'GET':
        form.fecha_inicio.data = date.today()
        form.fecha_fin.data = date.today()
        
        # Si el usuario es admin o gerente, la ausencia se marca como aprobada por defecto
        if current_user.is_admin or current_user.role.name == 'gerente':
            form.aprobado.data = True
        
        # Si se proporciona empleado en la URL, seleccionarlo
        employee_id_param = request.args.get('employee_id')
        if employee_id_param and any(e.id == int(employee_id_param) for e in empleados):
            form.employee_id.data = int(employee_id_param)
    
    if form.validate_on_submit():
        # Convertir el tipo de enum de string a objeto TipoAusencia
        tipo_ausencia = TipoAusencia[form.tipo.data]
        
        # Crear la ausencia
        ausencia = Ausencia(
            employee_id=form.employee_id.data,
            fecha_inicio=form.fecha_inicio.data,
            fecha_fin=form.fecha_fin.data,
            tipo=tipo_ausencia,
            motivo=form.motivo.data,
            aprobado=form.aprobado.data
        )
        
        # Si está aprobada, registrar quién la aprobó
        if form.aprobado.data:
            ausencia.aprobado_por_id = current_user.id
        
        db.session.add(ausencia)
        db.session.commit()
        
        # Obtener el empleado para el mensaje
        empleado = Employee.query.get(form.employee_id.data)
        
        log_activity(f"Registrada ausencia para {empleado.nombre} del {form.fecha_inicio.data} al {form.fecha_fin.data}")
        flash(f'Ausencia para {empleado.nombre} registrada correctamente.', 'success')
        
        # Redireccionar a la lista de ausencias
        return redirect(url_for('turnos.listar_ausencias', company_id=company_id))
        
    return render_template(
        'turnos/form_ausencia.html',
        company=company,
        form=form,
        ausencia=None
    )

@turnos_bp.route('/ausencias/<int:company_id>/editar/<int:ausencia_id>', methods=['GET', 'POST'])
@login_required
def editar_ausencia(company_id, ausencia_id):
    """Edita una ausencia existente."""
    # Verificar acceso a la empresa
    company = get_company_or_404(company_id)
    if not puede_ver_empresa(company_id):
        abort(403)
        
    # Obtener la ausencia o devolver 404
    ausencia = Ausencia.query.join(Employee).filter(
        Ausencia.id == ausencia_id,
        Employee.company_id == company_id
    ).first_or_404()
    
    # Preparar el formulario
    form = AusenciaForm(obj=ausencia)
    
    # Obtener todos los empleados activos de la empresa
    empleados = Employee.query.filter_by(company_id=company_id, is_active=True).order_by(Employee.nombre).all()
    form.employee_id.choices = [(e.id, f"{e.nombre} {e.apellidos}") for e in empleados]
    
    # Asignar valor del enum al formulario (solo para GET)
    if request.method == 'GET':
        form.tipo.data = ausencia.tipo.name
    
    if form.validate_on_submit():
        # Convertir el tipo de enum de string a objeto TipoAusencia
        tipo_ausencia = TipoAusencia[form.tipo.data]
        
        # Actualizar los datos de la ausencia
        ausencia.employee_id = form.employee_id.data
        ausencia.fecha_inicio = form.fecha_inicio.data
        ausencia.fecha_fin = form.fecha_fin.data
        ausencia.tipo = tipo_ausencia
        ausencia.motivo = form.motivo.data
        
        # Si el estado de aprobación ha cambiado
        if ausencia.aprobado != form.aprobado.data:
            ausencia.aprobado = form.aprobado.data
            
            # Si ahora está aprobada, registrar quién la aprobó
            if form.aprobado.data:
                ausencia.aprobado_por_id = current_user.id
            else:
                ausencia.aprobado_por_id = None
        
        db.session.commit()
        
        log_activity(f"Editada ausencia para {ausencia.employee.nombre} del {ausencia.fecha_inicio} al {ausencia.fecha_fin}")
        flash(f'Ausencia para {ausencia.employee.nombre} actualizada correctamente.', 'success')
        
        # Redireccionar a la lista de ausencias
        return redirect(url_for('turnos.listar_ausencias', company_id=company_id))
        
    return render_template(
        'turnos/form_ausencia.html',
        company=company,
        form=form,
        ausencia=ausencia
    )

@turnos_bp.route('/ausencias/<int:company_id>/eliminar/<int:ausencia_id>', methods=['POST'])
@login_required
def eliminar_ausencia(company_id, ausencia_id):
    """Elimina una ausencia."""
    # Verificar acceso a la empresa
    company = get_company_or_404(company_id)
    if not puede_ver_empresa(company_id):
        abort(403)
        
    # Obtener la ausencia o devolver 404
    ausencia = Ausencia.query.join(Employee).filter(
        Ausencia.id == ausencia_id,
        Employee.company_id == company_id
    ).first_or_404()
    
    # Guardar información para el mensaje
    empleado_nombre = ausencia.employee.nombre
    fecha_inicio = ausencia.fecha_inicio
    fecha_fin = ausencia.fecha_fin
    
    # Eliminar la ausencia
    db.session.delete(ausencia)
    db.session.commit()
    
    log_activity(f"Eliminada ausencia para {empleado_nombre} del {fecha_inicio} al {fecha_fin}")
    flash(f'Ausencia para {empleado_nombre} eliminada correctamente.', 'success')
    
    # Redireccionar a la lista de ausencias
    return redirect(url_for('turnos.listar_ausencias', company_id=company_id))

@turnos_bp.route('/ausencias/<int:company_id>/aprobar/<int:ausencia_id>', methods=['POST'])
@login_required
def aprobar_ausencia(company_id, ausencia_id):
    """Aprueba una ausencia pendiente."""
    # Verificar acceso a la empresa
    company = get_company_or_404(company_id)
    if not puede_ver_empresa(company_id):
        abort(403)
        
    # Verificar que el usuario tiene permisos para aprobar (admin o gerente)
    if not (current_user.is_admin or current_user.role.name == 'gerente'):
        abort(403)
        
    # Obtener la ausencia o devolver 404
    ausencia = Ausencia.query.join(Employee).filter(
        Ausencia.id == ausencia_id,
        Employee.company_id == company_id,
        Ausencia.aprobado == False
    ).first_or_404()
    
    # Aprobar la ausencia
    ausencia.aprobado = True
    ausencia.aprobado_por_id = current_user.id
    db.session.commit()
    
    log_activity(f"Aprobada ausencia para {ausencia.employee.nombre} del {ausencia.fecha_inicio} al {ausencia.fecha_fin}")
    flash(f'Ausencia para {ausencia.employee.nombre} aprobada correctamente.', 'success')
    
    # Redireccionar a la lista de ausencias
    return redirect(url_for('turnos.listar_ausencias', company_id=company_id))

@turnos_bp.route('/informes/<int:company_id>')
@login_required
def informes(company_id):
    """Muestra la página de informes de turnos."""
    # Verificar acceso a la empresa
    company = get_company_or_404(company_id)
    if not puede_ver_empresa(company_id):
        abort(403)
        
    return render_template(
        'turnos/informes.html',
        company=company
    )

@turnos_bp.route('/informes/<int:company_id>/horarios')
@login_required
def informe_horarios(company_id):
    """Genera un informe de horarios para un período específico."""
    # Verificar acceso a la empresa
    company = get_company_or_404(company_id)
    if not puede_ver_empresa(company_id):
        abort(403)
        
    # Obtener parámetros de fechas
    fecha_inicio_str = request.args.get('fecha_inicio')
    fecha_fin_str = request.args.get('fecha_fin')
    
    try:
        fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
        fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        # Si no se proporcionan fechas válidas, usar la semana actual
        fecha_inicio, fecha_fin = get_rango_semana(date.today())
    
    # Limitar el rango a 31 días por rendimiento
    if (fecha_fin - fecha_inicio).days > 31:
        fecha_fin = fecha_inicio + timedelta(days=31)
    
    # Obtener horarios para el período
    horarios = (Horario.query
               .join(Turno)
               .join(Employee)
               .filter(
                   Turno.company_id == company_id,
                   Horario.fecha.between(fecha_inicio, fecha_fin),
                   Employee.is_active == True
               )
               .order_by(Employee.nombre, Horario.fecha)
               .all())
    
    # Obtener ausencias para el período
    ausencias = (Ausencia.query
                .join(Employee)
                .filter(
                    Employee.company_id == company_id,
                    Employee.is_active == True,
                    or_(
                        and_(Ausencia.fecha_inicio <= fecha_fin, Ausencia.fecha_fin >= fecha_inicio)
                    )
                )
                .all())
    
    # Formato solicitado: excel o pdf
    formato = request.args.get('formato', 'web')
    
    if formato == 'excel':
        return generar_excel_horarios(company, horarios, ausencias, fecha_inicio, fecha_fin)
    elif formato == 'pdf':
        return generar_pdf_horarios(company, horarios, ausencias, fecha_inicio, fecha_fin)
    else:
        # Vista web por defecto
        return render_template(
            'turnos/informe_horarios.html',
            company=company,
            horarios=horarios,
            ausencias=ausencias,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin
        )

def generar_excel_horarios(company, horarios, ausencias, fecha_inicio, fecha_fin):
    """Genera un informe en formato Excel de los horarios."""
    # Crear un nuevo libro de Excel
    wb = Workbook()
    ws = wb.active
    ws.title = "Horarios"
    
    # Configurar estilos
    header_font = Font(bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    
    # Añadir título
    ws.cell(1, 1).value = f"Informe de Horarios - {company.name}"
    ws.cell(1, 1).font = Font(bold=True, size=14)
    ws.merge_cells('A1:H1')
    ws.cell(1, 1).alignment = Alignment(horizontal="center")
    
    # Añadir período del informe
    ws.cell(2, 1).value = f"Período: {fecha_inicio.strftime('%d/%m/%Y')} - {fecha_fin.strftime('%d/%m/%Y')}"
    ws.merge_cells('A2:H2')
    ws.cell(2, 1).alignment = Alignment(horizontal="center")
    
    # Añadir encabezados de columnas
    headers = ["Empleado", "Fecha", "Día", "Turno", "Horario", "Horas", "Tipo", "Notas"]
    for i, header in enumerate(headers, 1):
        cell = ws.cell(4, i)
        cell.value = header
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center")
    
    # Añadir datos de horarios
    row = 5
    for horario in horarios:
        # Empleado
        ws.cell(row, 1).value = f"{horario.employee.nombre} {horario.employee.apellidos}"
        
        # Fecha
        ws.cell(row, 2).value = horario.fecha.strftime('%d/%m/%Y')
        ws.cell(row, 2).alignment = Alignment(horizontal="center")
        
        # Día de la semana
        dia_semana = horario.fecha.weekday()
        dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        ws.cell(row, 3).value = dias[dia_semana]
        
        # Turno
        ws.cell(row, 4).value = horario.turno.nombre
        
        # Horario
        ws.cell(row, 5).value = f"{horario.turno.hora_inicio.strftime('%H:%M')} - {horario.turno.hora_fin.strftime('%H:%M')}"
        ws.cell(row, 5).alignment = Alignment(horizontal="center")
        
        # Horas efectivas
        ws.cell(row, 6).value = horario.turno.horas_efectivas
        ws.cell(row, 6).alignment = Alignment(horizontal="center")
        
        # Tipo de turno
        ws.cell(row, 7).value = horario.turno.tipo.value
        
        # Notas
        ws.cell(row, 8).value = horario.notas
        
        row += 1
    
    # Ajustar ancho de columnas automáticamente
    for i in range(1, 9):
        column_letter = chr(64 + i)  # A, B, C, ...
        ws.column_dimensions[column_letter].width = 15
    
    # Añadir una hoja para ausencias si hay alguna
    if ausencias:
        ws_ausencias = wb.create_sheet(title="Ausencias")
        
        # Añadir título
        ws_ausencias.cell(1, 1).value = f"Informe de Ausencias - {company.name}"
        ws_ausencias.cell(1, 1).font = Font(bold=True, size=14)
        ws_ausencias.merge_cells('A1:F1')
        ws_ausencias.cell(1, 1).alignment = Alignment(horizontal="center")
        
        # Añadir período del informe
        ws_ausencias.cell(2, 1).value = f"Período: {fecha_inicio.strftime('%d/%m/%Y')} - {fecha_fin.strftime('%d/%m/%Y')}"
        ws_ausencias.merge_cells('A2:F2')
        ws_ausencias.cell(2, 1).alignment = Alignment(horizontal="center")
        
        # Añadir encabezados de columnas
        headers = ["Empleado", "Tipo", "Inicio", "Fin", "Días", "Motivo"]
        for i, header in enumerate(headers, 1):
            cell = ws_ausencias.cell(4, i)
            cell.value = header
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal="center")
        
        # Añadir datos de ausencias
        row = 5
        for ausencia in ausencias:
            # Empleado
            ws_ausencias.cell(row, 1).value = f"{ausencia.employee.nombre} {ausencia.employee.apellidos}"
            
            # Tipo de ausencia
            ws_ausencias.cell(row, 2).value = ausencia.tipo.value
            
            # Fecha inicio
            ws_ausencias.cell(row, 3).value = ausencia.fecha_inicio.strftime('%d/%m/%Y')
            ws_ausencias.cell(row, 3).alignment = Alignment(horizontal="center")
            
            # Fecha fin
            ws_ausencias.cell(row, 4).value = ausencia.fecha_fin.strftime('%d/%m/%Y')
            ws_ausencias.cell(row, 4).alignment = Alignment(horizontal="center")
            
            # Días totales
            ws_ausencias.cell(row, 5).value = ausencia.dias_totales
            ws_ausencias.cell(row, 5).alignment = Alignment(horizontal="center")
            
            # Motivo
            ws_ausencias.cell(row, 6).value = ausencia.motivo
            
            row += 1
        
        # Ajustar ancho de columnas automáticamente
        for i in range(1, 7):
            column_letter = chr(64 + i)  # A, B, C, ...
            ws_ausencias.column_dimensions[column_letter].width = 15
    
    # Guardar el archivo en memoria
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    
    # Configurar la respuesta
    filename = f"horarios_{company.name}_{fecha_inicio.strftime('%Y%m%d')}_{fecha_fin.strftime('%Y%m%d')}.xlsx"
    return send_file(
        output,
        as_attachment=True,
        download_name=filename,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

def generar_pdf_horarios(company, horarios, ausencias, fecha_inicio, fecha_fin):
    """Genera un informe en formato PDF de los horarios."""
    from fpdf import FPDF
    
    # Crear un nuevo documento PDF
    pdf = FPDF()
    pdf.add_page()
    
    # Configurar fuentes
    pdf.set_font("Arial", 'B', 16)
    
    # Añadir título
    pdf.cell(0, 10, f"Informe de Horarios - {company.name}", 0, 1, 'C')
    
    # Añadir período del informe
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, f"Período: {fecha_inicio.strftime('%d/%m/%Y')} - {fecha_fin.strftime('%d/%m/%Y')}", 0, 1, 'C')
    
    # Añadir tabla de horarios
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Horarios", 0, 1, 'L')
    
    # Definir anchos de columnas
    col_widths = [50, 25, 25, 40, 30, 15]
    
    # Encabezados de la tabla
    headers = ["Empleado", "Fecha", "Turno", "Horario", "Tipo", "Horas"]
    pdf.set_fill_color(70, 114, 196)  # Azul para encabezados
    pdf.set_text_color(255, 255, 255)  # Texto blanco
    
    for i, header in enumerate(headers):
        pdf.cell(col_widths[i], 10, header, 1, 0, 'C', True)
    pdf.ln()
    
    # Datos de la tabla
    pdf.set_font("Arial", '', 10)
    pdf.set_text_color(0, 0, 0)  # Texto negro
    
    # Agrupar horarios por empleado
    horarios_por_empleado = {}
    for horario in horarios:
        employee_id = horario.employee_id
        if employee_id not in horarios_por_empleado:
            horarios_por_empleado[employee_id] = []
        horarios_por_empleado[employee_id].append(horario)
    
    # Añadir datos agrupados por empleado
    for employee_id, horarios_empleado in horarios_por_empleado.items():
        # Ordenar horarios por fecha
        horarios_empleado.sort(key=lambda h: h.fecha)
        
        # Obtener información del empleado
        empleado = horarios_empleado[0].employee
        
        # Alternar colores de fondo para filas
        fill = False
        
        for horario in horarios_empleado:
            # Si es una nueva página, añadir encabezados nuevamente
            if pdf.get_y() > 270:
                pdf.add_page()
                pdf.set_font("Arial", 'B', 12)
                pdf.set_fill_color(70, 114, 196)
                pdf.set_text_color(255, 255, 255)
                
                for i, header in enumerate(headers):
                    pdf.cell(col_widths[i], 10, header, 1, 0, 'C', True)
                pdf.ln()
                
                pdf.set_font("Arial", '', 10)
                pdf.set_text_color(0, 0, 0)
            
            # Establecer color de fondo para filas alternas
            if fill:
                pdf.set_fill_color(240, 240, 240)  # Gris claro
            else:
                pdf.set_fill_color(255, 255, 255)  # Blanco
            
            # Empleado
            pdf.cell(col_widths[0], 10, f"{empleado.nombre} {empleado.apellidos}", 1, 0, 'L', fill)
            
            # Fecha
            pdf.cell(col_widths[1], 10, horario.fecha.strftime('%d/%m/%Y'), 1, 0, 'C', fill)
            
            # Turno
            pdf.cell(col_widths[2], 10, horario.turno.nombre, 1, 0, 'L', fill)
            
            # Horario
            pdf.cell(col_widths[3], 10, f"{horario.turno.hora_inicio.strftime('%H:%M')} - {horario.turno.hora_fin.strftime('%H:%M')}", 1, 0, 'C', fill)
            
            # Tipo
            pdf.cell(col_widths[4], 10, horario.turno.tipo.value, 1, 0, 'L', fill)
            
            # Horas
            pdf.cell(col_widths[5], 10, str(horario.turno.horas_efectivas), 1, 1, 'C', fill)
            
            # Alternar el valor de fill
            fill = not fill
    
    # Añadir tabla de ausencias si hay alguna
    if ausencias:
        pdf.add_page()
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "Ausencias", 0, 1, 'L')
        
        # Definir anchos de columnas para ausencias
        col_widths_ausencias = [50, 30, 25, 25, 15, 45]
        
        # Encabezados de la tabla
        headers = ["Empleado", "Tipo", "Inicio", "Fin", "Días", "Motivo"]
        pdf.set_fill_color(70, 114, 196)  # Azul para encabezados
        pdf.set_text_color(255, 255, 255)  # Texto blanco
        
        for i, header in enumerate(headers):
            pdf.cell(col_widths_ausencias[i], 10, header, 1, 0, 'C', True)
        pdf.ln()
        
        # Datos de la tabla
        pdf.set_font("Arial", '', 10)
        pdf.set_text_color(0, 0, 0)  # Texto negro
        
        # Agrupar ausencias por empleado
        ausencias_por_empleado = {}
        for ausencia in ausencias:
            employee_id = ausencia.employee_id
            if employee_id not in ausencias_por_empleado:
                ausencias_por_empleado[employee_id] = []
            ausencias_por_empleado[employee_id].append(ausencia)
        
        # Añadir datos agrupados por empleado
        for employee_id, ausencias_empleado in ausencias_por_empleado.items():
            # Ordenar ausencias por fecha de inicio
            ausencias_empleado.sort(key=lambda a: a.fecha_inicio)
            
            # Obtener información del empleado
            empleado = ausencias_empleado[0].employee
            
            # Alternar colores de fondo para filas
            fill = False
            
            for ausencia in ausencias_empleado:
                # Si es una nueva página, añadir encabezados nuevamente
                if pdf.get_y() > 270:
                    pdf.add_page()
                    pdf.set_font("Arial", 'B', 12)
                    pdf.set_fill_color(70, 114, 196)
                    pdf.set_text_color(255, 255, 255)
                    
                    for i, header in enumerate(headers):
                        pdf.cell(col_widths_ausencias[i], 10, header, 1, 0, 'C', True)
                    pdf.ln()
                    
                    pdf.set_font("Arial", '', 10)
                    pdf.set_text_color(0, 0, 0)
                
                # Establecer color de fondo para filas alternas
                if fill:
                    pdf.set_fill_color(240, 240, 240)  # Gris claro
                else:
                    pdf.set_fill_color(255, 255, 255)  # Blanco
                
                # Empleado
                pdf.cell(col_widths_ausencias[0], 10, f"{empleado.nombre} {empleado.apellidos}", 1, 0, 'L', fill)
                
                # Tipo
                pdf.cell(col_widths_ausencias[1], 10, ausencia.tipo.value, 1, 0, 'L', fill)
                
                # Inicio
                pdf.cell(col_widths_ausencias[2], 10, ausencia.fecha_inicio.strftime('%d/%m/%Y'), 1, 0, 'C', fill)
                
                # Fin
                pdf.cell(col_widths_ausencias[3], 10, ausencia.fecha_fin.strftime('%d/%m/%Y'), 1, 0, 'C', fill)
                
                # Días
                pdf.cell(col_widths_ausencias[4], 10, str(ausencia.dias_totales), 1, 0, 'C', fill)
                
                # Motivo (truncado si es muy largo)
                motivo = ausencia.motivo[:20] + "..." if ausencia.motivo and len(ausencia.motivo) > 20 else ausencia.motivo
                pdf.cell(col_widths_ausencias[5], 10, motivo or "", 1, 1, 'L', fill)
                
                # Alternar el valor de fill
                fill = not fill
    
    # Añadir pie de página con fecha de generación
    pdf.set_y(-15)
    pdf.set_font("Arial", 'I', 8)
    pdf.cell(0, 10, f"Generado el {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", 0, 0, 'C')
    
    # Generar el archivo PDF en memoria
    pdf_output = pdf.output(dest='S').encode('latin1')
    
    # Configurar la respuesta
    filename = f"horarios_{company.name}_{fecha_inicio.strftime('%Y%m%d')}_{fecha_fin.strftime('%Y%m%d')}.pdf"
    return send_file(
        io.BytesIO(pdf_output),
        as_attachment=True,
        download_name=filename,
        mimetype='application/pdf'
    )