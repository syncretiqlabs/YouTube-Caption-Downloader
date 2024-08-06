# YouTube Caption Downloader

This Python script allows you to download and clean captions from YouTube videos and playlists. It supports downloading captions from a single video, a single playlist, or multiple playlists.

## Features

- Download captions from a single YouTube video
- Download captions from a YouTube playlist
- Support for downloading captions from multiple playlists
- Clean and format the downloaded captions
- Merge captions from multiple videos into a single file
- Multithreaded downloading for improved performance

## Requirements

- Python 3.6 or higher
- yt-dlp

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/syncretiqlabs/youtube-caption-downloader.git
   cd youtube-caption-downloader
   ```

2. Install the required package:
   ```
   pip install yt-dlp
   ```

## Usage

Run the script using Python:

```
python youtube_caption_downloader.py
```

Follow the prompts to:
1. Choose between downloading captions for a single video or playlist(s)
2. Enter the video URL or playlist URL(s)
3. Specify the output directory for the downloaded captions
4. Choose whether to merge the downloaded captions into a single file

## How it works

1. The script uses yt-dlp to fetch video information and download captions.
2. Captions are cleaned to remove timing information and formatting.
3. For playlists, the script downloads captions for each video in parallel.
4. If requested, all downloaded captions can be merged into a single file.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the [MIT License](LICENSE).