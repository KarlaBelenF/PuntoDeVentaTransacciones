from pydantic import BaseModel
from typing import List, Optional
# Define los esquemas de datos que se utilizarán para validar y serializar la información que se envía y recibe a través de la API.
# Los esquemas son clases que heredan de BaseModel de Pydantic, lo que permite definir los campos y sus tipos de datos, así como realizar validaciones automáticas.

class DetalleVentaCreate(BaseModel):
    producto_id: int
    cantidad: int
    precio_unitario: float
    importe: float

class VentaCreate(BaseModel):
    subtotal: float
    iva: float
    total: float
    detalles: List[DetalleVentaCreate]