import torch
import numpy as np
import cv2
from time import time
from ultralytics import YOLO
import os

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
        
        knife_detected = 43 in filtered_class_ids
        if knife_detected:
            print("ALERT: Knife detected!")
            self.send_alert(frame)

        self.labels = [
            f"{self.CLASS_NAMES_DICT[class_id]}: {confidence:.2f}"
            for class_id, confidence in zip(detections.class_id, detections.confidence)
        ]

        frame = self.box_annotator.annotate(scene=frame, detections=detections)
        return frame
    
    # Save a frame when a knife is detected as jpg and rewrites the file each time a new knife is detected
    # Rewriting jpg file is done to avoid saving multiple images of the same knife detection
    def send_alert(self, frame):
        static_folder_path = os.path.join(os.getcwd(), "static", "images")
        os.makedirs(static_folder_path, exist_ok=True)
        filename = os.path.join(static_folder_path, "alert_knife_detected.jpg")
        cv2.imwrite(filename, frame)
        print(f"Alert image saved at {filename}")
    
    def __call__(self):
        cap = cv2.VideoCapture(self.capture_index)
        assert cap.isOpened()
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        while True:
            start_time = time()
            ret, frame = cap.read()
            assert ret

            results = self.predict(frame)
            frame = self.plot_bboxes(results, frame)

            end_time = time()
            fps = 1 / np.round(end_time - start_time, 2)
            cv2.putText(frame, f"FPS: {fps}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            cv2.imshow('YOLOv8 Detection', frame)
            if cv2.waitKey(5) & 0xFF == 27: 
                break

        cap.release()
        cv2.destroyAllWindows()

detector = ObjectDetection(capture_index=0)
detector()
