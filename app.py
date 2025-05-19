from flask import Flask, render_template, request, send_file, redirect, url_for
from weasyprint import HTML
import io
import math
import os
import sqlite3
from datetime import date
from werkzeug.utils import secure_filename
from dropbox_upload import upload_to_dropbox, delete_from_dropbox

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def form():
    if request.method == "POST":
        data = request.form
        address = data.get("address")
        object_name = data.get("object_name")
        material = data.get("material")
        material_name = material if material != "ISTRIA" else "ISTRIA P350"
        base_layer = data.get("base_layer")
        area = float(data.get("area", 0))
        date_str = data.get("date", str(date.today()))

        mat_qty = int(data.get("material_qty", 0))
        mat_cost = int(data.get("material_cost", 0))
        mat_price = round(mat_cost / mat_qty, 2) if mat_qty else 0

        aquawax_qty = data.get("aquawax_qty")
        aquawax_cost = data.get("aquawax_cost")
        if aquawax_qty and aquawax_cost:
            aquawax_qty = int(aquawax_qty)
            aquawax_cost = int(aquawax_cost)
        else:
            aquawax_qty = aquawax_cost = None

        base_qty = data.get("base_qty")
        base_cost = data.get("base_cost")
        if base_qty and base_cost and base_layer:
            base_qty = int(base_qty)
            base_cost = int(base_cost)
            if "Dulux" in base_layer:
                base_price = 8000
            elif "Marshall" in base_layer:
                base_price = 4000
            else:
                base_price = 27000
        else:
            base_qty = base_cost = base_price = None

        extra_cost = data.get("extra_cost")
        extra_qty = math.ceil(float(extra_cost) / 12000) if extra_cost else None
        extra_cost = int(extra_cost) if extra_cost else None

        primer_cost = data.get("primer_cost")
        primer_qty = math.ceil(float(primer_cost) / 2500) if primer_cost else None
        primer_cost = int(primer_cost) if primer_cost else None

        include_work = data.get("include_work") == "on"
        work_price = float(data.get("work_price", 7000))
        work_sum = round(area * work_price, 2) if include_work else 0

        total = mat_cost + (aquawax_cost or 0) + (base_cost or 0) + \
                (extra_cost or 0) + (primer_cost or 0) + (work_sum or 0)

        clean_material = secure_filename(f"{material_name}_{base_layer or ''}".replace(" ", "_"))
        date_code = date_str.replace("-", "")
        filename = f"{date_code}_{int(total)}_{clean_material}.pdf"
        pdf_path = f"/tmp/{filename}"

        html = render_template("offer.html",
            address=address,
            object_name=object_name,
            material=material,
            material_name=material_name,
            mat_qty=mat_qty,
            mat_cost=mat_cost,
            mat_price=mat_price,
            aquawax_qty=aquawax_qty,
            aquawax_cost=aquawax_cost,
            base_layer=base_layer,
            base_qty=base_qty,
            base_cost=base_cost,
            base_price=base_price,
            extra_qty=extra_qty,
            extra_cost=extra_cost,
            primer_qty=primer_qty,
            primer_cost=primer_cost,
            include_work=include_work,
            work_price=work_price,
            work_sum=work_sum,
            total=total,
            date_str=date_str,
            area=area
        )
        HTML(string=html).write_pdf(pdf_path)

        try:
            dropbox_filename = upload_to_dropbox(pdf_path, filename)
        except Exception as e:
            dropbox_filename = f"Ошибка загрузки: {e}"

        with sqlite3.connect("offers.db") as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS offers (
                    date TEXT,
                    object_name TEXT,
                    address TEXT,
                    total REAL,
                    pdf_filename TEXT
                )
            """)
            conn.execute("""
                INSERT INTO offers (date, object_name, address, total, pdf_filename)
                VALUES (?, ?, ?, ?, ?)
            """, (date_str, object_name, address, total, dropbox_filename))

        if os.path.exists(pdf_path):
            os.remove(pdf_path)

        return f'<p><a href="https://www.dropbox.com/home/CommercialOffers/{dropbox_filename}" target="_blank">📄 Открыть загруженный PDF</a></p>'

    return render_template("form.html", current_date=date.today())

@app.route("/offers")
def offers_list():
    query = request.args.get("q", "").lower()
    with sqlite3.connect("offers.db") as conn:
        conn.row_factory = sqlite3.Row
        offers = conn.execute("SELECT rowid AS id, * FROM offers").fetchall()
    if query:
        offers = [o for o in offers if query in o["object_name"].lower()
                  or query in o["address"].lower() or query in o["date"]]
    return render_template("offers_list.html", offers=offers, query=query)

@app.route("/delete/<int:id>", methods=["POST"])
def delete_offer(id):
    with sqlite3.connect("offers.db") as conn:
        cur = conn.cursor()
        cur.execute("SELECT pdf_filename FROM offers WHERE rowid = ?", (id,))
        row = cur.fetchone()
        if row:
            filename = row[0]
            try:
                delete_from_dropbox(filename)
            except Exception as e:
                print("⚠ Не удалось удалить из Dropbox:", e)
        conn.execute("DELETE FROM offers WHERE rowid = ?", (id,))
    return redirect(url_for("offers_list"))
