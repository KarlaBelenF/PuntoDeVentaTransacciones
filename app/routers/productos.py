from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from ..database import get_db

# Crea un enrutador de FastAPI para manejar las rutas relacionadas con productos. 
# El prefijo "/productos" se añadirá a todas las rutas definidas en este enrutador
# Las rutas estarán etiquetadas con "Productos" para la documentación automática
router = APIRouter(prefix="/productos", tags=["Productos"])
@router.get("/{codigo}") # Define una ruta GET que recibe un código de producto como parámetro de la URL.
def buscar_producto(codigo: str, db: Session = Depends(get_db)): #depends(get_db) inyecta la sesión de base de datos en la función, lo que permite interactuar con la base de datos dentro de la ruta.
    resultado = db.execute( # Ejecuta una consulta SQL para buscar un producto por su código en la base de datos.
        text("SELECT id, codigo, descripcion, precio, stock FROM productos WHERE codigo = :cod"), #:cod es un marcador de posición para el parámetro que se pasará a la consulta.
        {"cod": codigo}
    ).fetchone() #fetchone() obtiene la primera fila del resultado de la consulta
    if not resultado:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
        
    return {
        "id": resultado[0],
        "codigo": resultado[1], 
        "descripcion": resultado[2], 
        "precio": resultado[3], 
        "stock": resultado[4]
    }