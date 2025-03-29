import os
import paramiko
from dotenv import load_dotenv

# ------------------------------------------------------------------------------------------------
# This script is used to push files to the RPi
# It will recursively upload all files and directories to the RPi
# It will skip any files that start with '_'
# You may need to run this script a second time after it creates the destination directory.
# ------------------------------------------------------------------------------------------------

# specify destination directory on RPi
destination_dir = "/home/rpimic/RPi_Listener"

# SSH credentials
load_dotenv()  # Load environment variables from .env file
ssh_host = os.getenv("ssh_host")
ssh_username = os.getenv("ssh_username")
ssh_password = os.getenv("ssh_password")


# get the parent directory
parent_dir = os.path.dirname(os.path.abspath(__file__))
print(f"local (PC) RPi directory:  {parent_dir}")


def open_ssh_connection():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ssh_host, username=ssh_username, password=ssh_password)
    return ssh

def upload_files_recursively(local_path, remote_path):
    ssh = open_ssh_connection()
    sftp = ssh.open_sftp()
    
    try:
        # Check if the local path is a directory
        if os.path.isdir(local_path):
            # Create the remote directory if it doesn't exist
            try:
                sftp.mkdir(remote_path)
                print(f"Directory created on RPi: {remote_path}")
            except IOError:
                print(f"Directory already exists on RPi: {remote_path}")

            # Iterate over the items in the local directory
            for item in os.listdir(local_path):
                local_item_path = os.path.join(local_path, item).replace('\\', '/')  # Replace backslashes with forward slashes
                remote_item_path = os.path.join(remote_path, item).replace('\\', '/')  # Replace backslashes with forward slashes

                # Skip files that start with '_'
                if not item.startswith('_'):
                    # Recursively upload files and directories
                    upload_files_recursively(local_item_path, remote_item_path)

        else:
            # If it's a file, upload it
            sftp.put(local_path, remote_path)
            print(f"Uploaded file:   {local_path}   to   {remote_path}") 

    except Exception as e:
        print(f"Failed to upload {local_path}: {e}")
    finally:
        sftp.close()
        ssh.close()

upload_files_recursively(parent_dir, destination_dir)

