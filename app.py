import eventlet
eventlet.monkey_patch() 
from flask import Flask, render_template, request, send_file
import os
from flask_socketio import SocketIO
from FormatLead import formatLeadpy  
from mapper import mapperMain
from ZoptoSender import zoptoSenderpy 

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")


def clear_old_files():
    """Remove all CSV files at the start of a new session."""
    for file in os.listdir():
        if file.endswith(".csv"):
            os.remove(file)

clear_old_files()  

@app.route("/", methods=["GET"])
def index():
    """Render the homepage and clear old files for a fresh session."""
    clear_old_files()
    return render_template("index.html")

@app.route("/download_formatted_campaign", methods=["POST"])
def download_formatted_campaign():
    """Processes an uploaded Zopto leads file and provides the formatted campaign for download."""
    if "file" not in request.files:
        return "No file uploaded", 400
    
    file = request.files["file"]
    if file.filename == "":
        return "Invalid file name", 400
    
    campaign_filepath = "ZoptoLeads.csv"
    formatted_filepath = "ParsedLeads.csv"

    file.save(campaign_filepath)

    # Process the campaign file
    formatLeadpy(campaign_filepath)

    if os.path.exists(formatted_filepath):
        socketio.emit("download_complete")  # Notify frontend to stop loading animation
        return send_file(formatted_filepath, as_attachment=True)

    return "File processing failed", 500

@app.route("/download_ai_messages", methods=["POST"])
def download_ai_messages():
    """Processes a filled leads file and generates AI messages for download."""
    if "file" not in request.files:
        return "No file uploaded.", 400
    
    file = request.files["file"]
    if file.filename == "":
        return "No file selected.", 400

    filled_leads_filepath = "ParsedLeads.csv"
    ai_messages_filepath = "OutputMessages.csv"

    file.save(filled_leads_filepath)

    sender_name = request.form.get("username", "").strip()

    if not sender_name:
        return "Error: Name field is empty. Please enter your name.", 400
    
   
    mapperMain(sender_name, filled_leads_filepath, socketio)

    if os.path.exists(ai_messages_filepath):
        socketio.emit("download_complete")  
        return send_file(ai_messages_filepath, as_attachment=True)

    return "File not found", 404

@app.route("/send_ai_messages", methods=["POST"])
def send_ai_messages():
    """Sends AI messages via Zopto API."""
    api_key = request.form.get("ZoptoKey", "").strip()  
    messages_file = "OutputMessages.csv"

    print(f"DEBUG: Received API Key: {api_key}") 

    if not api_key:
        return {"error": "Error: No API key provided."}, 400

    if not os.path.exists(messages_file):
        return {"error": "No AI messages file found."}, 404

    zoptoSenderpy(api_key, messages_file)
                                                                                                   
    return {"success": "AI Messages sent to Zopto!"}

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=10000, debug=True)
