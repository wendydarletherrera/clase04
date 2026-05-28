from __future__ import annotations

from datetime import datetime
from functools import wraps

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.security import check_password_hash

from app import db
from app.forms import LoginForm
from app.models import BitacoraAcceso, Usuario

auth_bp = Blueprint("auth", __name__)


def log_access(action: str, detail: str = "", user: Usuario | None = None) -> None:
    actor = user if user is not None else (current_user if current_user.is_authenticated else None)
    entry = BitacoraAcceso(
        usuario_id=actor.id if actor else None,
        ip=request.headers.get("X-Forwarded-For", request.remote_addr),
        accion=action,
        detalle=detail[:255] if detail else "",
    )
    db.session.add(entry)


def role_required(role: str):
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for("auth.login"))
            if current_user.rol != role:
                abort(403)
            return view(*args, **kwargs)

        return wrapped

    return decorator


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.ejecutivo"))

    form = LoginForm()
    if form.validate_on_submit():
        user = Usuario.query.filter_by(username=form.username.data.strip()).first()
        if user and user.is_active and check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=form.remember.data)
            user.ultimo_acceso = datetime.utcnow()
            log_access("login", "Inicio de sesion correcto", user)
            db.session.commit()
            flash("Bienvenido al panel comercial.", "success")
            next_url = request.args.get("next")
            return redirect(next_url or url_for("dashboard.ejecutivo"))

        log_access("login_failed", f"Usuario: {form.username.data}")
        db.session.commit()
        flash("Credenciales invalidas o usuario inactivo.", "danger")

    return render_template("login.html", form=form, title="Login")


@auth_bp.route("/logout")
@login_required
def logout():
    log_access("logout", "Cierre de sesion")
    db.session.commit()
    logout_user()
    flash("Sesion cerrada correctamente.", "info")
    return redirect(url_for("auth.login"))
