import csv
import io
import sqlite3
from datetime import date
from functools import wraps

from flask import (Flask, Response, flash, g, redirect, render_template,
                   request, session, url_for)
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.secret_key = "cambia-esta-clave-en-produccion"
DATABASE = "gastos.db"


# ---------- Base de datos ----------
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(_exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = sqlite3.connect(DATABASE)
    db.executescript(
        """
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS gastos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT NOT NULL,
            descripcion TEXT NOT NULL,
            monto REAL NOT NULL
        );
        """
    )
    existe = db.execute("SELECT 1 FROM usuarios WHERE username = 'admin'").fetchone()
    if not existe:
        db.execute(
            "INSERT INTO usuarios (username, password_hash) VALUES (?, ?)",
            ("admin", generate_password_hash("123")),
        )
    db.commit()
    db.close()


# ---------- Autenticación ----------
def login_required(vista):
    @wraps(vista)
    def envoltura(*args, **kwargs):
        if "usuario" not in session:
            flash("Debes iniciar sesión para continuar.", "error")
            return redirect(url_for("login"))
        return vista(*args, **kwargs)
    return envoltura


@app.route("/")
def inicio():
    return redirect(url_for("gastos" if "usuario" in session else "login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = get_db().execute(
            "SELECT * FROM usuarios WHERE username = ?", (username,)
        ).fetchone()
        if user and check_password_hash(user["password_hash"], password):
            session["usuario"] = user["username"]
            return redirect(url_for("gastos"))
        flash("Usuario o clave incorrectos.", "error")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Sesión cerrada.", "ok")
    return redirect(url_for("login"))


# ---------- Gastos ----------
@app.route("/gastos", methods=["GET", "POST"])
@login_required
def gastos():
    db = get_db()
    if request.method == "POST":
        fecha = request.form.get("fecha", "").strip()
        descripcion = request.form.get("descripcion", "").strip()
        try:
            monto = float(request.form.get("monto", ""))
        except ValueError:
            monto = None
        if not fecha or not descripcion or monto is None or monto <= 0:
            flash("Completa fecha, descripción y un monto mayor a 0.", "error")
        else:
            db.execute(
                "INSERT INTO gastos (fecha, descripcion, monto) VALUES (?, ?, ?)",
                (fecha, descripcion, monto),
            )
            db.commit()
            flash("Gasto registrado.", "ok")
        return redirect(url_for("gastos"))
    lista = db.execute("SELECT * FROM gastos ORDER BY fecha DESC, id DESC").fetchall()
    return render_template("gastos.html", gastos=lista, hoy=date.today().isoformat())


@app.route("/gastos/eliminar/<int:gasto_id>", methods=["POST"])
@login_required
def eliminar(gasto_id):
    db = get_db()
    db.execute("DELETE FROM gastos WHERE id = ?", (gasto_id,))
    db.commit()
    flash("Gasto eliminado.", "ok")
    return redirect(url_for("gastos"))


# ---------- Reporte ----------
def consultar(desde, hasta):
    sql = "SELECT * FROM gastos WHERE 1=1"
    params = []
    if desde:
        sql += " AND fecha >= ?"
        params.append(desde)
    if hasta:
        sql += " AND fecha <= ?"
        params.append(hasta)
    sql += " ORDER BY fecha ASC, id ASC"
    return get_db().execute(sql, params).fetchall()


@app.route("/reporte")
@login_required
def reporte():
    desde = request.args.get("desde", "")
    hasta = request.args.get("hasta", "")
    filas = consultar(desde, hasta)
    total = sum(f["monto"] for f in filas)
    por_mes = {}
    for f in filas:
        mes = f["fecha"][:7]
        por_mes[mes] = por_mes.get(mes, 0) + f["monto"]
    promedio = total / len(filas) if filas else 0
    mayor = max(filas, key=lambda f: f["monto"]) if filas else None
    return render_template(
        "reporte.html", filas=filas, total=total, por_mes=por_mes,
        promedio=promedio, mayor=mayor, desde=desde, hasta=hasta,
    )


@app.route("/reporte/csv")
@login_required
def reporte_csv():
    filas = consultar(request.args.get("desde", ""), request.args.get("hasta", ""))
    salida = io.StringIO()
    w = csv.writer(salida)
    w.writerow(["Fecha", "Descripcion", "Monto"])
    for f in filas:
        w.writerow([f["fecha"], f["descripcion"], f"{f['monto']:.2f}"])
    return Response(
        salida.getvalue(), mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=reporte_gastos.csv"},
    )


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
