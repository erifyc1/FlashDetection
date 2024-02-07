import numpy as np

def calculate_average_luminance(segment):
    # Luminance is in the Lightness channel (index 1) of HLS
    return np.mean(segment[:, :, 1])

# Function to process the dangerous array
def process_dangerous(dangerous, frame_rate):
    num_frames = dangerous.shape[0]
    height, width = dangerous.shape[1], dangerous.shape[2]
    segment_height = height // 4
    segment_width = width // 4
    luminance_threshold = 10
    num_flashes = np.zeros((4, 4))

    # Initialize luminance tracking and timestamps for each segment
    luminances = np.zeros((num_frames, 4, 4))

    # Precalculate all luminance values ahead of time
    for frame_idx in range(num_frames):
        for row in range(4):
            for col in range(4):
                y1, y2 = row * segment_height, (row + 1) * segment_height
                x1, x2 = col * segment_width, (col + 1) * segment_width
                segment = dangerous[frame_idx, y1:y2, x1:x2]
                average_luminance = calculate_average_luminance(segment)
                luminances[frame_idx, row, col] = average_luminance
    
    # Detect luminance changes
    for frame_idx in range(num_frames):
        for future_frame in range(frame_idx + 1, num_frames):
            for row in range(4):
                for col in range(4):
                    if abs(luminances[frame_idx, row, col] - luminances[future_frame, row, col]) > luminance_threshold:
                        # skip to next relevant frame
                        frame_idx = future_frame
                        num_flashes[row, col] += 1
    print(np.max(num_flashes))
    return num_flashes