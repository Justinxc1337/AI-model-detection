from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os
import json

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Hardcoded user credentials for proof of concept
USER_CREDENTIALS = {
    "admin": "password"
}

@app.route('/')
def login_page():
    # Redirect to the dashboard if already logged in
    if 'logged_in' in session and session['logged_in']:
        return redirect(url_for('dashboard_page'))
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
        session['logged_in'] = True
        return redirect(url_for('dashboard_page'))
    else:
        return render_template('login.html', error="Invalid username or password.")

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login_page'))

@app.route('/dashboard')
def dashboard_page():
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('login_page'))

    static_folder_path = os.path.join(os.getcwd(), "static", "images")
    original_folder_path = os.path.join(static_folder_path, "original")
    annotated_folder_path = os.path.join(static_folder_path, "annotated")

    # Gather all available images
    image_list = []
    for filename in os.listdir(original_folder_path):
        if filename.endswith(".jpg"):
            # Extract timestamp and format for display
            timestamp = filename.replace("alert_knife_detected_", "").replace(".jpg", "")
            formatted_timestamp = timestamp.replace("_", ", ")
            image_list.append({
                "timestamp": timestamp,
                "formatted_timestamp": formatted_timestamp,
                "original": filename,
                "annotated": f"alert_knife_detected_annotated_{timestamp}.jpg"
            })

    # Sort images by timestamp (latest first)
    image_list = sorted(image_list, key=lambda x: x['timestamp'], reverse=True)

    # Get the selected image (default to the latest image)
    selected_timestamp = request.args.get('timestamp', image_list[0]['timestamp'] if image_list else None)
    selected_image = next((img for img in image_list if img['timestamp'] == selected_timestamp), None)

    return render_template(
        'dashboard.html',
        image_list=image_list,
        selected_image=selected_timestamp,
        selected_formatted_timestamp=selected_image['formatted_timestamp'] if selected_image else None,
        selected_original=selected_image['original'] if selected_image else None,
        selected_annotated=selected_image['annotated'] if selected_image else None
    )
    
from urllib.parse import unquote

@app.route('/send_email', methods=['POST'])
def send_email():
    data = request.json
    email = data.get('email')
    # Decode both URL-encoded filenames
    original_image = unquote(data.get('original_image'))
    annotated_image = unquote(data.get('annotated_image'))

    # Path to the images
    static_folder_path = os.path.join(os.getcwd(), "static")
    original_image_path = os.path.join(static_folder_path, original_image.replace("\\", "/"))
    annotated_image_path = os.path.join(static_folder_path, annotated_image.replace("\\", "/"))

    if not os.path.exists(original_image_path) or not os.path.exists(annotated_image_path):
        return jsonify({"success": False, "error": "One or more image files not found."}), 404

    # Load email credentials from config.json
    with open("config.json", "r") as config_file:
        config = json.load(config_file)
        sender_email = config["sender_email"]
        app_password = config["app_password"]

    # Create email
    subject = "Knife Detection Images"
    body = f"Here are the images for the selected detection event:\n\nOriginal: {original_image}\nAnnotated: {annotated_image}"

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    # Attach original image
    with open(original_image_path, 'rb') as attachment:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', f'attachment; filename={original_image.split("/")[-1]}')
    msg.attach(part)

    # Attach annotated image
    with open(annotated_image_path, 'rb') as attachment:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', f'attachment; filename={annotated_image.split("/")[-1]}')
    msg.attach(part)

    # Send email
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, app_password)
            server.send_message(msg)
        return jsonify({"success": True}), 200
    except Exception as e:
        print(f"Failed to send email: {e}")
        return jsonify({"success": False, "error": str(e)}), 500



if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
