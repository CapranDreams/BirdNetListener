import pyaudio
import numpy as np
from scipy.io.wavfile import write
import datetime
import os
import paramiko
import json

# import logging
# logging.basicConfig(level=logging.DEBUG)

# load the config file
with open('config_recorder.json', 'r') as f:
    config = json.load(f)

fs = config['fs']  # Sample rate
seconds = config['seconds']  # Duration of recording
buffer_size = config['buffer_size']  # Buffer size
output_dir = config['output_dir']
server_dir = config['server_dir']

# SSH connection details
ssh_host = config['ssh_host']
ssh_username = config['ssh_username']
ssh_password = config['ssh_password']

location_name = config['location_name']
latitude = config['latitude']
longitude = config['longitude']

pa = pyaudio.PyAudio()
stream = pa.open(format=pyaudio.paInt16,
                channels=1,
                rate=fs,
                input=True,
                frames_per_buffer=buffer_size)

def open_ssh_connection():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ssh_host, username=ssh_username, password=ssh_password)
    return ssh

def send_file_over_ssh(file_path):
    ssh = open_ssh_connection()
    is_ok = False
    try:
        sftp = ssh.open_sftp()
        # remote_file_path = f"/home/rpimic/recordings/{os.path.basename(file_path)}"
        remote_file_path = f"{server_dir}{os.path.basename(file_path)}"
        sftp.put(file_path, remote_file_path)  # Upload the file
        print(f"  File sent to {remote_file_path}")
        is_ok = True
    except Exception as e:
        print(f"    Failed to send file: {e}")
    finally:
        sftp.close()
        ssh.close()
    return is_ok

# infinitely repeat: 
#       a 30 second recording 
#       save to a file 
#       with the current date and time
#       send that file over ssh to the server
#       delete the file from this producer
try:
    while True:
        try:
            print("Recording...")
            frames = []  # List to hold the frames for the recording
            for _ in range(0, int(fs / buffer_size * seconds)):  # Loop for 30 seconds
                myrecording = stream.read(buffer_size)
                frames.append(myrecording)  # Append each frame to the list

            # Convert list of frames to a single bytes object
            myrecording_bytes = b''.join(frames)

            # Convert bytes to a NumPy array
            myrecording_np = np.frombuffer(myrecording_bytes, dtype=np.int16)  # Assuming 16-bit audio

            # Get the current date and time
            current_datetime = datetime.datetime.now()
            output_file = os.path.join(output_dir, current_datetime.strftime("birdnet~%Y~%m~%d~%H~%M~%S") + f"~{location_name}~{latitude}~{longitude}" + ".wav")

            write(output_file, fs, myrecording_np)  # Save as WAV file
            print(f"Recording saved to {output_file}")

            success = send_file_over_ssh(output_file)
            if success:
                print(f"  File sent to {ssh_username}@{ssh_host}")           
                os.remove(output_file)
                print(f"  File deleted: {output_file}")
            else:
                print(f"  File NOT sent to {ssh_username}@{ssh_host}")     
                os.remove(output_file)
                print(f"  File deleted anyways: {output_file}")
                # for now, just delete the file to prevent accumulation
                # TODO: send an email to the user maybe?
                # TODO: try again until reconnection established?

        except OSError as e:
            print(f"OSError: {e}")
            break  # Exit the loop if an OSError occurs

except KeyboardInterrupt:
    print("KeyboardInterrupt")
finally:
    stream.stop_stream()
    stream.close()
    pa.terminate()
    print("Terminated")
