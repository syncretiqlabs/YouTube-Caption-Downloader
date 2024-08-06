import os
import subprocess
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import re

def clean_subtitle(subtitle_content):
    lines = subtitle_content.split('\n')
    cleaned_lines = []
    for line in lines:
        if line == 'WEBVTT' or re.match(r'^\d{2}:\d{2}:\d{2}\.\d{3} --> \d{2}:\d{2}:\d{2}\.\d{3}', line) or 'align:start position:0%' in line:
            continue
        line = re.sub(r'<\d{2}:\d{2}:\d{2}\.\d{3}>', '', line)
        line = re.sub(r'</?c>', '', line)
        line = line.strip()
        if line and (not cleaned_lines or line != cleaned_lines[-1]):
            cleaned_lines.append(line)
    
    if cleaned_lines and cleaned_lines[0].startswith('Kind:'):
        cleaned_lines = cleaned_lines[2:]
    
    cleaned_text = re.sub(r'\n{3,}', '\n\n', '\n'.join(cleaned_lines)).strip()
    return cleaned_text

def download_captions(video_url, output_dir):
    try:
        # Get video info
        cmd = ['yt-dlp', '-J', '--no-playlist', video_url]
        result = subprocess.run(cmd, capture_output=True, text=True)
        video_info = json.loads(result.stdout)
        
        video_id = video_info['id']
        video_title = video_info['title']
        
        safe_title = "".join([c for c in video_title if c.isalpha() or c.isdigit() or c==' ']).rstrip()
        output_template = os.path.join(output_dir, f'{video_id}_{safe_title}.%(ext)s')
        
        # Download captions
        cmd = ['yt-dlp', 
               '--skip-download', 
               '--write-auto-sub',
               '--sub-format', 'vtt',
               '--output', output_template,
               video_url]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Check if captions were downloaded
        subtitle_file = next((f for f in os.listdir(output_dir) if f.startswith(f'{video_id}_{safe_title}') and f.endswith('.vtt')), None)
        
        if subtitle_file is None:
            print(f"No captions found for: {video_title}")
            return None
        
        subtitle_path = os.path.join(output_dir, subtitle_file)
        
        with open(subtitle_path, 'r', encoding='utf-8') as f:
            subtitle_content = f.read()
        
        cleaned_subtitle = clean_subtitle(subtitle_content)
        
        txt_path = os.path.join(output_dir, f'{video_id}_{safe_title}.txt')
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(cleaned_subtitle)
        
        os.remove(subtitle_path)
        
        print(f"Downloaded and cleaned captions for: {video_title}")
        return txt_path
    except subprocess.CalledProcessError as e:
        print(f"Error downloading captions for {video_url}: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error processing captions for {video_url}: {str(e)}")
        return None

def get_playlist_videos(playlist_url):
    cmd = [
        'yt-dlp',
        '--flat-playlist',
        '--print', 'id',
        '--no-warnings',
        playlist_url
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    video_ids = list(set(result.stdout.strip().split('\n')))  # Remove duplicates
    return [f'https://www.youtube.com/watch?v={video_id}' for video_id in video_ids if video_id]

def merge_captions(caption_files, output_dir):
    merged_content = []
    for file in caption_files:
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()
            merged_content.append(content)
            merged_content.append('\n\n' + '-'*50 + '\n\n')
    
    merged_file_path = os.path.join(output_dir, 'merged_captions.txt')
    with open(merged_file_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(merged_content))
    
    print(f"Merged captions saved to: {merged_file_path}")

def process_playlist(playlist_url, output_dir):
    video_urls = get_playlist_videos(playlist_url)
    total_videos = len(video_urls)
    print(f"Found {total_videos} unique videos in the playlist.")
    
    successful_downloads = 0
    failed_downloads = 0
    caption_files = []

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(download_captions, url, output_dir) for url in video_urls]
        for future in as_completed(futures):
            result = future.result()
            if result:
                caption_files.append(result)
                successful_downloads += 1
            else:
                failed_downloads += 1
            print(f"Processed {successful_downloads + failed_downloads}/{total_videos} videos. "
                  f"Successful: {successful_downloads}, Failed: {failed_downloads}")
    
    print(f"\nDownload summary for playlist {playlist_url}:")
    print(f"Total videos in playlist: {total_videos}")
    print(f"Successfully downloaded: {successful_downloads}")
    print(f"Failed to download: {failed_downloads}")
    
    return caption_files

def main():
    mode = input("Enter 'v' for single video or 'p' for playlist(s): ").lower()
    
    if mode == 'v':
        video_url = input("Enter the YouTube video URL: ")
        output_dir = input("Enter the output directory for captions: ")
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        result = download_captions(video_url, output_dir)
        if result:
            print("Caption downloaded successfully.")
        else:
            print("Failed to download caption.")
    
    elif mode == 'p':
        output_dir = input("Enter the output directory for captions: ")
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        multiple_playlists = input("Do you want to include multiple playlists? (yes/no): ").lower() == 'yes'
        
        if multiple_playlists:
            num_playlists = int(input("Enter the number of playlists: "))
            playlist_urls = []
            for i in range(num_playlists):
                playlist_url = input(f"Enter playlist URL {i+1}: ")
                playlist_urls.append(playlist_url)
        else:
            playlist_urls = [input("Enter the YouTube playlist URL: ")]
        
        all_caption_files = []
        
        for playlist_url in playlist_urls:
            caption_files = process_playlist(playlist_url, output_dir)
            all_caption_files.extend(caption_files)
        
        if all_caption_files:
            merge_option = input("Do you want to merge all the successfully downloaded captions into a single file? (yes/no): ").lower()
            if merge_option == 'yes':
                merge_captions(all_caption_files, output_dir)
        else:
            print("No captions were downloaded successfully from any playlist.")
    
    else:
        print("Invalid mode selected. Please run the script again and choose 'v' or 'p'.")

if __name__ == "__main__":
    main()