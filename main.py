import os
import requests
import json
import time
from pytube import YouTube
import subprocess

# Set up FFmpeg (Koyeb/Heroku Compatibility)
FFMPEG_PATH = "/usr/bin/ffmpeg"
if not os.path.exists(FFMPEG_PATH):
    print("Downloading FFmpeg...")
    os.system("wget https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz")
    os.system("tar -xf ffmpeg-release-amd64-static.tar.xz")
    os.system("mv ffmpeg-*-static/ffmpeg /usr/bin/ffmpeg")

# Replace with your Telegram Bot Token
BOT_TOKEN = "YOUR_BOT_TOKEN"
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

FORMATS = ['Audio', '144p', '240p', '360p', '480p', '720p', '1080p', '1440p', '2160p']

def read_msg(offset):
    data = {"offset": offset}
    resp = requests.get(BASE_URL + '/getUpdates', data=data)
    dataframe = resp.json()

    for i in dataframe["result"]:
        try:
            user_id = i["message"]["from"]["id"]
            text = i["message"]["text"]

            print(f"User Input: {text}")
            yt = YouTube(text)

            if len(yt.streams) > 0:
                send_download(user_id, yt)
            else:
                send_message(user_id, 'Cannot download this video')

        except:
            try:
                process_download(i)
            except Exception as e:
                print("Error:", e)

    if dataframe["result"]:
        return dataframe["result"][-1]["update_id"] + 1

def send_download(user, yt):
    keyboard = [[{"text": "Audio"}]]
    resolutions = ["144p", "240p", "360p", "480p", "720p", "1080p", "1440p", "2160p"]

    for res in resolutions:
        if yt.streams.filter(res=res):
            keyboard.append([{"text": res}])

    send_message(user, "Select Download Option:", keyboard)

def process_download(i):
    user_id = i["message"]["from"]["id"]
    text = i["message"]["text"]

    yt = YouTube(get_last_url(user_id))
    title = yt.title.replace(" ", "_").replace("/", "_")
    username = str(user_id)

    os.makedirs(username, exist_ok=True)

    input_audio = f"{username}/{title}_audio"
    audio = yt.streams.filter(abr='128kbps')[0].download(filename=input_audio)

    if text == "Audio":
        output_audio = f"{username}/{title}.mp3"
        subprocess.call(["ffmpeg", "-i", input_audio, output_audio, "-y"])
        os.remove(input_audio)
        send_audio(user_id, output_audio)
    else:
        input_video = f"{username}/{title}_video"
        video = yt.streams.filter(res=text)[0].download(filename=input_video)

        output_video = f"{username}/{title}.mp4"
        subprocess.call(["ffmpeg", "-i", input_video, "-i", input_audio, "-c", "copy", output_video, "-y"])
        os.remove(input_video)
        os.remove(input_audio)
        send_video(user_id, output_video)

def send_message(user, message, keyboard=None):
    data = {"chat_id": user, "text": message}
    if keyboard:
        data["reply_markup"] = {"keyboard": keyboard, "resize_keyboard": True, "one_time_keyboard": True}
    requests.post(BASE_URL + "/sendMessage", json=data)

def send_audio(user, audio):
    with open(audio, 'rb') as f:
        requests.post(BASE_URL + "/sendAudio", data={"chat_id": user}, files={"audio": f})

def send_video(user, video):
    with open(video, 'rb') as f:
        requests.post(BASE_URL + "/sendVideo", data={"chat_id": user}, files={"video": f})

def get_last_url(user_id):
    return "YOUR_LAST_YOUTUBE_URL"  # Modify this to store/retrieve URLs properly

offset = 0
while True:
    try:
        offset = read_msg(offset)
    except Exception as e:
        print("Main Loop Error:", e)
    time.sleep(1)
