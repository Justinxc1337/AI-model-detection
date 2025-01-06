import torch
import numpy as np
import cv2
from time import time
from ultralytics import YOLO
import os
import time
from datetime import datetime, timezone, timedelta

from supervision.draw.color import ColorPalette
from supervision import Detections, BoxAnnotator
import supervision as sv

import smtplib
import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# Currently hardcoded for each instance of the program and where it is running
Country = "Denmark"
City = "Næstved"
Company = "Zealand Sjællands Erhvervsakademi"
Location = "Main Entrance"

class ObjectDetection:

    def __init__(self, capture_index):
        self.capture_index = capture_index
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print(f"Device: {self.device}")
        self.model = self.load_model()
        self.CLASS_NAMES_DICT = self.model.names
        self.box_annotator = BoxAnnotator(color=sv.ColorPalette.DEFAULT, thickness=3)
        self.last_detection_time = 0  # Track the last time an image was saved (in seconds)

        self.box_annotator = BoxAnnotator(
            color=sv.ColorPalette.DEFAULT,
            thickness=3
        )
        
    def load_config(self):
        try:
            with open("config.json", "r") as config_file:
                config = json.load(config_file)
            return config
        except Exception as e:
            print(f"Failed to load config.json: {e}")
            return None

    def send_email(self, original_path, annotated_path, formatted_timestamp):
        config = self.load_config()
        if not config:
            print("Email not sent: Configuration file is missing or invalid.")
            return

        try:
            sender_email = config["sender_email"]
            receiver_email = config["receiver_email"]
            password = config["app_password"]

            # Content included in the email
            subject = f"Knife Detection Alert {Company}, {Location}"
            body = f"""Knife detected at {formatted_timestamp}. From {Country}, {City}, at {Company}, Camera location - {Location}.
                \nBoth images attached: Original and Annotated.
                \nRed boxes indicate the detected dangerous objects and purple boxes indicate the detected people."""


            # Setting up the email 
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = receiver_email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain', 'utf-8'))

            # Original image attachment (the image without AI boxes)
            with open(original_path, 'rb') as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f"attachment; filename={original_path.split('/')[-1]}")
            msg.attach(part)

            # Annotation image attachment (the image with AI boxes)
            with open(annotated_path, 'rb') as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f"attachment; filename={annotated_path.split('/')[-1]}")

            msg.attach(part)

            # Send email using Gmail SMTP server
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(sender_email, password)
                server.send_message(msg)

            print("Email sent successfully!")
        except Exception as e:
            print(f"Failed to send email: {e}")

        
    def load_model(self):
        model = YOLO("yolov8l.pt")
        model.fuse()
        return model
    
    def predict(self, frame):
        results = self.model(frame)
        return results
    
    def plot_bboxes(self, results, frame):
        # focused_objects_ids removes unwanted classes/object boxes from the frame, only focusing on the intended detection
        # id 0 = "person", id 43 = "knife"
        focused_objects_ids = [0, 43]
        xyxys = results[0].boxes.xyxy.cpu().numpy()
        confidences = results[0].boxes.conf.cpu().numpy()
        class_ids = results[0].boxes.cls.cpu().numpy().astype(int)

        mask = np.isin(class_ids, focused_objects_ids)
        filtered_xyxys = xyxys[mask]
        filtered_confidences = confidences[mask]
        filtered_class_ids = class_ids[mask]

        detections = Detections(
            xyxy=filtered_xyxys,
            confidence=filtered_confidences,
            class_id=filtered_class_ids
        )
        
        annotated_frame = self.box_annotator.annotate(scene=frame.copy(), detections=detections)
        
        # Check for knife detection (object id 43)
        knife_detected = 43 in filtered_class_ids
        current_time = time.time()
        
        if knife_detected and (current_time - self.last_detection_time > 10):  # 10-second delay
            print("ALERT: Knife detected!")
            self.last_detection_time = current_time  # Update last detection time
            self.send_alert(frame, annotated_frame)

        self.labels = [
            f"{self.CLASS_NAMES_DICT[class_id]}: {confidence:.2f}"
            for class_id, confidence in zip(detections.class_id, detections.confidence)
        ]

        return annotated_frame
    
    # Save a frame when a knife is detected as jpg and rewrites the file each time a new knife is detected
    # Rewriting jpg file is done to avoid saving multiple images of the same knife detection
    def send_alert(self, frame, annotated_frame):
        cet_time = datetime.now(timezone.utc) + timedelta(hours=1)
        formatted_date = cet_time.strftime("%dD, %mM, %YY")
        formatted_time = cet_time.strftime("%HH, %MM, %SS")
        formatted_timestamp = f"{formatted_date}, {formatted_time}"

        static_folder_path = os.path.join(os.getcwd(), "static", "images")
        original_folder_path = os.path.join(static_folder_path, "original")
        annotated_folder_path = os.path.join(static_folder_path, "annotated")

        os.makedirs(original_folder_path, exist_ok=True)
        os.makedirs(annotated_folder_path, exist_ok=True)

        original_filename = f"alert_knife_detected_{formatted_date}_{formatted_time}.jpg"
        annotated_filename = f"alert_knife_detected_annotated_{formatted_date}_{formatted_time}.jpg"

        original_path = os.path.join(original_folder_path, original_filename)
        annotated_path = os.path.join(annotated_folder_path, annotated_filename)

        cv2.imwrite(original_path, frame)
        cv2.imwrite(annotated_path, annotated_frame)

        # Save metadata for frontend
        with open(os.path.join(static_folder_path, "detection_info.txt"), "w") as f:
            f.write(f"{original_filename},{annotated_filename},{formatted_timestamp}")

        # Notify via email
        self.send_email(original_path, annotated_path, formatted_timestamp)



    
    def __call__(self):
        cap = cv2.VideoCapture(self.capture_index)
        assert cap.isOpened()
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        while True:
            start_time = time.time()
            ret, frame = cap.read()
            assert ret

            results = self.predict(frame)
            frame = self.plot_bboxes(results, frame)

            end_time = time.time()
            fps = 1 / np.round(end_time - start_time, 2)
            cv2.putText(frame, f"FPS: {fps}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            cv2.imshow('YOLOv8 Detection', frame)
            if cv2.waitKey(5) & 0xFF == 27: 
                break

        cap.release()
        cv2.destroyAllWindows()


detector = ObjectDetection(capture_index=0)
detector()
