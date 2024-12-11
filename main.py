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
        # Get current time in CET
        cet_time = datetime.now(timezone.utc) + timedelta(hours=1)  # UTC+1 for Danish CET
        timestamp = cet_time.strftime("%Y-%m-%d_%H-%M-%S")
        display_time = cet_time.strftime("%d/%m/%Y %H:%M:%S")

        # Define paths for saving images
        static_folder_path = os.path.join(os.getcwd(), "static", "images")
        os.makedirs(static_folder_path, exist_ok=True)

        # Save the original and annotated images with timestamp
        original_filename = f"alert_knife_detected_{timestamp}.jpg"
        annotated_filename = f"alert_knife_detected_annotated_{timestamp}.jpg"

        cv2.imwrite(os.path.join(static_folder_path, original_filename), frame)
        cv2.imwrite(os.path.join(static_folder_path, annotated_filename), annotated_frame)

        # Save metadata for frontend
        with open(os.path.join(static_folder_path, "detection_info.txt"), "w") as f:
            f.write(f"{original_filename},{annotated_filename},{display_time}")

    
    def __call__(self):
        cap = cv2.VideoCapture(self.capture_index)
        assert cap.isOpened()
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        while True:
            start_time = time.time()  # Corrected
            ret, frame = cap.read()
            assert ret

            results = self.predict(frame)
            frame = self.plot_bboxes(results, frame)

            end_time = time.time()  # Corrected
            fps = 1 / np.round(end_time - start_time, 2)
            cv2.putText(frame, f"FPS: {fps}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            cv2.imshow('YOLOv8 Detection', frame)
            if cv2.waitKey(5) & 0xFF == 27: 
                break

        cap.release()
        cv2.destroyAllWindows()


detector = ObjectDetection(capture_index=0)
detector()
