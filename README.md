fixes <br>

run use python run.py <br>

virtual environment ('venv': venv) <br>

python interpreter <br>

# AI Object Detection using YoloV8

This application is a proof of concept for a real-time AI-powered object detection system. The solution uses YOLOv8 for detecting specific objects (e.g., knives and people) and includes functionality to send email alerts with both the original and annotated images. The application features a basic web interface and a hardcoded login system.

## Features

- **Real-Time Detection**: Utilizes YOLOv8 to detect objects in live video feeds with minimal latency.
- **Email Alerts**: Sends email notifications with the original and annotated images attached when a knife is detected.
- **Basic Web Interface**: A Flask-powered frontend to display detections.
- **Proof of Concept**: Login credentials and Gmail configurations are hardcoded for demonstration purposes.

## Limitations

This application is designed as a proof of concept and includes the following limitations:
- Login credentials are hardcoded in the application.
- Gmail email address and app password are stored in a `config.json` file excluded from the repository via `.gitignore`.
- No database integration; all detection data is stored locally.
- Basic error handling.

## Getting Started

### Prerequisites

1. **Python**: Install Python 3.8 or higher.
2. **Pip**: Ensure `pip` is installed for managing Python dependencies.
3. **Gmail Configuration**:
   - Enable "App Passwords" for your Gmail account.
   - Generate an app password and save it in a `config.json` file as described below.

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/ai-object-detection.git
   cd ai-object-detection
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `config.json` file in the root directory:
   ```json
   {
       "sender_email": "your_email@gmail.com",
       "receiver_email": "receiver_email@gmail.com",
       "app_password": "your_app_password"
   }
   ```

4. Ensure `config.json` is excluded from version control by adding it to `.gitignore`.

### Running the Application

1. Start the application:
   ```bash
   python run.py
   ```
1.5. run.py doesn't work yet, use second method - Start the YoloV8 AI Model and then the frontend UI:
  ```bash
   python main.py
   ```
  ```bash
   python app.py
   ```

2. Open the web interface:
   - Navigate to [http://127.0.0.1:5000](http://127.0.0.1:5000).

3. Login using the hardcoded credentials:
   - **Username**: `admin`
   - **Password**: `admin`

### Detection Alerts

When a knife is detected:
1. The system saves both the original and annotated images in the `static/images` directory.
2. An email alert is sent to the specified recipient with the images attached.
3. An SMS alert (not available)

## Folder Structure

```
project_root/
|-- app.py                  # Flask application
|-- main.py                 # YOLOv8 detection script
|-- run.py                  # Script to run both Flask and detection scripts
|-- config.json             # Gmail credentials (excluded from GitHub)
|-- templates/
|   |-- login.html          # Login page
|   |-- dashboard.html      # Detection dashboard
|-- static/
|   |-- css/
|   |   |-- styles.css      # Styles for the dashboard
|   |-- images/
|       |-- original/       # Original detection images
|       |-- annotated/      # Annotated detection images
|       |-- detection_info.txt  # Metadata for the latest detection
|-- requirements.txt        # Python dependencies
```

## Technologies Used

- **Python**: Programming language for detection and backend logic.
- **YOLOv8**: Real-time object detection model.
- **Flask**: Lightweight web framework for building the frontend.
- **OpenCV**: Video processing library for handling camera feeds.
- **Supervision**: Library for annotating detections with bounding boxes.

## Future Enhancements

- Replace hardcoded login and email credentials with environment variables or database integration.
- Add SMS notifications using services.
- Improve error handling and logging.
- Integrate a database for persistent storage of detections.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.

---

**Developed as part of a Datamatiker Final Project**
