from flask import Blueprint, request, jsonify
from database import get_db_connection
from certificate_utils import get_cert_expiry
from datetime import datetime

service_bp = Blueprint('service_bp', __name__)

@service_bp.route("/add", methods=["POST"])
def add_service():
    data = request.json
    name = data["name"]
    url = data["url"]
    email = data["alert_email"]

    try:
        expiry = get_cert_expiry(url)
        expiry_str = expiry.strftime("%Y-%m-%d")
    except Exception as e:
        expiry_str = None

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO services (name, url, alert_email, certificate_expiry) VALUES (?, ?, ?, ?)", (name, url, email, expiry_str))
    conn.commit()
    conn.close()
    return jsonify({"status": "Service added", "certificate_expiry": expiry_str}), 201

@service_bp.route("/update/<int:id>", methods=["PUT"])
def update_service(id):
    data = request.json
    name = data["name"]
    url = data["url"]
    email = data["alert_email"]
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE services SET name = ?, url = ?, alert_email = ? WHERE id = ?", (name, url, email, id))
    conn.commit()
    conn.close()
    return jsonify({"status": "Service updated"})

@service_bp.route("/delete/<int:id>", methods=["DELETE"])
def delete_service(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM services WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return jsonify({"status": "Service deleted"})

@service_bp.route("/list", methods=["GET"])
def list_services():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, url, alert_email, certificate_expiry FROM services")
    rows = cursor.fetchall()
    conn.close()

    service_list = [{
        "id": sid,
        "name": name,
        "url": url,
        "alert_email": email,
        "certificate_expiry": expiry
    } for sid, name, url, email, expiry in rows]

    return jsonify(service_list)

@service_bp.route("/fetch-expiry/<int:id>", methods=["POST"])
def fetch_expiry(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT url FROM services WHERE id = ?", (id,))
    row = cursor.fetchone()
    if not row:
        return jsonify({"error": "Service not found"}), 404

    url = row[0]
    try:
        expiry = get_cert_expiry(url)
        expiry_str = expiry.strftime("%Y-%m-%d")
        cursor.execute("UPDATE services SET certificate_expiry = ? WHERE id = ?", (expiry_str, id))
        conn.commit()
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

    return jsonify({"status": "Expiry date updated", "certificate_expiry": expiry_str})
