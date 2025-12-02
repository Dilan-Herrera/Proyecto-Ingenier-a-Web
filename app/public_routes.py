from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
import os
from werkzeug.security import generate_password_hash, check_password_hash
from .models import (
    create_user, get_user_by_email, 
    get_all_modelos, get_all_marcas, buscar_modelos_por_nombre, 
    get_all_perfiles, get_perfil_by_id, get_marca_by_id
)

public_bp = Blueprint("public", __name__)

ADMIN_USER = os.getenv("ADMIN_USER", "admin")
ADMIN_PASS = os.getenv("ADMIN_PASS", "admin123")

#  1. CORE MATEMÁTICO

def calcular_score_interno(modelo, pesos, maximos, minimos):
    try:
        def safe_float(valor):
            if valor is None: return 0.0
            try: return float(valor)
            except: return 0.0

        r = safe_float(modelo.get("rendimiento"))
        p = safe_float(modelo.get("precio"))
        c = safe_float(modelo.get("consumo"))
        t = safe_float(modelo.get("temperatura"))

        def norm(val, min_v, max_v):
            rango = max_v - min_v
            if rango == 0: return 0.0
            return (val - min_v) / rango

        Rn = norm(r, minimos['rend'], maximos['rend'])
        Pn = norm(p, minimos['prec'], maximos['prec'])
        Cn = norm(c, minimos['cons'], maximos['cons'])
        Tn = norm(t, minimos['temp'], maximos['temp'])

        alpha = safe_float(pesos.get("peso_rendimiento"))
        beta = safe_float(pesos.get("peso_precio"))
        gamma = safe_float(pesos.get("peso_consumo"))
        delta = safe_float(pesos.get("peso_temperatura"))

        return (alpha * Rn) + (beta * (1 - Pn)) + (gamma * (1 - Cn)) + (delta * (1 - Tn))
    except:
        return 0.0

## 2. RECOMENDACION PERSONAL DEL PROGRAMA

def generar_narrativa_humana(perfil_nombre, top3):
    """
    Compara el Top 1 vs Top 2 para generar un texto natural.
    """
    ganador = top3[0]
    
    if len(top3) == 1:
        return (f"Para tu perfil <strong>{perfil_nombre}</strong>, la única y mejor opción disponible "
                f"es la <strong>{ganador['nombre']}</strong>. Cumple con los requisitos básicos que buscas.")

    segundo = top3[1]
    
    precio_g = float(ganador['precio'])
    precio_s = float(segundo['precio'])
    rend_g = float(ganador['rendimiento'])
    rend_s = float(segundo['rendimiento'])
    
    diferencia_precio = precio_s - precio_g 
    diferencia_rend = rend_g - rend_s     

    # RECOMENDACIONES COMO "Vendedor Experto"
    
    if diferencia_precio > 0 and diferencia_rend > 0:
        return (f"¡La decisión está clara! Te recomiendo la <strong>{ganador['nombre']}</strong> sin dudarlo. "
                f"No solo es <strong>más económica</strong> que la {segundo['nombre']} (te ahorras ${diferencia_precio:.0f}), "
                f"sino que además tiene <strong>mayor rendimiento</strong>. Es la mejor compra para tu perfil {perfil_nombre}.")

    elif diferencia_precio > 0 and diferencia_rend <= 0:
        return (f"Analizando las opciones para {perfil_nombre}, te recomiendo comprar la <strong>{ganador['nombre']}</strong>. "
                f"Aunque la {segundo['nombre']} tiene un poco más de potencia, la diferencia es mínima y con la {ganador['nombre']} "
                f"<strong>te estás ahorrando ${diferencia_precio:.0f}</strong>. Es la compra más inteligente: obtienes casi los mismos beneficios por menos dinero.")

    elif diferencia_precio < 0 and diferencia_rend > 0:
        return (f"Si buscas ajustarte a tu perfil {perfil_nombre}, la <strong>{ganador['nombre']}</strong> es la ganadora. "
                f"Es verdad que cuesta un poco más que la {segundo['nombre']}, pero vale totalmente la pena porque su "
                f"<strong>rendimiento es superior</strong>. A largo plazo, esa potencia extra te servirá mucho más.")

    else:
        return (f"Estuvo muy reñido, pero para tu perfil {perfil_nombre} te recomiendo la <strong>{ganador['nombre']}</strong>. "
                f"Logra el mejor equilibrio entre los componentes que necesitas y la marca que escogiste, superando por poco "
                f"a la {segundo['nombre']}.")

#  RUTAS 

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
    
    perfiles = get_all_perfiles()
    return render_template("usuario_home.html", modelos=modelos, usuario=session.get("user_name"), busqueda=query, perfiles_disponibles=perfiles)

#  APIS COMPARADOR

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
    
    if not perfil_id:
        return jsonify({"error": "Seleccione un perfil"}), 400

    perfil = get_perfil_by_id(perfil_id)
    pesos = {
        "peso_rendimiento": float(perfil.get("peso_rendimiento", 0)),
        "peso_precio": float(perfil.get("peso_precio", 0)),
        "peso_consumo": float(perfil.get("peso_consumo", 0)),
        "peso_temperatura": float(perfil.get("peso_temperatura", 0)),
    }

    todos = get_all_modelos()
    filtrados = []
    for m in todos:
        if marca_id and str(m.get("marca_id")) != marca_id: continue
        filtrados.append(m)

    if not filtrados:
        return jsonify({"top3": [], "mensaje": "No hay modelos con esos filtros."})
    try:
        def sf(v): 
            try: return float(v) 
            except: return 0.0
        maximos = {k: max(sf(m.get(lbl)) for m in filtrados) for k, lbl in [('rend','rendimiento'),('prec','precio'),('cons','consumo'),('temp','temperatura')]}
        minimos = {k: min(sf(m.get(lbl)) for m in filtrados) for k, lbl in [('rend','rendimiento'),('prec','precio'),('cons','consumo'),('temp','temperatura')]}
    except:
        return jsonify({"top3": [], "mensaje": "Error de datos."})

    rankings = []
    for m in filtrados:
        score = calcular_score_interno(m, pesos, maximos, minimos)
        rankings.append({
            "nombre": m["nombre"],
            "precio": m["precio"],
            "rendimiento": m["rendimiento"],
            "score": round(score, 4)
        })

    rankings.sort(key=lambda x: x['score'], reverse=True)
    top3 = rankings[:3]
    
    texto_recomendacion = ""
    if top3:
        texto_recomendacion = generar_narrativa_humana(perfil['nombre'], top3)
    else:
        texto_recomendacion = "No hay datos suficientes."

    return jsonify({"top3": top3, "recomendacion": texto_recomendacion})

@public_bp.route("/api/get_tiendas", methods=["POST"])
def get_tiendas():
    ciudad = request.get_json().get("ciudad")
    tiendas_db = {
        "Quito": [{"nombre": "TechAdvisor CCI", "direccion": "Av. Amazonas y NNUU"}, {"nombre": "Tech Sur", "direccion": "CC El Recreo"}],
        "Guayaquil": [{"nombre": "MegaKywi", "direccion": "Av. 9 de Octubre"}, {"nombre": "Mall del Sol", "direccion": "Av. Juan Tanca Marengo"}],
        "Cuenca": [{"nombre": "TecnoAustro", "direccion": "Calle Larga"}]
    }
    return jsonify({"tiendas": tiendas_db.get(ciudad, [])})