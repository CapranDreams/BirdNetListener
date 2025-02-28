# Remove all recordings from recordings directory
import os

# Get the current directory
current_dir = os.getcwd()

# Define the path to the recordings directory   
recordings_dir = os.path.join(current_dir, "recordings")

# Remove all files in the recordings directory
for file in os.listdir(recordings_dir):
    os.remove(os.path.join(recordings_dir, file))
    print(f"  File deleted: {file}")

print(f"All files in {recordings_dir} deleted")   

