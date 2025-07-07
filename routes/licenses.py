from flask import Blueprint, request, jsonify
from database import get_db_connection

license_bp = Blueprint('license_bp', __name__)

@license_bp.route("/add", methods=["POST"])
def add_license():
    data = request.json
    name = data["name"]
    expiry_date = data["expiry_date"]
    email = data["alert_email"]

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO licenses (name, expiry_date, alert_email) VALUES (?, ?, ?)", (name, expiry_date, email))
    conn.commit()
    conn.close()
    return jsonify({"status": "License added"}), 201

@license_bp.route("/update/<int:id>", methods=["PUT"])
def update_license(id):
    data = request.json
    name = data["name"]
    expiry_date = data["expiry_date"]
    email = data["alert_email"]

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE licenses SET name = ?, expiry_date = ?, alert_email = ? WHERE id = ?", (name, expiry_date, email, id))
    conn.commit()
    conn.close()
    return jsonify({"status": "License updated"})

@license_bp.route("/delete/<int:id>", methods=["DELETE"])
def delete_license(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM licenses WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return jsonify({"status": "License deleted"})

@license_bp.route("/list", methods=["GET"])
def list_licenses():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, expiry_date, alert_email FROM licenses")
    rows = cursor.fetchall()
    conn.close()

    license_list = [{
        "id": lid,
        "name": name,
        "expiry_date": expiry,
        "alert_email": email
    } for lid, name, expiry, email in rows]

    return jsonify(license_list)
