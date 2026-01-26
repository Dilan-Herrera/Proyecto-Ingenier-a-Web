from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask import jsonify
import json 
from .models import (
    get_all_perfiles, get_perfil_by_id, create_perfil, update_perfil, delete_perfil,
    get_all_marcas, get_marca_by_id, create_marca, update_marca, delete_marca,
    get_all_modelos, get_modelo_by_id, get_modelo_by_codigo,
    create_modelo, update_modelo, delete_modelo, get_all_consultas
)

admin_bp = Blueprint("admin", __name__)

@admin_bp.before_request
def restringir_acceso_admin():
    """
    Este bloque se ejecuta antes de CUALQUIER ruta definida abajo.
    Si el usuario no es admin, lo patea al login.
    """
    if session.get("user_role") != "admin":
        flash("Acceso denegado. Debes iniciar sesión como Administrador.", "danger")
        return redirect(url_for("public.login"))

def calcular_ieg_avanzado(modelo, pesos, maximos, minimos):
    """
    Aplica la fórmula REAL con Normalización (0 a 1).
    IEG = (a * Rn) + (b * (1-Pn)) + (c * (1-Cn)) + (d * (1-Tn))
    """
    r_crudo = float(modelo.get("rendimiento") or 0)
    p_crudo = float(modelo.get("precio") or 0)
    c_crudo = float(modelo.get("consumo") or 0)
    t_crudo = float(modelo.get("temperatura") or 0)

    def normalizar(val, min_v, max_v):
        if max_v == min_v: return 0 
        return (val - min_v) / (max_v - min_v)

    Rn = normalizar(r_crudo, minimos['rend'], maximos['rend'])
    Pn = normalizar(p_crudo, minimos['prec'], maximos['prec'])
    Cn = normalizar(c_crudo, minimos['cons'], maximos['cons'])
    Tn = normalizar(t_crudo, minimos['temp'], maximos['temp'])

    alpha = float(pesos.get("peso_rendimiento") or 0)
    beta = float(pesos.get("peso_precio") or 0)
    gamma = float(pesos.get("peso_consumo") or 0)
    delta = float(pesos.get("peso_temperatura") or 0)

    score = (alpha * Rn) + (beta * (1 - Pn)) + (gamma * (1 - Cn)) + (delta * (1 - Tn))
    
    return score

@admin_bp.route("/")
def home():
    perfiles = get_all_perfiles()
    marcas = get_all_marcas()
    modelos = get_all_modelos()
    consultas = get_all_consultas()

    total_perfiles = len(perfiles)
    total_marcas = len(marcas)
    total_modelos = len(modelos)
    total_consultas = len(consultas)

    mejor_relacion = None
    mejor_ratio = None
    for m in modelos:
        precio = m.get("precio") or 0
        rendimiento = m.get("rendimiento") or 0
        try:
            if precio and precio > 0:
                ratio = float(rendimiento) / float(precio)
                if mejor_ratio is None or ratio > mejor_ratio:
                    mejor_ratio = ratio
                    mejor_relacion = m
        except (TypeError, ValueError):
            continue

    modelos_por_perfil = {}
    perfiles_dict = {str(p["_id"]): p for p in perfiles}

    for m in modelos:
        perfil_id = m.get("perfil_uso_id")
        if perfil_id:
            modelos_por_perfil[perfil_id] = modelos_por_perfil.get(perfil_id, 0) + 1

    chart_labels = []
    chart_values = []
    for perfil_id, count in modelos_por_perfil.items():
        perfil = perfiles_dict.get(str(perfil_id))
        nombre = perfil["nombre"] if perfil else "Sin perfil"
        chart_labels.append(nombre)
        chart_values.append(count)

    return render_template(
        "home.html",
        total_perfiles=total_perfiles,
        total_marcas=total_marcas,
        total_modelos=total_modelos,
        total_consultas=total_consultas,
        mejor_relacion=mejor_relacion,
        chart_labels=chart_labels,
        chart_values=chart_values,
    )


@admin_bp.route("/consultas")
def listar_consultas():
    consultas = get_all_consultas()
    perfiles = {str(p["_id"]): p for p in get_all_perfiles()}
    modelos = {str(m["_id"]): m for m in get_all_modelos()}

    for c in consultas:
        perfil = perfiles.get(str(c.get("perfil_uso_id")))
        modelo = modelos.get(str(c.get("modelo_id")))
        c["perfil_nombre"] = perfil["nombre"] if perfil else "N/A"
        c["modelo_nombre"] = modelo["nombre"] if modelo else "N/A"

    return render_template("consultas/listar.html", consultas=consultas)


# PERFILES DE USO

@admin_bp.route("/perfiles")
def listar_perfiles():
    perfiles = get_all_perfiles()
    return render_template("perfiles_uso/listar.html", perfiles=perfiles)


@admin_bp.route("/perfiles/nuevo", methods=["GET", "POST"])
def nuevo_perfil():
    errors = {}

    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        descripcion = request.form.get("descripcion", "").strip()

        peso_rendimiento = request.form.get("peso_rendimiento")
        peso_precio = request.form.get("peso_precio")
        peso_consumo = request.form.get("peso_consumo")
        peso_temperatura = request.form.get("peso_temperatura")

        if not nombre:
            errors["nombre"] = "El nombre del perfil es obligatorio."

        def validar_peso(campo, valor_raw):
            try:
                v = float(valor_raw)
                if v < 0:
                    errors[campo] = "El peso no puede ser negativo."
                return v
            except (TypeError, ValueError):
                errors[campo] = "El peso debe ser numérico."
                return None

        peso_rendimiento_val = validar_peso("peso_rendimiento", peso_rendimiento)
        peso_precio_val = validar_peso("peso_precio", peso_precio)
        peso_consumo_val = validar_peso("peso_consumo", peso_consumo)
        peso_temperatura_val = validar_peso("peso_temperatura", peso_temperatura)

        if not errors:
            data = {
                "nombre": nombre,
                "descripcion": descripcion,
                "peso_rendimiento": peso_rendimiento_val,
                "peso_precio": peso_precio_val,
                "peso_consumo": peso_consumo_val,
                "peso_temperatura": peso_temperatura_val,
            }
            create_perfil(data)
            flash("Perfil de uso creado correctamente.", "success")
            return redirect(url_for("admin.listar_perfiles"))

    return render_template("perfiles_uso/nuevo.html", errors=errors)


@admin_bp.route("/perfiles/editar/<id>", methods=["GET", "POST"])
def editar_perfil(id):
    perfil = get_perfil_by_id(id)
    if not perfil:
        flash("Perfil no encontrado.", "danger")
        return redirect(url_for("admin.listar_perfiles"))

    errors = {}

    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        descripcion = request.form.get("descripcion", "").strip()
        peso_rendimiento = request.form.get("peso_rendimiento")
        peso_precio = request.form.get("peso_precio")
        peso_consumo = request.form.get("peso_consumo")
        peso_temperatura = request.form.get("peso_temperatura")

        if not nombre:
            errors["nombre"] = "El nombre del perfil es obligatorio."

        def validar_peso(campo, valor_raw):
            try:
                v = float(valor_raw)
                if v < 0:
                    errors[campo] = "El peso no puede ser negativo."
                return v
            except (TypeError, ValueError):
                errors[campo] = "El peso debe ser numérico."
                return None

        peso_rendimiento_val = validar_peso("peso_rendimiento", peso_rendimiento)
        peso_precio_val = validar_peso("peso_precio", peso_precio)
        peso_consumo_val = validar_peso("peso_consumo", peso_consumo)
        peso_temperatura_val = validar_peso("peso_temperatura", peso_temperatura)

        if not errors:
            data = {
                "nombre": nombre,
                "descripcion": descripcion,
                "peso_rendimiento": peso_rendimiento_val,
                "peso_precio": peso_precio_val,
                "peso_consumo": peso_consumo_val,
                "peso_temperatura": peso_temperatura_val,
            }
            update_perfil(id, data)
            flash("Perfil actualizado correctamente.", "success")
            return redirect(url_for("admin.listar_perfiles"))

    return render_template("perfiles_uso/editar.html", perfil=perfil, errors=errors)


@admin_bp.route("/perfiles/eliminar/<id>", methods=["POST"])
def eliminar_perfil(id):
    delete_perfil(id)
    flash("Perfil eliminado correctamente.", "success")
    return redirect(url_for("admin.listar_perfiles"))


# MARCAS

@admin_bp.route("/marcas")
def listar_marcas():
    marcas = get_all_marcas()
    return render_template("marcas/listar.html", marcas=marcas)


@admin_bp.route("/marcas/nuevo", methods=["GET", "POST"])
def nueva_marca():
    errors = {}

    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        pais_origen = request.form.get("pais_origen", "").strip()

        if not nombre:
            errors["nombre"] = "El nombre de la marca es obligatorio."

        if not errors:
            data = {
                "nombre": nombre,
                "pais_origen": pais_origen,
            }
            create_marca(data)
            flash("Marca creada correctamente.", "success")
            return redirect(url_for("admin.listar_marcas"))

    return render_template("marcas/nuevo.html", errors=errors)


@admin_bp.route("/marcas/editar/<id>", methods=["GET", "POST"])
def editar_marca(id):
    marca = get_marca_by_id(id)
    if not marca:
        flash("Marca no encontrada.", "danger")
        return redirect(url_for("admin.listar_marcas"))

    errors = {}

    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        pais_origen = request.form.get("pais_origen", "").strip()

        if not nombre:
            errors["nombre"] = "El nombre de la marca es obligatorio."

        if not errors:
            data = {
                "nombre": nombre,
                "pais_origen": pais_origen,
            }
            update_marca(id, data)
            flash("Marca actualizada correctamente.", "success")
            return redirect(url_for("admin.listar_marcas"))

    return render_template("marcas/editar.html", marca=marca, errors=errors)


@admin_bp.route("/marcas/eliminar/<id>", methods=["POST"])
def eliminar_marca(id):
    delete_marca(id)
    flash("Marca eliminada correctamente.", "success")
    return redirect(url_for("admin.listar_marcas"))


# MODELOS DE COMPUTADORA

@admin_bp.route("/modelos")
def listar_modelos():
    modelos = get_all_modelos()
    marcas = {str(m["_id"]): m for m in get_all_marcas()}
    perfiles = {str(p["_id"]): p for p in get_all_perfiles()}

    modelos_enriquecidos = []
    for m in modelos:
        marca = marcas.get(str(m.get("marca_id")))
        perfil = perfiles.get(str(m.get("perfil_uso_id")))
        m["marca_nombre"] = marca["nombre"] if marca else "N/A"
        m["perfil_nombre"] = perfil["nombre"] if perfil else "N/A"
        modelos_enriquecidos.append(m)

    return render_template("modelos/listar.html", modelos=modelos_enriquecidos)


@admin_bp.route("/modelos/nuevo", methods=["GET", "POST"])
def nuevo_modelo():
    marcas = get_all_marcas()
    perfiles = get_all_perfiles()
    errors = {}

    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        codigo_modelo = request.form.get("codigo_modelo", "").strip()
        marca_id = request.form.get("marca_id")
        perfil_uso_id = request.form.get("perfil_uso_id")

        precio = request.form.get("precio")
        rendimiento = request.form.get("rendimiento")
        consumo = request.form.get("consumo")
        temperatura = request.form.get("temperatura")

        if not nombre:
            errors["nombre"] = "El nombre del modelo es obligatorio."

        if not codigo_modelo:
            errors["codigo_modelo"] = "El código del modelo es obligatorio."
        else:
            existente = get_modelo_by_codigo(codigo_modelo)
            if existente:
                errors["codigo_modelo"] = "Ya existe un modelo con ese código."

        try:
            precio_val = float(precio)
            if precio_val <= 0 or precio_val > 10000:
                errors["precio"] = "El precio debe ser mayor a 0 y razonable (<= 10000)."
        except (TypeError, ValueError):
            errors["precio"] = "El precio debe ser numérico."

        def validar_num_pos(nombre_campo, valor_raw, minimo=0):
            try:
                v = float(valor_raw)
                if v < minimo:
                    errors[nombre_campo] = f"{nombre_campo.capitalize()} debe ser ≥ {minimo}."
                return v
            except (TypeError, ValueError):
                errors[nombre_campo] = f"{nombre_campo.capitalize()} debe ser numérico."
                return None

        rendimiento_val = validar_num_pos("rendimiento", rendimiento, 0)
        consumo_val = validar_num_pos("consumo", consumo, 0)
        temperatura_val = validar_num_pos("temperatura", temperatura, 0)

        if not marca_id:
            errors["marca_id"] = "Debes seleccionar una marca."

        if not perfil_uso_id:
            errors["perfil_uso_id"] = "Debes seleccionar un perfil de uso."

        if not errors:
            data = {
                "nombre": nombre,
                "codigo_modelo": codigo_modelo,
                "marca_id": marca_id,
                "perfil_uso_id": perfil_uso_id,
                "precio": precio_val,
                "rendimiento": rendimiento_val,
                "consumo": consumo_val,
                "temperatura": temperatura_val,
            }
            create_modelo(data)
            flash("Modelo creado correctamente.", "success")
            return redirect(url_for("admin.listar_modelos"))

    return render_template("modelos/nuevo.html", marcas=marcas, perfiles=perfiles, errors=errors)


@admin_bp.route("/modelos/editar/<id>", methods=["GET", "POST"])
def editar_modelo(id):
    modelo = get_modelo_by_id(id)
    if not modelo:
        flash("Modelo no encontrado.", "danger")
        return redirect(url_for("admin.listar_modelos"))

    marcas = get_all_marcas()
    perfiles = get_all_perfiles()
    errors = {}

    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        codigo_modelo = request.form.get("codigo_modelo", "").strip()
        marca_id = request.form.get("marca_id")
        perfil_uso_id = request.form.get("perfil_uso_id")

        precio = request.form.get("precio")
        rendimiento = request.form.get("rendimiento")
        consumo = request.form.get("consumo")
        temperatura = request.form.get("temperatura")

        if not nombre:
            errors["nombre"] = "El nombre del modelo es obligatorio."

        if not codigo_modelo:
            errors["codigo_modelo"] = "El código del modelo es obligatorio."
        else:
            existente = get_modelo_by_codigo(codigo_modelo)
            if existente and str(existente["_id"]) != str(modelo["_id"]):
                errors["codigo_modelo"] = "Ya existe otro modelo con ese código."

        try:
            precio_val = float(precio)
            if precio_val <= 0 or precio_val > 10000:
                errors["precio"] = "El precio debe ser mayor a 0 y razonable (<= 10000)."
        except (TypeError, ValueError):
            errors["precio"] = "El precio debe ser numérico."

        def validar_num_pos(nombre_campo, valor_raw, minimo=0):
            try:
                v = float(valor_raw)
                if v < minimo:
                    errors[nombre_campo] = f"{nombre_campo.capitalize()} debe ser ≥ {minimo}."
                return v
            except (TypeError, ValueError):
                errors[nombre_campo] = f"{nombre_campo.capitalize()} debe ser numérico."
                return None

        rendimiento_val = validar_num_pos("rendimiento", rendimiento, 0)
        consumo_val = validar_num_pos("consumo", consumo, 0)
        temperatura_val = validar_num_pos("temperatura", temperatura, 0)

        if not marca_id:
            errors["marca_id"] = "Debes seleccionar una marca."

        if not perfil_uso_id:
            errors["perfil_uso_id"] = "Debes seleccionar un perfil de uso."

        if not errors:
            data = {
                "nombre": nombre,
                "codigo_modelo": codigo_modelo,
                "marca_id": marca_id,
                "perfil_uso_id": perfil_uso_id,
                "precio": precio_val,
                "rendimiento": rendimiento_val,
                "consumo": consumo_val,
                "temperatura": temperatura_val,
            }
            update_modelo(id, data)
            flash("Modelo actualizado correctamente.", "success")
            return redirect(url_for("admin.listar_modelos"))

    return render_template("modelos/editar.html",
                           modelo=modelo,
                           marcas=marcas,
                           perfiles=perfiles,
                           errors=errors)


@admin_bp.route("/modelos/eliminar/<id>", methods=["POST"])
def eliminar_modelo(id):
    delete_modelo(id)
    flash("Modelo eliminado correctamente.", "success")
    return redirect(url_for("admin.listar_modelos"))


@admin_bp.route("/calibracion_core", methods=["GET", "POST"])
def calibracion_core():
    perfiles = get_all_perfiles()
    perfil_id = request.values.get("perfil_id") 

    perfil = get_perfil_by_id(perfil_id) if perfil_id else None
    errores = {}
    pesos_form = {}
    resultados = []

    if perfil:
        pesos_form = {
            "peso_rendimiento": perfil.get("peso_rendimiento", 0),
            "peso_precio": perfil.get("peso_precio", 0),
            "peso_consumo": perfil.get("peso_consumo", 0),
            "peso_temperatura": perfil.get("peso_temperatura", 0),
        }

    if request.method == "POST" and perfil:
        accion = request.form.get("action")

        def parse_peso(campo):
            valor = request.form.get(campo)
            try:
                return float(valor)
            except (TypeError, ValueError):
                errores[campo] = "Debe ser un número."
                return None

        pr = parse_peso("peso_rendimiento")
        pp = parse_peso("peso_precio")
        pc = parse_peso("peso_consumo")
        pt = parse_peso("peso_temperatura")

        if not errores:
            pesos_nuevos = {
                "peso_rendimiento": pr,
                "peso_precio": pp,
                "peso_consumo": pc,
                "peso_temperatura": pt,
            }
            pesos_form = pesos_nuevos

            todos_modelos = get_all_modelos()
            
            if not todos_modelos:
                flash("Necesitas agregar modelos al sistema para calibrar.", "warning")
            else:
                try:
                    maximos = {
                        'rend': max(float(m.get('rendimiento',0)) for m in todos_modelos),
                        'prec': max(float(m.get('precio',0)) for m in todos_modelos),
                        'cons': max(float(m.get('consumo',0)) for m in todos_modelos),
                        'temp': max(float(m.get('temperatura',0)) for m in todos_modelos)
                    }
                    minimos = {
                        'rend': min(float(m.get('rendimiento',0)) for m in todos_modelos),
                        'prec': min(float(m.get('precio',0)) for m in todos_modelos),
                        'cons': min(float(m.get('consumo',0)) for m in todos_modelos),
                        'temp': min(float(m.get('temperatura',0)) for m in todos_modelos)
                    }
                except ValueError:
                    maximos = minimos = {'rend':0, 'prec':0, 'cons':0, 'temp':0}

                modelos_del_perfil = [m for m in todos_modelos if str(m.get("perfil_uso_id")) == str(perfil_id)]

                for m in modelos_del_perfil:
                    pesos_actuales = {
                        "peso_rendimiento": perfil.get("peso_rendimiento", 0),
                        "peso_precio": perfil.get("peso_precio", 0),
                        "peso_consumo": perfil.get("peso_consumo", 0),
                        "peso_temperatura": perfil.get("peso_temperatura", 0),
                    }
                    
                    ie_actual = calcular_ieg_avanzado(m, pesos_actuales, maximos, minimos)
                    ie_nuevo = calcular_ieg_avanzado(m, pesos_nuevos, maximos, minimos)
                    
                    resultados.append({
                        "modelo": m,
                        "ieg_actual": round(ie_actual, 4),
                        "ieg_nuevo": round(ie_nuevo, 4),
                        "diferencia": round(ie_nuevo - ie_actual, 4),
                    })
                    
                resultados.sort(key=lambda x: x['ieg_nuevo'], reverse=True)

            if accion == "guardar":
                data_update = {
                    "nombre": perfil["nombre"],
                    "descripcion": perfil.get("descripcion", ""),
                    "peso_rendimiento": pr,
                    "peso_precio": pp,
                    "peso_consumo": pc,
                    "peso_temperatura": pt,
                }
                update_perfil(perfil_id, data_update)
                flash("Pesos del perfil actualizados correctamente.", "success")
                perfil = get_perfil_by_id(perfil_id)

    return render_template(
        "calibracion.html",
        perfiles=perfiles,
        perfil_seleccionado=perfil,
        perfil_id_seleccionado=perfil_id,
        pesos_form=pesos_form,
        errores=errores,
        resultados=resultados,
    )

