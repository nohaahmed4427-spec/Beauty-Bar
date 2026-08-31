from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import sqlite3
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

DATABASE = "data/beauty_bar.db"

UPLOAD_FOLDER = "data/products"

ALLOWED_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg",
    "webp"
}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def get_db_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def create_database():
    os.makedirs("data", exist_ok=True)

    connection = get_db_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            description TEXT,
            image TEXT,
            category TEXT NOT NULL,
            stock_status TEXT NOT NULL DEFAULT 'Available'
        )
    """)

    # Add stock_status to old databases that were created before this field existed
    columns = connection.execute(
        "PRAGMA table_info(products)"
    ).fetchall()

    column_names = [column["name"] for column in columns]

    if "stock_status" not in column_names:
        connection.execute("""
            ALTER TABLE products
            ADD COLUMN stock_status TEXT NOT NULL DEFAULT 'Available'
        """)

    connection.commit()
    connection.close()


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in ALLOWED_EXTENSIONS
    )


@app.route("/")
def home():
    return jsonify({
        "message": "Beauty Bar Backend is running!"
    })


@app.route("/api/services")
def services():
    return jsonify({
        "services": [
            "Facial Care",
            "Acne Care",
            "Skin Hydration",
            "Skin Cleansing",
            "Sun Protection"
        ]
    })


# Get all products
@app.route("/api/products", methods=["GET"])
def get_products():

    connection = get_db_connection()

    products = connection.execute(
        "SELECT * FROM products ORDER BY id DESC"
    ).fetchall()

    connection.close()

    result = []

    for product in products:

        item = dict(product)

        if item["image"]:
            item["image"] = (
                "http://127.0.0.1:5000/"
                + item["image"].replace("\\", "/")
            )

        result.append(item)

    return jsonify(result)


# Add a new product
@app.route("/api/products", methods=["POST"])
def add_product():

    name = request.form.get("name", "").strip()
    price = request.form.get("price")
    description = request.form.get("description", "").strip()
    category = request.form.get("category", "").strip()

    stock_status = request.form.get(
        "stock_status",
        "Available"
    ).strip()

    image = request.files.get("image")

    if not name or not price or not category:
        return jsonify({
            "error": "Name, price, and category are required"
        }), 400

    if stock_status not in ["Available", "Out of Stock"]:
        return jsonify({
            "error": "Invalid stock status"
        }), 400

    try:

        price = float(price)

        if price < 0:
            raise ValueError

    except ValueError:

        return jsonify({
            "error": "Price must be a valid positive number"
        }), 400


    image_path = ""

    if image and image.filename:

        if not allowed_file(image.filename):

            return jsonify({
                "error":
                    "Only PNG, JPG, JPEG, and WEBP images are allowed"
            }), 400

        filename = secure_filename(
            image.filename
        )

        base, extension = os.path.splitext(
            filename
        )

        counter = 1

        final_filename = filename

        while os.path.exists(
            os.path.join(
                app.config["UPLOAD_FOLDER"],
                final_filename
            )
        ):

            final_filename = (
                f"{base}_{counter}{extension}"
            )

            counter += 1

        image.save(
            os.path.join(
                app.config["UPLOAD_FOLDER"],
                final_filename
            )
        )

        image_path = (
            f"uploads/{final_filename}"
        )


    connection = get_db_connection()

    cursor = connection.execute("""
        INSERT INTO products
        (
            name,
            price,
            description,
            image,
            category,
            stock_status
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        name,
        price,
        description,
        image_path,
        category,
        stock_status
    ))

    connection.commit()

    product_id = cursor.lastrowid

    connection.close()

    return jsonify({
        "message": "Product added successfully",
        "product_id": product_id
    }), 201


# Update product stock status
@app.route(
    "/api/products/<int:product_id>/stock",
    methods=["PUT"]
)
def update_stock(product_id):

    data = request.get_json()

    if not data:
        return jsonify({
            "error": "No data provided"
        }), 400

    stock_status = data.get("stock_status")

    if stock_status not in ["Available", "Out of Stock"]:
        return jsonify({
            "error": "Invalid stock status"
        }), 400

    connection = get_db_connection()

    cursor = connection.execute(
        """
        UPDATE products
        SET stock_status = ?
        WHERE id = ?
        """,
        (
            stock_status,
            product_id
        )
    )

    connection.commit()

    updated = cursor.rowcount

    connection.close()

    if updated == 0:
        return jsonify({
            "error": "Product not found"
        }), 404

    return jsonify({
        "message": "Stock status updated successfully"
    })


# Serve uploaded images
@app.route("/uploads/<filename>")
def uploaded_file(filename):

    return send_from_directory(
        app.config["UPLOAD_FOLDER"],
        filename
    )


if __name__ == "__main__":

    create_database()

    app.run(debug=True)