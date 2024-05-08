import FileHandler
import sys
import time
# def main(file_name):
#     # Your main logic goes here
#     try:
#         with open(file_name, 'r') as file:
#             # Process the file content
#             FileHandler.filehandler(file_name, 1)
#     except FileNotFoundError:
#         print(f"Error: File '{file_name}' not found.")
#     except Exception as e:
#         print(f"Error: {e}")

if __name__ == "__main__":
    # Entry point of Flash Detection, provide a file name and a speed multiplier

    t1 = time.time()
    FileHandler.filehandler("./sample_videos/natural_flash/Generator Explosion and Arc Flash.mp4", 1)
    t2 = time.time()
    print("runtime: " + str(int(t2-t1)) + " seconds")
#     if len(sys.argv) != 2:
#         print("Usage: python FlashDetection.py <file_path>")
#     else:
#         file_name = sys.argv[1]
#         main(file_name)