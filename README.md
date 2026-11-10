# 💰 Control de Gastos

Aplicación web para registrar gastos personales y generar reportes. Desarrollada con **Python**, **Flask** y **SQLite**.

## Funcionalidades

- **Inicio de sesión** con usuario y clave (la clave se guarda con hash, nunca en texto plano).
- **Registro de gastos**: fecha, descripción y monto.
- **Listado** de gastos ordenado por fecha, con opción de eliminar.
- **Reporte**: total gastado, número de gastos, promedio, mayor gasto, total por mes y detalle; con **filtro por rango de fechas**, **descarga en CSV** e **impresión**.
- Las rutas están protegidas: sin iniciar sesión se redirige al login.

## Credenciales de acceso

| Usuario | Clave |
|---------|-------|
| `admin` | `123`   |

## Instalación y ejecución

```bash
git clone <URL-DE-ESTE-REPOSITORIO>
cd control-gastos
python -m venv venv
# Windows: venv\Scripts\activate   |   Linux/Mac: source venv/bin/activate
pip install -r requirements.txt
python app.py
```

Abrir en el navegador: <http://127.0.0.1:5000>

La base de datos `gastos.db` se crea sola la primera vez, junto con el usuario `admin`.

## Cómo funciona

### 1. Inicio de sesión
Se ingresa con `admin` / `123`.

![Login](capturas/01-login.png)

Si las credenciales son incorrectas, se muestra un mensaje de error.

![Error de login](capturas/02-login-error.png)

### 2. Registro de gastos
Se completa fecha, descripción y monto, y se pulsa **Guardar**. El gasto aparece en la tabla inferior; con **Eliminar** se borra.

![Gastos](capturas/03-gastos.png)

### 3. Reporte
En **Reporte** se ve el resumen de los gastos, el total por mes y el detalle.

![Reporte](capturas/04-reporte.png)

Se puede filtrar por rango de fechas (ejemplo: desde 2026-11-01), descargar el CSV o imprimir.

![Reporte filtrado](capturas/05-reporte-filtrado.png)

## Estructura del proyecto

```
control-gastos/
├── app.py              # Rutas, lógica y base de datos (Flask + SQLite)
├── requirements.txt
├── static/style.css
├── templates/          # base, login, gastos, reporte (Jinja2)
└── capturas/           # imágenes del README
```

## Base de datos (SQLite)

- `usuarios (id, username, password_hash)`
- `gastos (id, fecha, descripcion, monto)`
