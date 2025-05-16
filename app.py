from flask import Flask, render_template, request, send_file
from weasyprint import HTML
import io
import math
from datetime import date

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def form():
    if request.method == "POST":
        try:
            data = request.form

            address = data.get("address", "")
            object_name = data.get("object_name", "")
            material = data.get("material", "")
            base_layer = data.get("base_layer") or None
            date_str = data.get("date", str(date.today()))
            area = float(data.get("area") or 0)

            # Цены
            material_prices = {
                "PERLATA": 54200,
                "TACTITE": 72000,
                "LimeWash": 28000,
                "ISTRIA": 10563
            }
            mat_price = material_prices.get(material, 0)
            mat_qty = int(float(data.get("material_qty") or 0))
            mat_cost = round(mat_qty * mat_price, 2)

            aquawax_qty = int(float(data.get("aquawax_qty") or 0))
            aquawax_cost = float(data.get("aquawax_cost") or 0)
            aquawax_price = round(aquawax_cost / aquawax_qty, 2) if aquawax_qty else 0

            base_qty = int(float(data.get("base_qty") or 0))
            base_cost = float(data.get("base_cost") or 0)
            base_price = round(base_cost / base_qty, 2) if base_qty else 0

            include_work = 'include_work' in data
            work_price = float(data.get("work_price") or 0)
            work_sum = round(area * work_price, 2) if include_work else 0

            extra_cost = float(data.get("extra_cost") or 0)
            extra_qty = math.ceil(extra_cost / 12000) if extra_cost else 0

            primer_cost = float(data.get("primer_cost") or 0)
            primer_qty = math.ceil(primer_cost / 2500) if primer_cost else 0

            material_full_names = {
                "PERLATA": 'PERLATA PLS',
                "TACTITE": 'TACTITE',
                "LimeWash": 'LimeWash',
                "ISTRIA": 'ISTRIA P350'
            }
            material_name = material_full_names.get(material, material)

            total = sum([
                mat_cost,
                aquawax_cost,
                base_cost,
                work_sum,
                extra_cost,
                primer_cost
            ])

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
                                   aquawax_cost=aquawax_cost,
                                   aquawax_price=aquawax_price,
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
        except Exception as e:
            return f"<h3>Ошибка при обработке формы:</h3><pre>{e}</pre>", 500

    return render_template("form.html", current_date=date.today())
