from flask import Flask, jsonify, request, abort, send_from_directory
from flask_cors import CORS

app = Flask(__name__)


CORS(app) 

# In-memory "database"
products = [
    {"id": 1, "name": "Laptop", "price": 999.99, "quantity": 10},
    {"id": 2, "name": "Mouse",  "price": 25.50,  "quantity": 50},
]
next_id = 3


def find_product(pid):
    return next((p for p in products if p["id"] == pid), None)


# ── GET /products ──────────────────────────────────────────────────────────────
@app.route("/products", methods=["GET"])
def get_products():
    return jsonify(products), 200


# ── GET /products/<id> ─────────────────────────────────────────────────────────
@app.route("/products/<int:pid>", methods=["GET"])
def get_product(pid):
    product = find_product(pid)
    if not product:
        abort(404, description="Product not found")
    return jsonify(product), 200


# ── POST /products ─────────────────────────────────────────────────────────────
@app.route("/products", methods=["POST"])
def create_product():
    global next_id
    data = request.get_json(silent=True)
    if not data or "name" not in data or "price" not in data:
        abort(400, description="name and price are required")
    product = {
        "id":       next_id,
        "name":     data["name"],
        "price":    float(data["price"]),
        "quantity": int(data.get("quantity", 0)),
    }
    products.append(product)
    next_id += 1
    return jsonify(product), 201


# ── PUT /products/<id> ─────────────────────────────────────────────────────────
@app.route("/products/<int:pid>", methods=["PUT"])
def update_product(pid):
    product = find_product(pid)
    if not product:
        abort(404, description="Product not found")
    data = request.get_json(silent=True) or {}
    product["name"]     = data.get("name",     product["name"])
    product["price"]    = float(data.get("price",    product["price"]))
    product["quantity"] = int(data.get("quantity", product["quantity"]))
    return jsonify(product), 200


# ── DELETE /products/<id> ──────────────────────────────────────────────────────
@app.route("/products/<int:pid>", methods=["DELETE"])
def delete_product(pid):
    product = find_product(pid)
    if not product:
        abort(404, description="Product not found")
    products.remove(product)
    return jsonify({"message": "Product deleted"}), 200


# ── Health check ───────────────────────────────────────────────────────────────
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


# ── Error handlers ─────────────────────────────────────────────────────────────
@app.errorhandler(400)
def bad_request(e):
    return jsonify({"error": str(e.description)}), 400

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": str(e.description)}), 404

# ──ajouter une route / qui renvoie le fichier index.html ───
@app.route("/")
def index():
    return send_from_directory('templates', 'index.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
