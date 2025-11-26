from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import os
from werkzeug.security import generate_password_hash, check_password_hash
from .models import create_user, get_user_by_email

public_bp = Blueprint("public", __name__)

ADMIN_USER = os.getenv("ADMIN_USER", "admin")
ADMIN_PASS = os.getenv("ADMIN_PASS", "admin123")

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

        new_user = {
            "nombre": nombre,
            "email": email,
            "password": hashed_password,
            "role": "usuario" 
        }
        create_user(new_user)

        flash("Cuenta creada exitosamente. ¡Ahora puedes iniciar sesión!", "success")
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
    if "user_role" not in session:
        return redirect(url_for("public.login"))
    
    if session["user_role"] == "admin":
        return redirect(url_for("admin.home"))

    return render_template("usuario_home.html", nombre=session.get("user_name"))