from flask import Blueprint, request, jsonify
from database import get_db_connection
from certificate_utils import get_cert_expiry
from datetime import datetime
from urllib.parse import urlparse
from logger import logger  # ✅ Import the shared logger
import re

service_bp = Blueprint('service_bp', __name__)


def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme in ['http', 'https'], result.netloc])
    except ValueError:
        return False


def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_emails(email_string):
    emails = [e.strip() for e in email_string.split(',')]
    for email in emails:
        if not email:
            continue
        if not is_valid_email(email):
            return False
    return True


@service_bp.route("/add", methods=["POST"])
def add_service():
    data = request.json
    logger.info("Add service request received.")

    if not all(key in data for key in ['name', 'url', 'alert_email']):
        logger.warning("Missing required fields.")
        return jsonify({"error": "Missing required fields (name, url, alert_email)"}), 400

    name = data["name"].strip()
    url = data["url"].strip().lower()
    email = data["alert_email"].strip()

    if len(name) < 3 or len(name) > 50:
        logger.warning(f"Invalid name length: {name}")
        return jsonify({"error": "Name must be between 3 and 50 characters"}), 400

    if not is_valid_url(url):
        logger.warning(f"Invalid URL format: {url}")
        return jsonify({"error": "Invalid URL format. Must include http:// or https://"}), 400

    if not validate_emails(email):
        logger.warning(f"Invalid email(s): {email}")
        return jsonify({"error": "One or more email addresses are invalid"}), 400

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM services WHERE name = ?", (name,))
        if cursor.fetchone():
            logger.warning(f"Service name already exists: {name}")
            return jsonify({"error": "Service name already exists"}), 409

        cursor.execute("SELECT id FROM services WHERE url = ?", (url,))
        if cursor.fetchone():
            logger.warning(f"URL already exists: {url}")
            return jsonify({"error": "URL already exists"}), 409

        expiry_str = None
        try:
            expiry = get_cert_expiry(url)
            expiry_str = expiry.strftime("%Y-%m-%d")
        except Exception as e:
            logger.error(f"Certificate check failed for {url}: {e}")

        cursor.execute(
            "INSERT INTO services (name, url, alert_email, certificate_expiry) VALUES (?, ?, ?, ?)",
            (name, url, email, expiry_str)
        )
        conn.commit()

        logger.info(f"Service added: {name} ({url})")
        return jsonify({
            "status": "Service added",
            "certificate_expiry": expiry_str,
            "service": {
                "name": name,
                "url": url,
                "alert_email": email
            }
        }), 201

    except Exception as e:
        logger.error(f"Error adding service: {e}")
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    finally:
        if conn:
            conn.close()


@service_bp.route("/update/<int:id>", methods=["PUT"])
def update_service(id):
    data = request.json
    logger.info(f"Update request received for service ID {id}.")

    if not all(key in data for key in ['name', 'url', 'alert_email']):
        return jsonify({"error": "Missing required fields (name, url, alert_email)"}), 400

    name = data["name"].strip()
    url = data["url"].strip().lower()
    email = data["alert_email"].strip()

    if len(name) < 3 or len(name) > 50:
        return jsonify({"error": "Name must be between 3 and 50 characters"}), 400

    if not is_valid_url(url):
        return jsonify({"error": "Invalid URL format. Must include http:// or https://"}), 400

    if not validate_emails(email):
        return jsonify({"error": "One or more email addresses are invalid"}), 400

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM services WHERE id = ?", (id,))
        if not cursor.fetchone():
            logger.warning(f"Service ID not found: {id}")
            return jsonify({"error": "Service not found"}), 404

        cursor.execute("SELECT id FROM services WHERE name = ? AND id != ?", (name, id))
        if cursor.fetchone():
            return jsonify({"error": "Service name already exists"}), 409

        cursor.execute("SELECT id FROM services WHERE url = ? AND id != ?", (url, id))
        if cursor.fetchone():
            return jsonify({"error": "URL already exists"}), 409

        expiry_str = None
        try:
            expiry = get_cert_expiry(url)
            expiry_str = expiry.strftime("%Y-%m-%d")
        except Exception as e:
            logger.error(f"Certificate check failed during update: {e}")

        cursor.execute(
            "UPDATE services SET name = ?, url = ?, alert_email = ?, certificate_expiry = ? WHERE id = ?",
            (name, url, email, expiry_str, id)
        )
        conn.commit()

        logger.info(f"Service updated: ID {id}, name {name}")
        return jsonify({
            "status": "Service updated",
            "certificate_expiry": expiry_str,
            "service": {
                "id": id,
                "name": name,
                "url": url,
                "alert_email": email
            }
        }), 200

    except Exception as e:
        logger.error(f"Error updating service ID {id}: {e}")
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    finally:
        if conn:
            conn.close()


@service_bp.route("/delete/<int:id>", methods=["DELETE"])
def delete_service(id):
    logger.info(f"Delete request for service ID {id}")
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM services WHERE id = ?", (id,))
        if not cursor.fetchone():
            logger.warning(f"Service not found for deletion: ID {id}")
            return jsonify({"error": "Service not found"}), 404

        cursor.execute("DELETE FROM services WHERE id = ?", (id,))
        conn.commit()
        logger.info(f"Service deleted: ID {id}")
        return jsonify({"status": "Service deleted"}), 200
    except Exception as e:
        logger.error(f"Error deleting service ID {id}: {e}")
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    finally:
        if conn:
            conn.close()


@service_bp.route("/list", methods=["GET"])
def list_services():
    logger.info("List services requested.")
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, url, alert_email, certificate_expiry FROM services")
        rows = cursor.fetchall()

        service_list = [{
            "id": sid,
            "name": name,
            "url": url,
            "alert_email": email,
            "certificate_expiry": expiry
        } for sid, name, url, email, expiry in rows]

        logger.info(f"Returned {len(service_list)} services.")
        return jsonify(service_list)
    except Exception as e:
        logger.error(f"Error listing services: {e}")
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    finally:
        if conn:
            conn.close()


@service_bp.route("/fetch-expiry/<int:id>", methods=["POST"])
def fetch_expiry(id):
    logger.info(f"Manual expiry fetch for service ID {id}")
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT url FROM services WHERE id = ?", (id,))
        row = cursor.fetchone()
        if not row:
            logger.warning(f"Service not found for expiry fetch: ID {id}")
            return jsonify({"error": "Service not found"}), 404

        url = row[0]
        try:
            expiry = get_cert_expiry(url)
            expiry_str = expiry.strftime("%Y-%m-%d")
            cursor.execute("UPDATE services SET certificate_expiry = ? WHERE id = ?", (expiry_str, id))
            conn.commit()
            logger.info(f"Updated expiry for service ID {id} → {expiry_str}")
            return jsonify({
                "status": "Expiry date updated",
                "certificate_expiry": expiry_str
            }), 200
        except Exception as e:
            logger.error(f"Error fetching expiry for service ID {id}: {e}")
            return jsonify({"error": str(e)}), 500
    except Exception as e:
        logger.error(f"Database error during expiry fetch: {e}")
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    finally:
        if conn:
            conn.close()
