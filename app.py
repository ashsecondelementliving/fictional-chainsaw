import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template, request, send_file
import os
import uuid
from flask_socketio import SocketIO
from FormatLead import formatLeadpy  
from mapper import mapperMain
from ZoptoSender import zoptoSenderpy 
from eventlet.semaphore import Semaphore
send_lock = Semaphore(1)

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/download_formatted_campaign", methods=["POST"])
def download_formatted_campaign():
    if "file" not in request.files:
        return "No file uploaded", 400

    file = request.files["file"]
    if file.filename == "":
        return "Invalid file name", 400

    session_id = str(uuid.uuid4())
    campaign_filepath = f"/tmp/{session_id}_ZoptoLeads.csv"
    formatted_filepath = f"/tmp/{session_id}_ParsedLeads.csv"

    file.save(campaign_filepath)
    formatLeadpy(campaign_filepath, formatted_filepath)

    if os.path.exists(formatted_filepath):
        response = send_file(formatted_filepath, as_attachment=True)

        @response.call_on_close
        def cleanup():
            try:
                os.remove(campaign_filepath)
                os.remove(formatted_filepath)
            except Exception as e:
                print("Cleanup error:", e)

        return response

    return "File processing failed", 500

@app.route("/download_ai_messages", methods=["POST"])
def download_ai_messages():
    if "file" not in request.files:
        return "No file uploaded.", 400

    file = request.files["file"]
    if file.filename == "":
        return "No file selected.", 400

    sender_name = request.form.get("username", "").strip()
    if not sender_name:
        return "Error: Name field is empty. Please enter your name.", 400

    session_id = str(uuid.uuid4())
    filled_leads_filepath = f"/tmp/{session_id}_ParsedLeads.csv"
    ai_messages_filepath = f"/tmp/{session_id}_OutputMessages.csv"

    file.save(filled_leads_filepath)
    mapperMain(sender_name, filled_leads_filepath, ai_messages_filepath, socketio)

    if os.path.exists(ai_messages_filepath):
        socketio.emit("download_complete")
        socketio.emit("ai_file_ready", {"path": ai_messages_filepath})  
        response = send_file(ai_messages_filepath, as_attachment=True)

        @response.call_on_close
        def cleanup():
            try:
                os.remove(filled_leads_filepath)
                os.remove(ai_messages_filepath)
            except Exception as e:
                print("Cleanup error:", e)

        return response

    return "File not found", 404

@app.route("/send_ai_messages", methods=["POST"])
def send_ai_messages():
    if not send_lock.acquire(blocking=False):
        return {"error": "A send is already in progress."}, 409
    try:
        api_key = request.form.get("ZoptoKey", "").strip()
        output_file = request.form.get("output_file", "").strip()

        if not api_key:
            return {"error": "Error: No API key provided."}, 400
        if not output_file or not os.path.exists(output_file):
            return {"error": "No AI messages file found."}, 404

        queued, skipped = zoptoSenderpy(api_key, output_file)

        if queued == 0:
            return {
                "error": "No messages queued (duplicates/empty/filtered).",
                "queued": queued,
                "skipped": skipped
            }, 400

        return {"success": f"Queued {queued} messages.", "skipped": skipped}
    finally:
        send_lock.release()

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=10000, debug=True)
