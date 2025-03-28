"""Add bank_account column to companies and adjust phone length

Revision ID: 6a9d8f1a6e1d
Revises: 
Create Date: 2025-03-28 07:45:21.654321

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6a9d8f1a6e1d'
down_revision = None  # se ajustará automáticamente si ya existen migraciones
branch_labels = None
depends_on = None


def upgrade():
    # Añadir columna bank_account a la tabla companies
    op.add_column('companies', sa.Column('bank_account', sa.String(24), nullable=True))
    
    # Cambiar el tamaño de la columna phone de 32 a 13 caracteres
    # Primero obtener el tipo de dato existente para preservar el resto de propiedades
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = inspector.get_columns('companies')
    column_info = next((c for c in columns if c['name'] == 'phone'), None)
    
    if column_info:
        # Solo actualizamos si la columna existe y tiene un tamaño diferente
        existing_type = column_info.get('type', None)
        if existing_type and hasattr(existing_type, 'length') and existing_type.length != 13:
            op.alter_column('companies', 'phone',
                           existing_type=sa.String(existing_type.length),
                           type_=sa.String(13),
                           existing_nullable=True)


def downgrade():
    # Eliminar la columna bank_account de la tabla companies
    op.drop_column('companies', 'bank_account')
    
    # Restaurar el tamaño de la columna phone a 32 caracteres
    op.alter_column('companies', 'phone',
                   existing_type=sa.String(13),
                   type_=sa.String(32),
                   existing_nullable=True)