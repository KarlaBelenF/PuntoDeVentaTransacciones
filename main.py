import sys
import requests
from PySide6.QtWidgets import QApplication, QTableWidgetItem, QMessageBox
from PySide6.QtUiTools import QUiLoader

def calcular_totales():
    total = 0.0
    for i in range(ventana.tabla_productos.rowCount()):
        item_importe = ventana.tabla_productos.item(i, 4)
        if item_importe and item_importe.text().strip(): 
            total += float(item_importe.text())
    
    iva = total * 0.16
    subtotal = total - iva
    
    ventana.text_subtotal.setText(f"${subtotal:.2f}")
    ventana.txt_IVA.setText(f"${iva:.2f}")
    ventana.txt_total.setText(f"${total:.2f}")

def agregar_producto():
    codigo = ventana.txt_codigo.text()
    if not codigo:
        return
        
    try:
        respuesta = requests.get(f"http://127.0.0.1:8000/productos/{codigo}", timeout=3)
        
        if respuesta.status_code == 200:
            producto = respuesta.json() 
            id_producto = str(producto['id'])
            stock_disponible = int(producto['stock'])
            
            for i in range(ventana.tabla_productos.rowCount()):
                celda_clave = ventana.tabla_productos.item(i, 0)
                if celda_clave and celda_clave.text() == id_producto:
                    cant_actual = int(ventana.tabla_productos.item(i, 2).text())
                    
                    # Freno de stock si ya está en el carrito
                    if cant_actual >= stock_disponible:
                        QMessageBox.warning(ventana, "Límite de stock", f"Solo tienes {stock_disponible} unidades de {producto['descripcion']}.")
                        ventana.txt_codigo.clear()
                        return
                        
                    nueva_cant = cant_actual + 1
                    nuevo_importe = nueva_cant * float(producto['precio'])
                    
                    ventana.tabla_productos.item(i, 2).setText(str(nueva_cant))
                    ventana.tabla_productos.item(i, 4).setText(str(nuevo_importe))
                    
                    calcular_totales()
                    ventana.txt_codigo.clear()
                    return 
            
            if stock_disponible < 1:
                QMessageBox.warning(ventana, "Agotado", f"El producto {producto['descripcion']} está agotado.")
                ventana.txt_codigo.clear()
                return

            # 2. Si no existe en la tabla y sí hay stock, creamos la fila nueva
            fila = ventana.tabla_productos.rowCount()
            ventana.tabla_productos.insertRow(fila)
            
            ventana.tabla_productos.setItem(fila, 0, QTableWidgetItem(id_producto))
            ventana.tabla_productos.setItem(fila, 1, QTableWidgetItem(producto['descripcion']))
            ventana.tabla_productos.setItem(fila, 2, QTableWidgetItem("1"))
            ventana.tabla_productos.setItem(fila, 3, QTableWidgetItem(str(producto['precio'])))
            ventana.tabla_productos.setItem(fila, 4, QTableWidgetItem(str(producto['precio'])))
            
            calcular_totales()
        else:
            QMessageBox.warning(ventana, "Error de búsqueda", "Producto no encontrado en la base de datos.")
            
    except requests.exceptions.RequestException:
        QMessageBox.critical(ventana, "Falla de conexión", "Conexión fallida. Revisa si el backend de Belén está corriendo y no está pausado.")
        
    ventana.txt_codigo.clear()

def guardar_venta():
    if ventana.tabla_productos.rowCount() == 0:
        QMessageBox.warning(ventana, "Carrito vacío", "El carrito está vacío, no hay artículos para cobrar.")
        return

    try:
        # Quitamos el "$" para mandar números puros
        subtotal = float(ventana.text_subtotal.text().replace('$', ''))
        iva = float(ventana.txt_IVA.text().replace('$', ''))
        total = float(ventana.txt_total.text().replace('$', ''))
        
        detalles = []
        for i in range(ventana.tabla_productos.rowCount()):
            celda_id = ventana.tabla_productos.item(i, 0)
            if not celda_id: continue
            
            detalles.append({
                "producto_id": int(celda_id.text()),
                "cantidad": int(ventana.tabla_productos.item(i, 2).text()),
                "precio_unitario": float(ventana.tabla_productos.item(i, 3).text()),
                "importe": float(ventana.tabla_productos.item(i, 4).text())
            })
            
        venta_data = {
            "subtotal": subtotal,
            "iva": iva,
            "total": total,
            "detalles": detalles
        }
        
        # Mandamos a la API 
        respuesta = requests.post("http://127.0.0.1:8000/ventas/", json=venta_data, timeout=3)
        
        if respuesta.status_code == 200:
            QMessageBox.information(ventana, "Venta Exitosa", f"¡Venta guardada con éxito! Folio: {respuesta.json()['folio']}")
            ventana.tabla_productos.setRowCount(0)
            ventana.text_subtotal.setText("$0.00")
            ventana.txt_IVA.setText("$0.00")
            ventana.txt_total.setText("$0.00")
        else:
            QMessageBox.critical(ventana, "Error al guardar", f"Error del servidor: {respuesta.json()}")
            
    except requests.exceptions.RequestException:
        QMessageBox.critical(ventana, "Falla de red", "Error de conexión al intentar guardar. Verifica el backend.")
    except Exception as e:
        QMessageBox.critical(ventana, "Error interno", f"Error interno en la aplicación: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    loader = QUiLoader()
    ventana = loader.load("pantalla.ui", None)
    
    ventana.text_subtotal.setReadOnly(True)
    ventana.txt_IVA.setReadOnly(True)
    ventana.txt_total.setReadOnly(True)
    
    ventana.btn_guardar_venta.clicked.connect(guardar_venta)
    ventana.txt_codigo.returnPressed.connect(agregar_producto)
    
    ventana.show()
    sys.exit(app.exec())