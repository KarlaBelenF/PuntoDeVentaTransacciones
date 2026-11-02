from fastapi import FastAPI 
from .routers import productos, ventas

app = FastAPI(title="API Punto de Venta") # Crea la instancia de FastAPI con un título para la documentación automática.

# Incluye los routers de productos y ventas en la aplicación FastAPI, lo que permite manejar las rutas relacionadas con productos y ventas.
app.include_router(productos.router)
app.include_router(ventas.router)