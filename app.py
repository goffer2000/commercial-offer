from flask import Flask, render_template, request, send_file, redirect
from weasyprint import HTML
from datetime import date
import os
import io
import math
import sqlite3
from dropbox_upload import upload_to_dropbox

app = Flask(__name__)
os.makedirs("static/generated", exist_ok=True)

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
            if "Dulux" in base_layer or "Marshall" in base_layer:
                base_price = 8000 if "Dulux" in base_layer else 4000
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

        total = mat_cost + (aquawax_cost or 0) + (base_cost or 0) + (extra_cost or 0) + (primer_cost or 0) + (work_sum or 0)

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

        filename = f"{date_str.replace('-', '')}_{int(total)}_{material}_{base_layer or ''}.pdf".replace(' ', '_')
        file_path = f"static/generated/{filename}"
        HTML(string=html).write_pdf(file_path)

        dropbox_path = f"/CommercialOffers/{filename}"
        dropbox_status = False
        try:
            dropbox_status = upload_to_dropbox(file_path, dropbox_path)
        except Exception as e:
            print("Dropbox upload failed:", e)

        with sqlite3.connect("offers.db") as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS offers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT, object_name TEXT, address TEXT,
                    total REAL, pdf_filename TEXT, dropbox_uploaded INTEGER
                )
            """)
            conn.execute("""
                INSERT INTO offers (date, object_name, address, total, pdf_filename, dropbox_uploaded)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (date_str, object_name, address, total, filename, int(dropbox_status)))

        return send_file(file_path, as_attachment=False)

    return render_template("form.html", current_date=date.today())

@app.route("/offers")
def offers_list():
    query = request.args.get("q", "").lower()
    with sqlite3.connect("offers.db") as conn:
        conn.row_factory = sqlite3.Row
        offers = conn.execute("SELECT * FROM offers").fetchall()

    if query:
        offers = [o for o in offers if query in o["object_name"].lower() or query in o["address"].lower() or query in o["date"]]

    return render_template("offers_list.html", offers=offers, query=query)

@app.route("/delete/<int:offer_id>")
def delete_offer(offer_id):
    with sqlite3.connect("offers.db") as conn:
        row = conn.execute("SELECT pdf_filename FROM offers WHERE id = ?", (offer_id,)).fetchone()
        if row:
            pdf_path = f"static/generated/{row['pdf_filename']}"
            if os.path.exists(pdf_path):
                os.remove(pdf_path)
        conn.execute("DELETE FROM offers WHERE id = ?", (offer_id,))
    return redirect("/offers")
