from app.database import Base, engine
from app.models.user import User
Base.metadata.create_all(bind=engine)

print("Base de datos inicializada y tablas creadas correctamente")  