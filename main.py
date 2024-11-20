import cv2
import argparse

from ultralytics import YOLO
import supervision as sv

def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="YOLOv8 live")
    parser.add_argument("--webcam-resolution", 
        default=[1280, 720], 
        nargs=2, 
        type=int
    )
    args = parser.parse_args()
    return args
    
    

def main ():
    args = parse_arguments()
    frame_width, frame_height = args.webcam_resolution
    
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, frame_width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_height)
    
    model = YOLO("yolov8l.pt")
    
    box_annotator = sv.BoxAnnotator(
        thickness=2,
        text_thickness=2,
        text_scale=1,
    )
    
    while True:
        ret, frame =cap.read()
        
        result = model(frame)[0]
        detections = sv.Detections.from_yolov8(result)
        
        frame = box_annotator(scene=frame, detections=detections)
        
        cv2.imshow("yolov8", frame)
        
        if (cv2.waitKey(30) == 27):
            break
    

if __name__ == "__main__":
    main ()