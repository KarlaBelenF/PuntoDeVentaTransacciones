from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:Mamarremamarrexd@localhost:3306/punto_venta" # sqlalchemy es el ORM que nos permite interactuar con la base de datos de manera más sencilla y estructurada. pymysql es el driver que permite a SQLAlchemy conectarse a MySQL.

engine = create_engine(SQLALCHEMY_DATABASE_URL) # Crea el motor de la base de datos, que es responsable de gestionar las conexiones y ejecutar las consultas SQL.
# Crea una clase de sesión que se utilizará para interactuar con la base de datos.
# autocommit=False significa que las transacciones no se confirmarán automáticamente
# autoflush=False significa que los cambios no se enviarán automáticamente a la base de datos hasta que se confirme la transacción
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base() # Crea la clase base para las clases de modelo SQLAlchemy

def get_db(): # Generador que proporciona una sesión de base de datos a las rutas de FastAPI. Se utiliza con Depends para inyectar la sesión en las funciones de ruta.
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()