"""
Modelos de datos para la API.
"""
from datetime import datetime, date
from app import db


class APITask(db.Model):
    """
    Modelo de datos para las tareas de la API.
    """
    __tablename__ = 'api_tasks'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text)
    priority = db.Column(db.String(20), default='media')
    frequency = db.Column(db.String(20), default='diaria')
    status = db.Column(db.String(20), default='pendiente')
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        """Representación del modelo"""
        return f'<Task {self.id}: {self.title}>'
    
    def to_dict(self):
        """
        Convierte el modelo a un diccionario para la serialización JSON.
        Las fechas se formatean como cadenas ISO 8601.
        """
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'priority': self.priority,
            'frequency': self.frequency,
            'status': self.status,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }