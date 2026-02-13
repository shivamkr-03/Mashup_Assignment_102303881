import os
import shutil
import yt_dlp
import zipfile
import smtplib
from pydub import AudioSegment
from email.message import EmailMessage


# ------------------------------------
# DIRECTORY SETUP
# ------------------------------------

def prepare_workspace(base_dir="temp_files"):
    folders = ["videos", "audio", "clips", "result"]

    for folder in folders:
        os.makedirs(os.path.join(base_dir, folder), exist_ok=True)

    return base_dir


# ------------------------------------
# DOWNLOAD YOUTUBE VIDEOS
# ------------------------------------

def download_songs(artist_name, video_limit, base_dir):
    print("Downloading videos...")

    ydl_options = {
        "format": "best",
        "outtmpl": os.path.join(base_dir, "videos", "%(title)s.%(ext)s"),
        "noplaylist": True,
        "quiet": True
    }

    query = f"ytsearch{video_limit}:{artist_name} songs"

    try:
        with yt_dlp.YoutubeDL(ydl_options) as ydl:
            ydl.download([query])
    except Exception as e:
        raise Exception(f"Video download failed: {e}")


# ------------------------------------
# CONVERT VIDEO TO MP3
# ------------------------------------

def convert_to_mp3(base_dir):
    print("Converting videos to audio...")

    video_folder = os.path.join(base_dir, "videos")
    audio_folder = os.path.join(base_dir, "audio")

    for file in os.listdir(video_folder):
        video_path = os.path.join(video_folder, file)

        if not os.path.isfile(video_path):
            continue

        try:
            audio = AudioSegment.from_file(video_path)
            filename = os.path.splitext(file)[0] + ".mp3"
            audio.export(os.path.join(audio_folder, filename), format="mp3")
        except Exception:
            continue


# ------------------------------------
# TRIM AUDIO FILES
# ------------------------------------

def trim_audio_clips(duration_seconds, base_dir):
    print("Trimming audio files...")

    trim_length = duration_seconds * 1000
    audio_folder = os.path.join(base_dir, "audio")
    clips_folder = os.path.join(base_dir, "clips")

    for file in os.listdir(audio_folder):
        if not file.lower().endswith(".mp3"):
            continue

        audio_path = os.path.join(audio_folder, file)

        try:
            track = AudioSegment.from_mp3(audio_path)

            if len(track) < trim_length:
                continue

            trimmed_track = track[:trim_length]
            trimmed_track.export(
                os.path.join(clips_folder, file),
                format="mp3"
            )

        except Exception:
            continue


# ------------------------------------
# MERGE CLIPS
# ------------------------------------

def merge_clips(base_dir):
    print("Merging clips...")

    clips_folder = os.path.join(base_dir, "clips")
    final_audio = AudioSegment.empty()

    clip_files = sorted(os.listdir(clips_folder))

    if not clip_files:
        raise Exception("No audio clips available for merging.")

    for file in clip_files:
        if file.lower().endswith(".mp3"):
            clip = AudioSegment.from_mp3(os.path.join(clips_folder, file))
            final_audio += clip

    output_path = os.path.join(base_dir, "result", "final_mashup.mp3")
    final_audio.export(output_path, format="mp3")

    return output_path


# ------------------------------------
# ZIP FILE CREATION
# ------------------------------------

def create_zip(mp3_path, base_dir):
    zip_path = os.path.join(base_dir, "result", "mashup_output.zip")

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(mp3_path, arcname=os.path.basename(mp3_path))

    return zip_path


# ------------------------------------
# EMAIL FUNCTION
# ------------------------------------

def send_mashup_email(receiver_email, zip_path):
    sender_email = os.getenv("SENDER_EMAIL")
    app_password = os.getenv("APP_PASSWORD")

    if not sender_email or not app_password:
        raise Exception("Email credentials are not configured.")

    msg = EmailMessage()
    msg["Subject"] = "Your Generated Mashup"
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg.set_content(
        "Hello,\n\nYour mashup file is attached below.\n\nRegards,\nMashup Generator"
    )

    with open(zip_path, "rb") as file:
        msg.add_attachment(
            file.read(),
            maintype="application",
            subtype="zip",
            filename="mashup_output.zip"
        )

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, app_password)
            server.send_message(msg)
    except Exception as e:
        raise Exception(f"Email sending failed: {e}")


# ------------------------------------
# MAIN MASHUP FUNCTION (FOR WEB APP)
# ------------------------------------

def build_mashup(singer, number_of_videos, duration):
    base_dir = prepare_workspace()

    download_songs(singer, number_of_videos, base_dir)
    convert_to_mp3(base_dir)
    trim_audio_clips(duration, base_dir)

    final_mp3 = merge_clips(base_dir)
    zip_file = create_zip(final_mp3, base_dir)

    return zip_file


# ------------------------------------
# OPTIONAL CLEANUP
# ------------------------------------

def cleanup_workspace(base_dir="temp_files"):
    if os.path.exists(base_dir):
        shutil.rmtree(base_dir)