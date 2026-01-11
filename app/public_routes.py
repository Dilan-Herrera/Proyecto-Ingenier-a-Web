from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
import os
from werkzeug.security import generate_password_hash, check_password_hash
from .services import CoreService
from .models import (
    create_user, get_user_by_email, get_all_modelos, get_all_marcas, 
    buscar_modelos_por_nombre, get_all_perfiles, get_perfil_by_id, 
    get_all_laptops
)

public_bp = Blueprint("public", __name__)

ADMIN_USER = os.getenv("ADMIN_USER")
ADMIN_PASS = os.getenv("ADMIN_PASS")


@public_bp.route("/")
def index():
    return redirect(url_for("public.login"))

@public_bp.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        nombre = request.form.get("nombre")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        if not nombre or not email or not password:
            flash("Todos los campos son obligatorios.", "danger")
            return redirect(url_for("public.registro"))
        if password != confirm_password:
            flash("Las contraseñas no coinciden.", "danger")
            return redirect(url_for("public.registro"))
        if get_user_by_email(email):
            flash("El correo electrónico ya está registrado.", "warning")
            return redirect(url_for("public.registro"))

        hashed_password = generate_password_hash(password)
        create_user({"nombre": nombre, "email": email, "password": hashed_password, "role": "usuario"})
        flash("Cuenta creada exitosamente.", "success")
        return redirect(url_for("public.login"))
    return render_template("registro.html")

@public_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario_input = request.form.get("username")
        password_input = request.form.get("password")

        if usuario_input == ADMIN_USER and password_input == ADMIN_PASS:
            session["user_role"] = "admin"
            session["user_name"] = "Administrador"
            return redirect(url_for("admin.home"))

        user_db = get_user_by_email(usuario_input)
        if user_db and check_password_hash(user_db["password"], password_input):
            session["user_role"] = "usuario"
            session["user_name"] = user_db["nombre"]
            session["user_id"] = str(user_db["_id"])
            return redirect(url_for("public.home_usuario"))

        flash("Correo o contraseña incorrectos.", "danger")
        return redirect(url_for("public.login"))
    return render_template("login.html")

@public_bp.route("/logout")
def logout():
    session.clear()
    flash("Has cerrado sesión.", "info")
    return redirect(url_for("public.login"))

@public_bp.route("/inicio")
def home_usuario():
    if "user_role" not in session: return redirect(url_for("public.login"))
    if session["user_role"] == "admin": return redirect(url_for("admin.home"))

    query = request.args.get("q")
    if query: modelos = buscar_modelos_por_nombre(query)
    else: modelos = get_all_modelos()

    marcas = {str(m["_id"]): m["nombre"] for m in get_all_marcas()}
    for m in modelos:
        m["nombre_marca"] = marcas.get(str(m.get("marca_id")), "Desconocida")
    
    return render_template("usuario_home.html", 
                           modelos=modelos, 
                           usuario=session.get("user_name"),
                           busqueda=query, 
                           perfiles_disponibles=get_all_perfiles())

@public_bp.route("/api/get_marcas", methods=["GET"])
def get_marcas_api():
    marcas = get_all_marcas()
    data = [{"id": str(m["_id"]), "nombre": m["nombre"]} for m in marcas]
    return jsonify({"marcas": data})

@public_bp.route("/api/comparar_resultados", methods=["POST"])
def comparar_resultados():
    data = request.get_json()
    perfil_id = data.get("perfil_id")
    marca_id = data.get("marca_id") 
    
    if not perfil_id: return jsonify({"error": "Seleccione un perfil"}), 400

    perfil = get_perfil_by_id(perfil_id)
    pesos = {
        "peso_rendimiento": float(perfil.get("peso_rendimiento", 0)),
        "peso_precio": float(perfil.get("peso_precio", 0)),
        "peso_consumo": float(perfil.get("peso_consumo", 0)),
        "peso_temperatura": float(perfil.get("peso_temperatura", 0)),
    }

    pcs = get_all_modelos()
    laptops = get_all_laptops()
    
    for p in pcs: p['tipo_equipo'] = 'PC Escritorio'
    for l in laptops: l['tipo_equipo'] = 'Laptop'
    
    todos = pcs + laptops
    
    filtrados = [m for m in todos if not marca_id or str(m.get("marca_id")) == marca_id]

    if not filtrados: return jsonify({"top3": [], "mensaje": "No hay modelos disponibles."})

    try:
        def sf(v): return CoreService._safe_float(v)
        maximos = {k: max(sf(m.get(l)) for m in filtrados) for k, l in [('rend','rendimiento'),('prec','precio'),('cons','consumo'),('temp','temperatura')]}
        minimos = {k: min(sf(m.get(l)) for m in filtrados) for k, l in [('rend','rendimiento'),('prec','precio'),('cons','consumo'),('temp','temperatura')]}
    except:
        return jsonify({"top3": [], "mensaje": "Datos insuficientes para calcular."})

    rankings = []
    for m in filtrados:
        score = CoreService.calcular_score(m, pesos, maximos, minimos)
        rankings.append({
            "nombre": m["nombre"],
            "precio": m["precio"],
            "rendimiento": m["rendimiento"],
            "score": round(score, 4),
            "tipo": m["tipo_equipo"]
        })

    rankings.sort(key=lambda x: x['score'], reverse=True)
    top3 = rankings[:3]
    
    recomendacion = CoreService.generar_narrativa_avanzada(perfil['nombre'], top3, pesos)

    return jsonify({"top3": top3, "recomendacion": recomendacion})

@public_bp.route("/api/get_tiendas", methods=["POST"])
def get_tiendas():
    ciudad = request.get_json().get("ciudad")
    tiendas_db = {
        "Quito": [{"nombre": "TechAdvisor Norte", "direccion": "Av. Amazonas y NNUU"}, {"nombre": "Sur Store", "direccion": "CC El Recreo"}],
        "Guayaquil": [{"nombre": "MegaKywi", "direccion": "Av. 9 de Octubre"}, {"nombre": "Mall del Sol", "direccion": "Av. Juan Tanca Marengo"}],
        "Cuenca": [{"nombre": "TecnoAustro", "direccion": "Calle Larga"}]
    }
    return jsonify({"tiendas": tiendas_db.get(ciudad, [])})