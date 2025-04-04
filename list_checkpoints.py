from app import create_app, db
from models_checkpoints import CheckPoint

app = create_app()

with app.app_context():
    checkpoints = CheckPoint.query.all()
    print(f'Total puntos de fichaje: {len(checkpoints)}')
    for cp in checkpoints:
        print(f'{cp.id}. {cp.name} ({cp.company.name})')