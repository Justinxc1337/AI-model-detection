from flask import Flask, render_template, request, redirect, url_for
import os

app = Flask(__name__)

USER_CREDENTIALS = {
    "admin": "password"
}

@app.route('/')
def login_page():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
        return redirect(url_for('dashboard_page'))
    else:
        return "Invalid login. Try again.", 401

@app.route('/dashboard')
def dashboard_page():
    static_folder_path = os.path.join(os.getcwd(), "static", "images")
    info_file = os.path.join(static_folder_path, "detection_info.txt")

    if os.path.exists(info_file):
        with open(info_file, "r") as f:
            original_image, annotated_image, detection_time = f.read().strip().split(',')
        return render_template('dashboard.html',
                               original_image=original_image,
                               annotated_image=annotated_image,
                               detection_time=detection_time)
    else:
        return render_template('dashboard.html',
                               original_image=None,
                               annotated_image=None,
                               detection_time=None)

if __name__ == "__main__":
    app.run(debug=True)
