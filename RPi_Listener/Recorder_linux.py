import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
import datetime
import os
import paramiko
import json
import requests

# import logging
# logging.basicConfig(level=logging.DEBUG)

# load the config file
with open('config_recorder.json', 'r') as f:
    config = json.load(f)

fs = config['fs']  # Sample rate
seconds = config['seconds']  # Duration of recording
output_dir = config['output_dir']
server_dir = config['server_dir']

# SSH connection details
ssh_host = config['ssh_host']
ssh_username = config['ssh_username']
ssh_password = config['ssh_password']

location_name = config['location_name']
latitude = config['latitude']
longitude = config['longitude']

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
        remote_file_path = f"{server_dir}{os.path.basename(file_path)}"
        sftp.put(file_path, remote_file_path)  # Upload the file
        print(f"  File sent over SSH to {remote_file_path}")
        is_ok = True
    except Exception as e:
        print(f"    Failed to send file over SSH: {e}")
    finally:
        sftp.close()
        ssh.close()
    return is_ok

SERVER_URL = config['server_url']
SERVER_APIKEY = config['server_apikey']
def send_wav_to_server(file_path):
    try:
        # Open the file in binary mode
        with open(file_path, 'rb') as file:
            # Create a dictionary with the file
            files = {'file': (os.path.basename(file_path), file, 'audio/wav')}
            
            # Set the API key in the headers
            headers = {'X-API-Key': SERVER_APIKEY}
            
            # Make the POST request
            response = requests.post(
                f"{SERVER_URL}",
                files=files,
                headers=headers
            )
            
            # Check if the request was successful
            if response.status_code == 200:
                print(f"  File successfully uploaded to server API: {os.path.basename(file_path)}")
                return True
            else:
                print(f"  Failed to upload file to server API. Status code: {response.status_code}")
                print(f"  Response: {response.text}")
                return False
                
    except Exception as e:
        print(f"  Error uploading file to server API: {e}")
        return False

try:
    while True:
        try:
            print("Recording...")
            # Record audio using sounddevice
            myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=1, dtype='int16')
            sd.wait()  # Wait until recording is finished

            # Get the current date and time
            current_datetime = datetime.datetime.now()
            new_wav_filename = current_datetime.strftime("birdnet~%Y~%m~%d~%H~%M~%S") + f"~{location_name}~{latitude}~{longitude}" + ".wav"
            output_file = os.path.join(output_dir, new_wav_filename)

            write(output_file, fs, myrecording)  # Save as WAV file
            print(f"Recording saved to {output_file}")

            # THIS METHOD IS FOR SENDING THE FILE OVER SSH
            # ssh_success = send_file_over_ssh(output_file)

            # THIS METHOD IS FOR SENDING THE FILE OVER THE WEB API
            api_success = send_wav_to_server(output_file)
            
            # Delete the file after sending (or attempting to send)
            os.remove(output_file)
            print(f"  File deleted: {output_file}")

        except OSError as e:
            print(f"OSError: {e}")
            # break  # Exit the loop if an OSError occurs

except KeyboardInterrupt:
    print("KeyboardInterrupt")
finally:
    print("Terminated")
