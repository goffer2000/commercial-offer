from flask import Flask, render_template, request, send_file
from weasyprint import HTML
import io, math
from datetime import date

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def form():
    if request.method == "POST":
        data = request.form
        address = data.get("address", "")
        object_name = data.get("object_name", "")
        material = data.get("material", "")
        base_layer = data.get("base_layer") or None
        date_str = data.get("date", str(date.today()))
        area = float(data.get("area") or 0)

        prices = {"PERLATA": 54200, "TACTITE": 72000, "LimeWash": 28000, "ISTRIA": 10563, "AQUAWAX": 59000}
        mat_price = prices.get(material, 0)
        mat_qty = int(float(data.get("material_qty") or 0))
        mat_cost = mat_qty * mat_price

        aquawax_qty = int(float(data.get("aquawax_qty") or 0))
        aquawax_cost = aquawax_qty * prices["AQUAWAX"] if aquawax_qty else 0
        aquawax_price = prices["AQUAWAX"] if aquawax_qty else 0

        base_qty = int(float(data.get("base_qty") or 0))
        base_cost = float(data.get("base_cost") or 0)
        base_price = round(base_cost / base_qty, 2) if base_layer and base_qty else 0

        total = mat_cost + aquawax_cost + base_cost

        return send_file(io.BytesIO(HTML(string=render_template("offer.html",
            address=address, object_name=object_name, material=material,
            material_name={"PERLATA":"PERLATA PLS","TACTITE":"TACTITE","LimeWash":"LimeWash","ISTRIA":"ISTRIA P350"}.get(material, material),
            mat_qty=mat_qty, mat_cost=mat_cost, mat_price=mat_price,
            aquawax_qty=aquawax_qty, aquawax_cost=aquawax_cost, aquawax_price=aquawax_price,
            base_layer=base_layer, base_qty=base_qty, base_cost=base_cost, base_price=base_price,
            total=total, date_str=date_str, area=area)).write_pdf()),
            download_name="Коммерческое_предложение.pdf", mimetype="application/pdf")
    return render_template("form.html", current_date=date.today())
