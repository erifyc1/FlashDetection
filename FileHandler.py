# Open the video file
import cv2
import numpy as np
from collections import deque
import DangerDetection

def filehandler(filename, speed):
    # get file and frame data
    cap = cv2.VideoCapture(filename)

    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_rate = int(cap.get(cv2.CAP_PROP_FPS))

    # frames of a second of video
    frames_per_second = int(frame_rate * speed)

    # sliding window array which accounts for a second of visual data
    dangerous = np.zeros((frames_per_second, frame_height, frame_width, 3), dtype=np.uint8)
    frame_buffer = deque(maxlen=frames_per_second)

    while cap.isOpened():
        count = 0
        ret, frame = cap.read()
        if not ret:
            print("done")
            break
        # Convert from BGR to HLS
        hls_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HLS)

        # Add the current frame to the buffer
        frame_buffer.append(hls_frame)

        # Check if we have enough frames for the sliding window
        print(frame_buffer, frames_per_second)
        if len(frame_buffer) == frames_per_second:
            # Fill the 'dangerous' array with the frames from the buffer
            for i, buf_frame in enumerate(frame_buffer):
                dangerous[i] = buf_frame

            # Process the 'dangerous' array
            dangerous_segments = DangerDetection.process_dangerous(dangerous, frame_rate)
            if count % 14 == 0 and len(dangerous_segments) > 0:
                print(dangerous_segments)
            count += 1
            #print(f"Processing window starting at frame {cap.get(cv2.CAP_PROP_POS_FRAMES) - frames_per_half_second}")


    cap.release()