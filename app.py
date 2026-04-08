from flask import Flask, request, jsonify, send_file
from pypdf import PdfReader, PdfWriter
import os
import io
import requests
import tempfile

app = Flask(__name__)

# Google Drive direct download URL for the template PDF
TEMPLATE_PDF_ID = "1_Y9k93JtudqOZdfEtWCfyPknd41N-1PT"
TEMPLATE_URL    = f"https://drive.google.com/uc?export=download&id={TEMPLATE_PDF_ID}"

@app.route("/fill-pdf", methods=["POST"])
def fill_pdf():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON body received"}), 400

        field_map   = data.get("fields", {})
        secret      = data.get("secret", "")

        # Simple secret key check to prevent unauthorized use
        expected_secret = os.environ.get("API_SECRET", "legendary2026")
        if secret != expected_secret:
            return jsonify({"error": "Unauthorized"}), 401

        # Download the template PDF from Google Drive
        response = requests.get(TEMPLATE_URL, timeout=30)
        if response.status_code != 200:
            return jsonify({"error": "Could not download template PDF"}), 500

        template_bytes = io.BytesIO(response.content)

        # Fill the PDF
        reader = PdfReader(template_bytes)
        writer = PdfWriter()
        writer.append(reader)

        # Apply field values to all pages
        for page in writer.pages:
            writer.update_page_form_field_values(writer.pages[writer.pages.index(page)], field_map)

        # Save filled PDF to bytes
        output = io.BytesIO()
        writer.write(output)
        output.seek(0)

        return send_file(
            output,
            mimetype="application/pdf",
            as_attachment=True,
            download_name="filled_donation_packet.pdf"
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
