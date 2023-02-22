# Download UST RVC
Download UST's remote video capture (RVC) recordings.

## Warning

The downloaded recording are for your personal use only. Do NOT share the recording with others.

## Usage

1. Make sure Python is installed. 

1. Open a Terminal / Command Prompt and install the tool with `pip`.

    ```bash
    pip install git+https://github.com/RapDoodle/Download-UST-RVC.git
    ```

1. Install [`ffmepg`](https://ffmpeg.org/) and make sure it is in your `PATH`.

    ```bash
    # For Windows users with Chocolatey (https://chocolatey.org/)
    choco install ffmpeg

    # For Ubuntu or Debian users
    sudo apt update && sudo apt install ffmpeg

    # For MacOS users with Homebrew (https://brew.sh/)
    brew install ffmpeg
    ```

1. Login to Canvas, open the page with the recording, and wait for the page to be loaded.

1. Open the browser's developer tool (for Google Chrome, it can be opened with F12) and navigate to the `Network` panel.

1. Play the video. After the video have started playing, pause the video and find the chunklist's URL. 

    <img src="guide.png?raw=true" height="350">

1. Run the script to download the video

    ```bash
    rvc-dl -u "Replace With Chunklist URL"
    ```

    Optionally, if you want to specify the name of the file, you can use the `-o` option

    ```bash
    rvc-dl -u "Replace With Chunklist URL" -o "Your Filename Goes Here.mp4"
    ```