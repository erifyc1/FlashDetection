import cv2
import numpy as np
from collections import deque
from red_transition_fsm import *
from DangerDetection import *

def filehandler(filename, speed):
    hertz = 3 #rate of flashing must not exceed 3 times per second
    if speed > 5 or speed < 2e-1:
      raise ValueError("speed must not exceed 5x and must greater than .1x")
    # get file and frame data
    cap = cv2.VideoCapture(filename)

    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_rate = int(cap.get(cv2.CAP_PROP_FPS))

    # frames of a second of video
    frames_per_second = int(frame_rate * speed)

    # sliding window array which accounts for a second of visual data
    dangerous = np.zeros((frames_per_second, frame_height, frame_width, 3), dtype=np.uint8)
    frame_buffer = deque(maxlen = frames_per_second)
    frame_buffer_red = Buffer(4,4,frame_rate)

    # if skipping a second to optimize
    frame_counter = 0
    start_danger = -1

    

    timestamps = []

    big_num = 134217728 #arbitrarily large integer, power of 2 for potential micro-optimization

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("total duration:", frame_counter / frames_per_second)
            print("done")
            break

        # Convert from BGR to HLS
        hls_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HLS)

         # Convert from BGR to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        tristimulus_matrix = np.array([
            [0.4124564, 0.3575761, 0.1804375],
            [0.2126729, 0.7151522, 0.0721750],
            [0.0193339, 0.1191920, 0.9503041]
        ])
        # Flatten the frame_rgb array
        flat_frame_rgb = frame_rgb.reshape(-1, 3)

        # Calculate b values for all pixels
        b = np.dot(flat_frame_rgb, tristimulus_matrix.T)

        # Calculate d values for all pixels
        d = b[:, 0] + 15 * b[:, 1] + 3 * b[:, 2]

        # Calculate u and v values for all pixels
        d[d == 0.0] = big_num
        u = 4 * b[:, 0] / d
        v = 9 * b[:, 1] / d

        # Calculate cTotal for all pixels
        cTotal = np.sum(frame_rgb, axis=2).reshape(-1)

        # Calculate rperc values for all pixels
        cTotal[cTotal == 0.0] = big_num
        rperc = flat_frame_rgb[:, 0] / cTotal

        # Reshape u, v, and rperc to the original shape
        u = u.reshape(frame_rgb.shape[0], frame_rgb.shape[1])
        v = v.reshape(frame_rgb.shape[0], frame_rgb.shape[1])
        rperc = rperc.reshape(frame_rgb.shape[0], frame_rgb.shape[1])

        # Combine u, v, and rperc into chromacityRerc
        chromacityRerc = np.stack((u, v, rperc), axis=2)

        #Add the currecnt frame to the buffer for red detection
        frame_buffer_red.add_frame(chromacityRerc)
        
        # Add the current frame to the buffer
        frame_buffer.append(hls_frame)

        # Check if we have enough frames for the sliding window
        if len(frame_buffer) == frames_per_second:
            # Fill the 'dangerous' array with the frames from the buffer
            for i, buf_frame in enumerate(frame_buffer):
                dangerous[i] = buf_frame

            # Process the potentially dangerous array
            flashes = process_dangerous(dangerous, frame_rate)
            #dangerous rate of flashing and not currently within a flashing state
            if flashes >= hertz and start_danger == -1:
                start_danger = frame_counter
            #we reach a region in which we don't have many flashes (end of flashing or region with no flashing)
            if flashes < hertz:
                if start_danger >= 0: #end of flashing, else do nothing if in a region with no flashing
                    timestamps.append([start_danger / frame_rate, frame_counter / frame_rate])
                    start_danger = -1 #reset start danger so we know we are looking for a new dangerous window
            frame_buffer.popleft() #remove first element in buffer, to be filled by next frame in filestream
        frame_counter += 1
    cap.release()

    if (start_danger >= 0): #if we are still in a state of danger
       timestamps.append([start_danger / frame_rate, frame_counter / frame_rate])

    #timestamp merge: Detection of flashes occurs within 1-to-2.5-second windows so we want to merge what's "close" together
    #closeness is a relatively arbitrary determination, 2 seconds chosen
    idx = 0
    merge_window = 2
    while idx < len(timestamps):
      stamp = timestamps[idx]
      if idx + 1 == len(timestamps):
        break
      next = timestamps[idx + 1]
      if abs(stamp[1] - next[0]) < merge_window:
        stamp[1] = next[1]
        timestamps.remove(next)
      else:
        idx += 1

    for st in timestamps:
      print("flashing from", st[0], "to", st[1])