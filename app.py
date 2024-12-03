from flask import Flask, render_template, request, redirect, url_for

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
    return render_template('dashboard.html')

if __name__ == "__main__":
    app.run(debug=True)
