from flask import Flask, render_template, request, send_file
from weasyprint import HTML
import io
import math
from datetime import date

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def form():
    if request.method == "POST":
        data = request.form
        address = data.get("address")
        object_name = data.get("object_name")
        material = data.get("material")
        base_layer = data.get("base_layer")
        area = float(data.get("area", 0))
        date_str = data.get("date", str(date.today()))

        # Основной материал
        mat_qty = int(data.get("material_qty", 0))
        mat_cost = int(data.get("material_cost", 0))
        mat_price = mat_cost / mat_qty if mat_qty else 0

        # Базовый слой
        base_qty = data.get("base_qty")
        base_cost = data.get("base_cost")
        if base_cost:
            base_qty = int(base_qty)
            base_cost = int(base_cost)
            base_price = base_cost / base_qty if base_qty else 0
        else:
            base_qty = base_cost = base_price = None

        # Aquawax
        aquawax_qty = aquawax_cost = aquawax_price = 0
        if material in ["LimeWash", "ISTRIA"]:
            aquawax_qty = int(data.get("aquawax_qty", 0))
            aquawax_cost = int(data.get("aquawax_cost", 0))
            aquawax_price = aquawax_cost / aquawax_qty if aquawax_qty else 0

        # Работы
        include_work = 'include_work' in data
        work_price = float(data.get("work_price", 0))
        work_sum = area * work_price if include_work else 0

        # Доп. материалы и грунтовка (сумма вводится, цена фикс)
        extra_cost = float(data.get("extra_cost", 0))
        primer_cost = float(data.get("primer_cost", 0))

        extra_qty = int(extra_cost / 12000) if extra_cost else 0
        primer_qty = int(primer_cost / 2500) if primer_cost else 0

        # Общая сумма
        total = mat_cost + aquawax_cost
        if base_cost:
            total += base_cost
        if include_work:
            total += work_sum + extra_cost + primer_cost

        # Названия материалов
        material_full_names = {
            "PERLATA": "PERLATA PLS",
            "TACTITE": "TACTITE",
            "LimeWash": "LimeWash",
            "ISTRIA": "ISTRIA P350"
        }
        material_name = material_full_names.get(material, material)

        html = render_template("offer.html",
                               address=address,
                               object_name=object_name,
                               material=material,
                               material_name=material_name,
                               mat_qty=mat_qty,
                               mat_cost=mat_cost,
                               mat_price=mat_price,
                               base_layer=base_layer,
                               base_qty=base_qty,
                               base_cost=base_cost,
                               base_price=base_price,
                               aquawax_qty=aquawax_qty,
                               aquawax_price=aquawax_price,
                               aquawax_cost=aquawax_cost,
                               include_work=include_work,
                               work_price=work_price,
                               work_sum=work_sum,
                               extra_qty=extra_qty,
                               extra_cost=extra_cost,
                               primer_qty=primer_qty,
                               primer_cost=primer_cost,
                               total=total,
                               date_str=date_str,
                               area=area)
        pdf = HTML(string=html, base_url=request.host_url).write_pdf()
        return send_file(io.BytesIO(pdf), mimetype="application/pdf",
                         download_name="Коммерческое_предложение.pdf")

    return render_template("form.html", current_date=date.today())
