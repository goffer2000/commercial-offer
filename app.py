from flask import Flask, render_template, request, send_file
from weasyprint import HTML
from datetime import date
import io
import math

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def form():
    if request.method == "POST":
        data = request.form
        address = data.get("address")
        object_name = data.get("object_name")
        date_str = data.get("date", str(date.today()))
        area = float(data.get("area", 0))
        material = data.get("material")

        # Основной материал
        mat_qty = int(data.get("material_qty", 0))
        mat_cost = int(data.get("material_cost", 0))
        mat_price = round(mat_cost / mat_qty, 2) if mat_qty else 0
        material_name = material if material != "ISTRIA" else "ISTRIA P350"

        # AQUAWAX
        aquawax_qty = data.get("aquawax_qty")
        aquawax_cost = data.get("aquawax_cost")
        if aquawax_qty and aquawax_cost:
            aquawax_qty = int(aquawax_qty)
            aquawax_cost = int(aquawax_cost)
            aquawax_price = round(aquawax_cost / aquawax_qty, 2)
        else:
            aquawax_qty = aquawax_cost = aquawax_price = None

        # Базовый слой
        base_layer = data.get("base_layer")
        base_qty = data.get("base_qty")
        base_cost = data.get("base_cost")
        if base_layer and base_qty and base_cost:
            base_qty = int(base_qty)
            base_cost = int(base_cost)
            base_price = round(base_cost / base_qty, 2) if base_qty else 0
        else:
            base_layer = base_qty = base_cost = base_price = None

        # Доп. материалы и грунтовка
        extra_cost = data.get("extra_cost")
        primer_cost = data.get("primer_cost")
        extra_qty = primer_qty = 0
        if extra_cost:
            extra_cost = int(extra_cost)
            extra_qty = math.ceil(area / 35)
        else:
            extra_cost = None

        if primer_cost:
            primer_cost = int(primer_cost)
            primer_qty = math.ceil(area / 16)
        else:
            primer_cost = None

        # Работы
        include_work = 'include_work' in data
        work_price = work_sum = 0
        if include_work:
            work_price = float(data.get("work_price", 7000))
            work_sum = round(area * work_price)

        # Итого
        total = mat_cost
        if aquawax_cost: total += aquawax_cost
        if base_cost: total += base_cost
        if extra_cost: total += extra_cost
        if primer_cost: total += primer_cost
        if include_work: total += work_sum

        html = render_template("offer.html",
                               address=address,
                               object_name=object_name,
                               date_str=date_str,
                               area=area,
                               material=material,
                               material_name=material_name,
                               mat_qty=mat_qty,
                               mat_cost=mat_cost,
                               mat_price=mat_price,
                               aquawax_qty=aquawax_qty,
                               aquawax_cost=aquawax_cost,
                               aquawax_price=aquawax_price,
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
                               total=total)

        pdf = HTML(string=html, base_url=request.base_url).write_pdf()
        return send_file(io.BytesIO(pdf), download_name="Коммерческое_предложение.pdf", mimetype="application/pdf")

    return render_template("form.html", current_date=date.today())
