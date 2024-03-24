import cv2
import time
import numpy as np
from collections import deque
from red_transition_fsm import *
from DangerDetection import *

def filehandler(filename, speed):
    hertz = 3
    if speed > 5 or speed < 2e-1:
      raise ValueError("speed must not exceed 5x and must be positive")
    flash_seconds = 0
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
    frame_buffer = deque(maxlen=frames_per_second)
    frame_buffer_red=Buffer(4,4,frame_rate)

    # if skipping a second to optimize
    skip = 0
    frame_counter = 0
    start_danger = -1
    # last_danger = -1
    profiling = np.array([0.0,0.0,0.0,0.0,0.0,0.0,0.0])
    timestamps = []

    while cap.isOpened():
        ret, frame = cap.read()
        if frame_counter % 60 == 0:
           print(f"progress: {int(100 * frame_counter / frame_count)}%")
        if not ret:
            print(frame_counter, frame_counter / frames_per_second)
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
        ff_t1 = time.time()
        # Flatten the frame_rgb array
        flat_frame_rgb = frame_rgb.reshape(-1, 3)

        # Calculate b values for all pixels
        b = np.dot(flat_frame_rgb, tristimulus_matrix.T)
        ff_t2 = time.time()
        profiling[0] += ff_t2 - ff_t1
        # Calculate d values for all pixels
        d = b[:, 0] + 15 * b[:, 1] + 3 * b[:, 2]
        ff_t3 = time.time()
        profiling[1] += ff_t3 - ff_t2
        # Calculate u and v values for all pixels
        d[d == 0.0] = 134217728
        u = 4 * b[:, 0] / d
        v = 9 * b[:, 1] / d
        ff_t4 = time.time()
        profiling[2] += ff_t4 - ff_t3
        # Calculate cTotal for all pixels
        cTotal = np.sum(frame_rgb, axis=2).reshape(-1)

        # Calculate rperc values for all pixels
        cTotal[cTotal == 0.0] = 134217728
        rperc = flat_frame_rgb[:, 0] / cTotal
        ff_t5 = time.time()
        profiling[3] += ff_t5 - ff_t4
        # Reshape u, v, and rperc to the original shape
        u = u.reshape(frame_rgb.shape[0], frame_rgb.shape[1])
        v = v.reshape(frame_rgb.shape[0], frame_rgb.shape[1])
        rperc = rperc.reshape(frame_rgb.shape[0], frame_rgb.shape[1])

        # Combine u, v, and rperc into chromacityRerc
        chromacityRerc = np.stack((u, v, rperc), axis=2)
        ff_t6 = time.time()
        profiling[4] += ff_t6 - ff_t5
        #Add the currecnt frame to the buffer for red detection
        frame_buffer_red.add_frame(chromacityRerc)
        
        # Add the current frame to the buffer
        frame_buffer.append(hls_frame)
        ff_t7 = time.time()
        profiling[5] += ff_t7 - ff_t6
        # Skip a second of frames
        # if skip > 0:
        #     skip -= 1
        #     frame_buffer.popleft()
        #     frame_counter += 1
        #     continue

        # Check if we have enough frames for the sliding window
        # print(frame_buffer, frames_per_second)
        if len(frame_buffer) == frames_per_second:
            # Fill the 'dangerous' array with the frames from the buffer
            for i, buf_frame in enumerate(frame_buffer):
                dangerous[i] = buf_frame

            # Process the 'dangerous' array
            flashes = process_dangerous(dangerous, frame_rate)
            if flashes >= hertz and start_danger == -1:
                start_danger = frame_counter
            if flashes < hertz:
                if start_danger >= 0:
                    timestamps.append([start_danger / frame_rate, frame_counter / frame_rate])
                    #print("danger from", start_danger / frames_per_second, "seconds to", frame_counter / frames_per_second, "seconds, frames", start_danger, frame_counter)
                    start_danger = -1
                    #last_danger = frame_counter
                #skip = frames_per_second
            frame_buffer.popleft()

            # print("number of flashes occured is" + str(flashes))
            # print(f"Processing window starting at frame {cap.get(cv2.CAP_PROP_POS_FRAMES) - frames_per_half_second}")
        frame_counter += 1
        ff_t8 = time.time()
        profiling[6] += ff_t8 - ff_t7
    cap.release()
    print(profiling)
    #timestamp merge: Detection of flashes occurs within half-second windows so we want to merge what's close together
    idx = 0
    while idx < len(timestamps):
      stamp = timestamps[idx]
      if idx + 1 == len(timestamps):
        break
      next = timestamps[idx + 1]
      if abs(stamp[1] - next[0]) < 1.5:
        stamp[1] = next[1]
        timestamps.remove(next)
      else:
        idx += 1

    for st in timestamps:
      print("flashing from", st[0], "to", st[1])