import os
import json
import requests
import yt_dlp
from flask import Flask, request

TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
BASE_URL = f"https://api.telegram.org/bot{TOKEN}/"

app = Flask(__name__)

# Function to send a message
def send_message(chat_id, text):
    url = BASE_URL + "sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, json=payload)

# Function to download a YouTube video
def download_youtube_video(url, resolution):
    ydl_opts = {
        "format": f"bestvideo[height<={resolution}]+bestaudio/best",
        "outtmpl": f"downloads/video.mp4",
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    return "downloads/video.mp4"

@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()
    
    if "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"]["text"]

        if text.startswith("https://youtu"):
            send_message(chat_id, "Downloading video... Please wait.")
            video_path = download_youtube_video(text, 1080)  # Default to 1080p
            files = {"video": open(video_path, "rb")}
            requests.post(BASE_URL + "sendVideo", data={"chat_id": chat_id}, files=files)
            os.remove(video_path)
        else:
            send_message(chat_id, "Send a valid YouTube link.")

    return "OK", 200

# Flask app for webhook
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
