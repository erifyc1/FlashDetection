import FileHandler
import sys

FileHandler.filehandler("/Users/dahyun/Documents/Programfile/CS497/CS497_FlashDetection/sample_videos/natural_flash/Generator Explosion and Arc Flash.mp4",2)
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

# if __name__ == "__main__":
#     if len(sys.argv) != 2:
#         print("Usage: python FlashDetection.py <file_path>")
#     else:
#         file_name = sys.argv[1]
#         main(file_name)