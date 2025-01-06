import os
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for session handling

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


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
