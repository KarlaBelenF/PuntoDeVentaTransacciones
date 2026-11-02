from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from ..database import get_db
from .. import schemas

router = APIRouter(prefix="/ventas", tags=["Ventas"])

@router.post("/")
def guardar_venta(venta_data: schemas.VentaCreate, db: Session = Depends(get_db)): 
    try:
        db.execute(text("SET SESSION TRANSACTION ISOLATION LEVEL SERIALIZABLE;"))
        db.execute(text("START TRANSACTION;"))

        resultado = db.execute(
            text("INSERT INTO ventas (subtotal, iva, total) VALUES (:sub, :iva, :tot)"),
            {"sub": venta_data.subtotal, "iva": venta_data.iva, "tot": venta_data.total}
        )
        venta_id = resultado.lastrowid 

        for det in venta_data.detalles:
            stock_actual = db.execute(
                text("SELECT stock FROM productos WHERE id = :p_id"),
                {"p_id": det.producto_id}
            ).scalar() # scalar() obtiene el primer valor de la primera fila del resultado de la consulta, que en este caso es el stock actual del producto.

            if stock_actual is None:
                raise Exception(f"El producto con ID {det.producto_id} no existe.")
            
            if stock_actual < det.cantidad:
                raise Exception(f"Stock insuficiente para el producto ID {det.producto_id}. Disponible: {stock_actual}")

            db.execute(
                text("INSERT INTO detalles_venta (venta_id, producto_id, cantidad, precio_unitario, importe) VALUES (:v_id, :p_id, :cant, :pre, :imp)"),
                {"v_id": venta_id, "p_id": det.producto_id, "cant": det.cantidad, "pre": det.precio_unitario, "imp": det.importe}
            )
            db.execute(
                text("UPDATE productos SET stock = stock - :cant WHERE id = :p_id"),
                {"cant": det.cantidad, "p_id": det.producto_id}
            )

        db.execute(text("COMMIT;"))
        return {"mensaje": "Venta guardada exitosamente", "folio": venta_id}

    except Exception as e:
        db.execute(text("ROLLBACK;"))
        raise HTTPException(status_code=400, detail=str(e))