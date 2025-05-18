from flask import Flask, render_template, request, send_file
from weasyprint import HTML
import io
import math
from datetime import date
import sqlite3
from db import init_db

app = Flask(__name__)
init_db()

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

        # Основной материал
        mat_qty = int(data.get("material_qty", 0))
        mat_cost = int(data.get("material_cost", 0))
        mat_price = round(mat_cost / mat_qty, 2) if mat_qty else 0

        # AQUAWAX
        aquawax_qty = data.get("aquawax_qty")
        aquawax_cost = data.get("aquawax_cost")
        if aquawax_qty and aquawax_cost:
            aquawax_qty = int(aquawax_qty)
            aquawax_cost = int(aquawax_cost)
        else:
            aquawax_qty = aquawax_cost = None

        # Базовый слой
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

        # Доп. материалы
        extra_cost = data.get("extra_cost")
        extra_qty = math.ceil(float(extra_cost) / 12000) if extra_cost else None
        extra_cost = int(extra_cost) if extra_cost else None

        # Грунтовка
        primer_cost = data.get("primer_cost")
        primer_qty = math.ceil(float(primer_cost) / 2500) if primer_cost else None
        primer_cost = int(primer_cost) if primer_cost else None

        # Работы
        include_work = data.get("include_work") == "on"
        work_price = float(data.get("work_price", 7000))
        work_sum = round(area * work_price, 2) if include_work else 0

        # Общая сумма
        total = mat_cost + (aquawax_cost or 0) + (base_cost or 0) + \
                (extra_cost or 0) + (primer_cost or 0) + (work_sum or 0)

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

        filename = f"Коммерческое_предложение_{date_str}_{object_name}.pdf"
        pdf_path = f"static/generated/{filename}"
        HTML(string=html).write_pdf(pdf_path)

        try:
    with sqlite3.connect("offers.db") as conn:
        conn.execute("""
            INSERT INTO offers (date, object_name, address, total, pdf_filename)
            VALUES (?, ?, ?, ?, ?)
        """, (date_str, object_name, address, total, filename))
    print("✅ Успешно записано в БД")
except Exception as e:
    print("❌ Ошибка при записи в БД:", e)

        return send_file(pdf_path, as_attachment=False)

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

if __name__ == "__main__":
    app.run(debug=True)
