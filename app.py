import os
import logging
from datetime import datetime

from flask import Flask, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
from sqlalchemy.orm import DeclarativeBase

# Configure logging (ya configurado en config.py)
logger = logging.getLogger(__name__)

# Initialize SQLAlchemy base class
class Base(DeclarativeBase):
    pass

# Initialize extensions
db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()
csrf = CSRFProtect()
migrate = Migrate()

def create_app(config_class='config.Config'):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    # Temporarily disable CSRF for debugging
    app.config['WTF_CSRF_ENABLED'] = False
    csrf.init_app(app)
    migrate.init_app(app, db)
    
    # Configure login
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor, inicie sesión para acceder a esta página.'
    login_manager.login_message_category = 'warning'
    
    # Import models to ensure they're registered with SQLAlchemy
    with app.app_context():
        from models import (User, Company, Employee, ActivityLog, EmployeeDocument,
                           EmployeeNote, EmployeeHistory, EmployeeSchedule, 
                           EmployeeCheckIn, EmployeeVacation)
        # Import task models
        from models_tasks import (Location, LocalUser, Task, TaskSchedule, TaskCompletion, 
                                TaskPriority, TaskFrequency, TaskStatus, WeekDay)
        
        # Create admin user if it doesn't exist
        from utils import create_admin_user
        create_admin_user()
    
    # Register blueprints
    from routes import (auth_bp, main_bp, company_bp, employee_bp, user_bp, 
                       schedule_bp, checkin_bp, vacation_bp)
    from routes_tasks import tasks_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(company_bp)
    app.register_blueprint(employee_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(schedule_bp)
    app.register_blueprint(checkin_bp)
    app.register_blueprint(vacation_bp)
    app.register_blueprint(tasks_bp, url_prefix='/tasks')
    
    # Register error handlers
    @app.errorhandler(403)
    def forbidden_page(error):
        return render_template('errors/403.html'), 403
        
    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('errors/404.html'), 404
        
    @app.errorhandler(500)
    def server_error_page(error):
        return render_template('errors/500.html'), 500
    
    # Log activity middleware (optimizado para reducir DB commits)
    # Usar before_request y after_request para solo hacer commit después de la solicitud
    activity_log_added = False
    
    @app.before_request
    def log_activity():
        # Ignorar solicitudes estáticas y de monitoreo frecuentes
        if (request.path.startswith('/static') or 
            request.path == '/favicon.ico' or 
            request.path == '/health'):
            return  # Skip logging
            
        if current_user.is_authenticated:
            from models import ActivityLog
            
            # Solo registrar acciones interesantes (no GETs a páginas comunes)
            if request.method != 'GET' or not request.path.startswith(('/dashboard', '/employees')):
                nonlocal activity_log_added
                log_entry = ActivityLog(
                    user_id=current_user.id,
                    action=f"{request.method} {request.path}",
                    ip_address=request.remote_addr,
                    timestamp=datetime.utcnow()
                )
                db.session.add(log_entry)
                activity_log_added = True
    
    @app.after_request
    def commit_logs(response):
        nonlocal activity_log_added
        # Solo hacer commit si se agregó un log y no hubo errores
        if activity_log_added and response.status_code < 400:
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                logger.warning(f"Error al guardar log de actividad: {e}")
            finally:
                activity_log_added = False
        return response
    
    # Initialize app config
    from config import Config
    Config.init_app(app)
    
    return app

# Import these here to avoid circular imports
from flask import render_template
from flask_login import current_user

# Create the application instance
app = create_app()
