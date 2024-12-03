import threading
import subprocess

def run_main():
    subprocess.run(["python", "main.py"])

def run_app():
    subprocess.run(["python", "app.py"])

if __name__ == "__main__":
    main_thread = threading.Thread(target=run_main)
    app_thread = threading.Thread(target=run_app)

    main_thread.start()
    app_thread.start()

    main_thread.join()
    app_thread.join()
