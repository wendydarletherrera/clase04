from __future__ import annotations

import click
from flask import Flask, redirect, url_for
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from werkzeug.security import generate_password_hash

from app.config import Config

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
csrf = CSRFProtect()


def create_app(config_class: type[Config] = Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    login_manager.login_view = "auth.login"
    login_manager.login_message = "Inicia sesion para continuar."
    login_manager.login_message_category = "warning"

    from app.models import Usuario

    @login_manager.user_loader
    def load_user(user_id: str) -> Usuario | None:
        return db.session.get(Usuario, int(user_id))

    from app.auth.routes import auth_bp
    from app.dashboard.routes import dashboard_bp
    from app.data.routes import data_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp, url_prefix="/dashboard")
    app.register_blueprint(data_bp, url_prefix="/data")

    @app.route("/")
    def index():
        return redirect(url_for("dashboard.ejecutivo"))

    register_cli(app)
    register_template_filters(app)

    return app


def register_template_filters(app: Flask) -> None:
    @app.template_filter("money")
    def money(value):
        if value is None:
            return "Bs 0.00"
        return f"Bs {float(value):,.2f}"


def register_cli(app: Flask) -> None:
    @app.cli.command("create-admin")
    def create_admin_command():
        """Create or update the initial administrator from environment variables."""
        from app.models import Usuario

        username = app.config["ADMIN_USERNAME"]
        email = app.config["ADMIN_EMAIL"]
        password = app.config["ADMIN_PASSWORD"]
        full_name = app.config["ADMIN_FULL_NAME"]

        if not password:
            raise click.ClickException("ADMIN_PASSWORD no esta definido en el entorno.")

        user = Usuario.query.filter_by(username=username).first()
        action = "actualizado"
        if user is None:
            user = Usuario(username=username)
            db.session.add(user)
            action = "creado"

        user.nombre_completo = full_name
        user.email = email
        user.password_hash = generate_password_hash(password)
        user.rol = "admin"
        user.estado = "activo"
        db.session.commit()
        click.echo(f"Usuario admin {action}: {username}")

    @app.cli.command("import-csv")
    @click.option("--path", "csv_path", default="dataset_cafe_andino.csv", show_default=True)
    def import_csv_command(csv_path: str):
        """Import sales rows from a CSV file into PostgreSQL."""
        from app.data.services import import_sales_csv

        result = import_sales_csv(csv_path)
        click.echo(
            "Importacion finalizada. "
            f"insertados={result.inserted}, omitidos={result.skipped}, errores={len(result.errors)}"
        )
        for error in result.errors[:10]:
            click.echo(f"Linea {error['line']}: {error['error']}", err=True)
        if len(result.errors) > 10:
            click.echo(f"... {len(result.errors) - 10} errores adicionales", err=True)
