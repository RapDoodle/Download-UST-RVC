# Download UST RVC
Download UST's remote video capture (RVC) recordings.

## Warning

The downloaded recording are for your personal use only. Do NOT share the recording with others.

## Usage

1. Install [`ffmepg`](https://ffmpeg.org/) and make sure it is in your `PATH`.

```bash
# For Windows users with Chocolatey (https://chocolatey.org/)
choco install ffmpeg

# For Ubuntu or Debian users
sudo apt update && sudo apt install ffmpeg

# For MacOS users with Homebrew (https://brew.sh/)
brew install ffmpeg
```

2. Login to Canvas, open the page with the recording, and wait for the page to be loaded.

3. Open the browser's developer tool (for Google Chrome, it can be opened with F12) and navigate to the `Network` panel.

4. Play the video. After the video have started playing, stop the video and find the chunklist's URL. 

<img src="guide.png?raw=true" height="500">

5. Run the script to download the video

```bash
python rvc_dl.py -u "Replace With Chunklist URL"
```

Optionally, if you want to specify the name of the file, you can use the `-o` option

```bash
python rvc_dl.py -u "Replace With Chunklist URL" -o "Your Filename Goes Here"
```