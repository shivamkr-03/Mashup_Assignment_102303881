import sys
import os
import yt_dlp
from pydub import AudioSegment


# DISPLAY CORRECT USAGE


def show_help():
    print("\nCorrect Usage:")
    print('python 102303881.py "<SingerName>" <NumberOfVideos> <AudioDuration> <OutputFileName>')
    print('Example:')
    print('python 102303881.py "Sharry Maan" 15 25 mashup.mp3\n')



# ARGUMENT VALIDATION


def parse_arguments():
    if len(sys.argv) != 5:
        print("Invalid number of arguments.")
        show_help()
        sys.exit(1)

    singer_name = sys.argv[1]

    try:
        video_count = int(sys.argv[2])
        clip_duration = int(sys.argv[3])
    except ValueError:
        print("NumberOfVideos and AudioDuration must be integers.")
        sys.exit(1)

    output_filename = sys.argv[4]

    if video_count <= 10:
        print("NumberOfVideos must be greater than 10.")
        sys.exit(1)

    if clip_duration <= 20:
        print("AudioDuration must be greater than 20 seconds.")
        sys.exit(1)

    if not output_filename.lower().endswith(".mp3"):
        print("OutputFileName must have .mp3 extension.")
        sys.exit(1)

    return singer_name, video_count, clip_duration, output_filename


# ---------------------------
# CREATE REQUIRED FOLDERS
# ---------------------------

def setup_folders():
    folders = ["downloads", "audio_files", "clips", "final_output"]
    for folder in folders:
        os.makedirs(folder, exist_ok=True)


# DOWNLOAD VIDEOS


def fetch_videos(singer, count):
    print(f"\nDownloading top {count} videos of {singer}...")

    ydl_config = {
        "format": "best",
        "outtmpl": "downloads/%(title)s.%(ext)s",
        "quiet": False,
        "noplaylist": True
    }

    query = f"ytsearch{count}:{singer} songs"

    try:
        with yt_dlp.YoutubeDL(ydl_config) as ydl:
            ydl.download([query])
    except Exception as e:
        print(f"Error while downloading videos: {e}")
        sys.exit(1)

    print("Video download completed.")


# CONVERT VIDEO TO AUDIO


def extract_audio():
    print("\n Extracting audio from videos...")

    for file in os.listdir("downloads"):
        video_path = os.path.join("downloads", file)

        if not os.path.isfile(video_path):
            continue

        try:
            sound = AudioSegment.from_file(video_path)
            output_name = os.path.splitext(file)[0] + ".mp3"
            output_path = os.path.join("audio_files", output_name)
            sound.export(output_path, format="mp3")
            print(f"✔ Converted: {file}")
        except Exception as e:
            print(f"⚠ Skipped {file}: {e}")

    print("Audio extraction finished.")



# TRIM AUDIO FILES


def create_clips(seconds):
    print(f"\nCreating {seconds}-second clips...")

    duration_ms = seconds * 1000

    for file in os.listdir("audio_files"):
        audio_path = os.path.join("audio_files", file)

        if not file.lower().endswith(".mp3"):
            continue

        try:
            track = AudioSegment.from_mp3(audio_path)

            if len(track) < duration_ms:
                print(f"Skipped {file} (too short)")
                continue

            clipped = track[:duration_ms]
            clipped.export(os.path.join("clips", file), format="mp3")
            print(f"Trimmed: {file}")

        except Exception as e:
            print(f"Error trimming {file}: {e}")

    print("Audio clipping done.")


# MERGE ALL CLIPS


def combine_clips(output_name):
    print("\nMerging all clips...")

    merged_audio = AudioSegment.empty()

    clip_files = sorted(os.listdir("clips"))

    if not clip_files:
        print("No audio clips found.")
        sys.exit(1)

    for file in clip_files:
        if file.lower().endswith(".mp3"):
            clip = AudioSegment.from_mp3(os.path.join("clips", file))
            merged_audio += clip
            print(f"Added: {file}")

    final_path = os.path.join("final_output", output_name)

    try:
        merged_audio.export(final_path, format="mp3")
        print(f"\n Mashup created successfully at: {final_path}")
    except Exception as e:
        print(f"Failed to export final mashup: {e}")
        sys.exit(1)



# MAIN EXECUTION FLOW


def main():
    singer, count, duration, output_file = parse_arguments()
    setup_folders()
    fetch_videos(singer, count)
    extract_audio()
    create_clips(duration)
    combine_clips(output_file)


if __name__ == "__main__":
    main()