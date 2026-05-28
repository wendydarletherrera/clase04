from __future__ import annotations

import os
from pathlib import Path

from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_login import login_required
from werkzeug.utils import secure_filename

from app import db
from app.auth.routes import log_access, role_required
from app.data.services import import_sales_csv
from app.forms import CsvUploadForm

data_bp = Blueprint("data", __name__)


@data_bp.route("/importar", methods=["GET", "POST"])
@login_required
@role_required("admin")
def importar():
    form = CsvUploadForm()
    if form.validate_on_submit():
        upload_dir = Path(current_app.config["CSV_UPLOAD_FOLDER"])
        upload_dir.mkdir(parents=True, exist_ok=True)
        file_storage = form.csv_file.data
        filename = secure_filename(file_storage.filename or "ventas.csv")
        temp_path = upload_dir / filename
        file_storage.save(temp_path)

        result = import_sales_csv(temp_path)
        log_access(
            "import_csv",
            f"archivo={filename}; insertados={result.inserted}; omitidos={result.skipped}; errores={len(result.errors)}",
        )
        db.session.commit()

        try:
            os.remove(temp_path)
        except OSError:
            current_app.logger.warning("No se pudo eliminar archivo temporal %s", temp_path)

        if result.errors:
            flash(
                f"Importacion con errores: {result.inserted} insertados, "
                f"{result.skipped} omitidos, {len(result.errors)} errores.",
                "warning",
            )
            for error in result.errors[:5]:
                flash(f"Linea {error['line']}: {error['error']}", "danger")
        else:
            flash(
                f"CSV importado: {result.inserted} insertados, {result.skipped} duplicados omitidos.",
                "success",
            )
        return redirect(url_for("data.importar"))

    return render_template("import_csv.html", form=form, title="Importar CSV")
