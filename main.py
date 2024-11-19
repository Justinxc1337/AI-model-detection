import cv2
import argparse

def main ():
    cap = cv2.VideoCapture(0)
    
    while True:
        ret, frame =cap.read()
        cv2.imshow("yolov8", frame)
        
        if (cv2.waitKey(30) == 27):
            break
    

if __name__ == "__main__":
    main ()