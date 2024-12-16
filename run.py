import threading
import webbrowser
from main import ObjectDetection
from app import app

def run_main():
    detector = ObjectDetection(capture_index=0)
    detector()

def run_app():
    app.run(debug=True, use_reloader=False)  # Disable the reloader to avoid conflicts

if __name__ == "__main__":
    webbrowser.open("http://127.0.0.1:5000")

    main_thread = threading.Thread(target=run_main)
    app_thread = threading.Thread(target=run_app)

    main_thread.start()
    app_thread.start()

    main_thread.join()
    app_thread.join()
#Doesn't work