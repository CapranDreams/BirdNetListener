# BirdNetListener
Remote microphone that pushes to the BirdNet server

## Setup

1. Install Raspberry Pi OS Lite (64-bit) on the Raspberry Pi Zero 2 W. Other versions may work, but this is the only version that has been tested.

2. Install python and dependencies:

- Install python 3.11 or higher

```bash
sudo apt update
sudo apt install software-properties-common
sudo apt upgrade
sudo apt install python3
sudo apt install python3-dev
sudo apt install python3-pip
```

- Install dependencies

```bash
pip install -r requirements.txt
```

3. Add the `start_script.sh` file to the Raspberry Pi Crontab:

```bash
crontab -e
```

Add the following line to the crontab (or the appropriate path to the start_script.sh file):

```bash
@reboot /home/pi/RPi_Listener/start_script.sh
```

4. Configure the `config_recorder.json` file. There are two options for uploading the wav files to the server:

- Option 1: Upload the wav files to the server via SSH
- Option 2: Upload the wav files to the server via a web API

If you want to use Option 1, you need to configure the SSH credentials in the `config_recorder.json` file.

If you want to use Option 2, you need to configure the web API credentials in the `config_recorder.json` file. It is recommended to use Option 2 if you can setup a server to receive the wav files.

The config expects all fields to be present, but only the fields for the selected option will be used.

```json
{
    "fs": 44100, 
    "seconds": 30,
    "buffer_size": 1024,

    "output_dir": "recordings",
    "server_dir": "C:/Users/<serverName>/BirdNET/birdnet/BirdNET_UI/data/wav/",

    "location_name": "<locationName>",
    "latitude": 0,
    "longitude": 0,

    "ssh_host": "<serverHost>",
    "ssh_username": "<serverUsername>",
    "ssh_password": "<serverPassword>",
    
    "server_url": "https://xxxxxx.com/api/submit_wav",
    "server_apikey": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
}
```

5. Run the script using the folloing command for testing. Otherwise, it will run automatically when the Raspberry Pi starts. 

```bash
python Recorder_linux.py
```
