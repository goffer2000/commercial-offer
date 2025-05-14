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

        materials = {
            "PERLATA": {"rate": 6, "price": 54200, "bases": ["BaseColor Matt", "Marshall Export2"]},
            "TACTITE": {"rate": 9, "price": 72000, "bases": ["BaseColor Satine", "Dulux Bindo20"]},
            "LimeWash": {"rate": 5, "price": 28000, "bases": []},
            "ISTRIA": {"rate": 0.8, "price": 10563, "bases": []}
        }

        base_prices = {
            "BaseColor Matt": {"rate": 9, "price": 27000},
            "BaseColor Satine": {"rate": 9, "price": 27000},
            "Dulux Bindo20": {"rate": 7, "price": 8000},
            "Marshall Export2": {"rate": 7, "price": 4000}
        }

        m = materials[material]
        mat_qty = math.ceil(area / m["rate"])
        mat_cost = mat_qty * m["price"]

        base_qty = base_cost = None
        if base_layer in base_prices:
            base = base_prices[base_layer]
            base_qty = math.ceil(area / base["rate"])
            base_cost = base_qty * base["price"]

        total = mat_cost + (base_cost or 0)

        html = render_template("offer.html", **locals())
        pdf_file = HTML(string=html).write_pdf()

        return send_file(io.BytesIO(pdf_file), mimetype="application/pdf",
                         download_name="Коммерческое_предложение.pdf")

    return render_template("offer.html")

if __name__ == "__main__":
    app.run(debug=True)
