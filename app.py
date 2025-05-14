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

        mat_qty = int(data.get("material_qty", 0))
        mat_cost = int(data.get("material_cost", 0))
        base_qty = data.get("base_qty")
        base_cost = data.get("base_cost")

        total = mat_cost
        if base_cost:
            base_qty = int(base_qty)
            base_cost = int(base_cost)
            total += base_cost
        else:
            base_qty = base_cost = None

        html = render_template("offer.html",
                               address=address,
                               object_name=object_name,
                               material=material,
                               mat_qty=mat_qty,
                               mat_cost=mat_cost,
                               base_layer=base_layer,
                               base_qty=base_qty,
                               base_cost=base_cost,
                               total=total,
                               date_str=date_str)
        pdf = HTML(string=html).write_pdf()
        return send_file(io.BytesIO(pdf), mimetype="application/pdf",
                         download_name="Коммерческое_предложение.pdf")
    return render_template("form.html", current_date=date.today())
