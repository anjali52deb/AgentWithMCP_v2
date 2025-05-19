# It has two version

# ======================
# do not delete this working version-2 (working)
# ======================

import os
import gc
import json
import tempfile
import traceback
import subprocess
import soundfile as sf
from moviepy.editor import VideoFileClip
from yt_dlp import YoutubeDL
import whisper

LANGUAGE_HINTS = {
    "hi": ["kumar sanu", "bollywood", "naaraaz", "hindi", "sambhala", "mere", "hai", "tum", "dil", "pyaar",
            "asha bhosle", "lata", "arijit", "yeh", "tera", "sapna", "sapne", "zindagi", "mohabbat", "ishq", "shayari",
            "hero", "villain", "gaana", "film", "kahani", "ranbir", "deepika"],
    "ta": ["kollywood", "tamil", "rajini", "vijay", "amma", "enna", "yen", "illa", "thalaiva", "padam",
            "sivakarthikeyan", "vijay sethupathi", "ajith", "kamal", "nayanthara", "thambi", "satham", "kadhal",
            "vettai", "vannakam", "ponniyin", "selvan", "mass", "basha", "veeram"],
    "te": ["tollywood", "telugu", "allu", "mahesh", "raasi", "nuvvu", "vaddu", "padam", "chiranjeevi", "pawan",
            "pushpa", "icon star", "srivalli", "kotha", "bava", "ammo", "veera", "kotha", "nenu", "evaru", "chitti",
            "adavi", "mass", "megastar"],
    "bn": ["bengali", "kolkata", "bangla", "rabindra", "ami", "tumi", "koro", "kotha", "chele", "meyera",
            "song", "gaaner", "sokal", "ratri", "shonar", "bangla", "bijoy", "pran", "anondo", "bhalobasha",
            "bhai", "rong", "misti", "rosogolla"],
    "ml": ["malayalam", "kerala", "mohanlal", "fahadh", "ente", "njan", "alle", "oru", "vannu", "chila",
            "manasil", "amma", "kutty", "mammootty", "nivin", "dileep", "kalyaanam", "pookal", "thaniye", "soorya",
            "thattathin", "marayathe", "kanne"]
}

def detect_language_hint(title: str, transcript: str, lang_hints: dict, threshold=2) -> str:
    text = (title + " " + transcript).lower()
    scores = {lang: sum(1 for word in hints if word in text) for lang, hints in lang_hints.items()}
    best_lang = max(scores, key=scores.get)
    return best_lang if scores[best_lang] >= threshold else ""

def is_transcript_repetitive(text, threshold=5):
    words = text.split()
    unique = set(words)
    return len(unique) < threshold

def handle_youtube_link(url, query):
    video_path = None
    raw_audio_path = None
    converted_audio_path = None

    try:
        print(f"\n>> [yt-dlp] Downloading YouTube video: {url}")
        ydl_opts = {
            "format": "best[height<=480][ext=mp4]",
            "outtmpl": os.path.join(tempfile.gettempdir(), "yt_video.%(ext)s"),
            "merge_output_format": "mp4",
            "quiet": True,
            "verbose": True,
            "noplaylist": True,
        }

        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            video_path = os.path.join(tempfile.gettempdir(), f"yt_video.{info['ext']}")
            title = info.get("title", "Unknown YouTube Video")
        print(f">> [yt-dlp] Video downloaded: {title}")

        print(">> [Whisper] Loading transcription model...")
        model = whisper.load_model("medium")

        raw_audio_path = video_path.replace(".mp4", "_raw.wav")
        converted_audio_path = video_path.replace(".mp4", ".wav")

        print(">> [Audio] Extracting and converting to 16kHz mono...")
        with VideoFileClip(video_path) as clip:
            clip.audio.write_audiofile(raw_audio_path, logger=None)

        subprocess.run([
            "ffmpeg", "-y", "-i", raw_audio_path,
            "-ac", "1", "-ar", "16000", "-sample_fmt", "s16",
            "-f", "wav", converted_audio_path
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        print(">> [Audio] Validating WAV file...")
        data, samplerate = sf.read(converted_audio_path)
        if len(data) < samplerate:
            raise Exception("Audio too short for transcription")

        print(">> [Whisper] First-pass transcription...")
        result = model.transcribe(converted_audio_path)
        transcript = result.get("text", "").strip()
        lang_code = result.get("language", "en")
        print(f">> [Whisper] Detected language: {lang_code}")
        print(f">> [Whisper] Transcript preview: {transcript[:100]}...")

        lang_hint = detect_language_hint(title, transcript, LANGUAGE_HINTS)
        if lang_hint and lang_hint != lang_code:
            print(f">> [Lang Hint] Overriding Whisper language from {lang_code} to {lang_hint}")
            result = model.transcribe(converted_audio_path, language=lang_hint)
            transcript = result.get("text", "").strip()
            lang_code = lang_hint

        if is_transcript_repetitive(transcript):
            print(">> [Whisper] Transcript appears repetitive or invalid. Using visual-only fallback.")
            transcript = ""

        print(">> [Gemini] Performing visual analysis...")
        visual_summary = analyze_video_frames(video_path, title, query="What do you see happening visually in this video?")

        if not transcript and not visual_summary:
            return f"🎥 {title}\n\n⚠️ Unable to extract meaningful content from this video."

        print(">> [Gemini] Classifying content type...")
        video_type = classify_video_content_type(transcript, visual_summary)
        print(f">> [Gemini] Detected video type: {video_type}")

        prompt_map = {
            "song": "Extract full lyrics from this song video.",
            "cooking": "Summarize the cooking recipe. Mention ingredients and steps.",
            "lecture": "Summarize the key points explained in this lecture.",
            "interview": "List who is speaking and summarize what they say.",
            "vlog": "Describe what the person is doing and where they are."
        }
        smart_prompt = prompt_map.get(video_type, f"Based on the transcript and visuals, respond to:\n{query}")
        if not transcript:
            smart_prompt = "The transcript was unreliable. Based on visuals only, describe what is happening in this video."

        print(f">> [Gemini] Final prompt:\n{smart_prompt}")
        final_output = summarize_frames_with_gemini(visual_summary, smart_prompt, transcript)

        return f"🎥 YouTube: {title}\n\n{final_output}"

    except Exception as e:
        print(">> [Error Traceback]")
        print(traceback.format_exc())
        return f"[ERROR during YouTube video processing: {e}]"

    finally:
        gc.collect()
        for path in [video_path, raw_audio_path, converted_audio_path]:
            if path and os.path.exists(path):
                try:
                    os.remove(path)
                    print(f">> [cleanup] Deleted temp file: {path}")
                except Exception as cleanup_error:
                    print(f">> [cleanup warning] Failed to delete {path}: {cleanup_error}")


# ======================
# do not delete this working version-1 (working)
# ======================
# import traceback
# import gc
# import soundfile as sf
# from moviepy.editor import VideoFileClip

# def handle_youtube_link(url, query):
#     video_path = None
#     raw_audio_path = None
#     converted_audio_path = None

#     try:
#         print(f"\n>> [yt-dlp] Starting download for: {url}")

#         ydl_opts = {
#             "format": "best[height<=480][ext=mp4]",
#             "outtmpl": tempfile.gettempdir() + "/yt_video.%(ext)s",
#             "merge_output_format": "mp4",
#             "quiet": True,
#             "verbose": True,
#             "noplaylist": True,
#         }

#         with YoutubeDL(ydl_opts) as ydl:
#             info = ydl.extract_info(url, download=True)
#             video_path = os.path.join(tempfile.gettempdir(), f"yt_video.{info['ext']}")
#             title = info.get("title", "Unknown YouTube Video")
#         print(f">> [yt-dlp] Video downloaded: {title}")

#         print(">> [Whisper] Loading model...")
#         model = whisper.load_model("medium")

#         raw_audio_path = video_path.replace(".mp4", "_raw.wav")
#         converted_audio_path = video_path.replace(".mp4", ".wav")

#         print(">> [Whisper] Extracting and converting audio...")
#         with VideoFileClip(video_path) as clip:
#             clip.audio.write_audiofile(raw_audio_path, logger=None)

#         ffmpeg_cmd = [
#             "ffmpeg", "-y", "-i", raw_audio_path,
#             "-ac", "1", "-ar", "16000", "-sample_fmt", "s16",
#             "-f", "wav", converted_audio_path
#         ]
#         subprocess.run(ffmpeg_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

#         print(">> [Whisper] Validating audio...")
#         data, samplerate = sf.read(converted_audio_path)
#         if len(data) < samplerate:
#             raise Exception("Audio too short to process")

#         print(">> [Whisper] Transcribing full audio...")
#         result = model.transcribe(converted_audio_path)
#         lang_code = result.get("language", "en")
#         transcript = result.get("text", "").strip()
#         print(f">> [Whisper] Language: {lang_code}")
#         print(f">> [Whisper] Transcript (preview): {transcript[:100]}...")

#         print(">> [Whisper] Transcribing...")
#         result = model.transcribe(converted_audio_path, language=lang_code)
#         transcript = result.get("text", "").strip()
#         print(f">> [Whisper] Transcript (preview): {transcript[:100]}")

#         print(">> [Gemini] Analyzing video frames...")
#         visual_analysis = analyze_video_frames(video_path, title, query="What do you see happening visually in this video?")

#         if not transcript and not visual_analysis:
#             return f"🎥 {title}\n\n[⚠️ Unable to extract meaningful content from this video.]"

#         video_type = classify_video_content_type(transcript, visual_analysis)
#         print(f">> [Gemini] Detected video type: {video_type}")

#         smart_prompt = {
#             "song": "Please extract the full lyrics from this song video.",
#             "cooking": "Summarize the cooking recipe shown in this video. Mention ingredients and steps clearly.",
#             "lecture": "Summarize the key points explained in this lecture.",
#             "interview": "List who is speaking and summarize what each person says.",
#             "vlog": "Describe what the person is doing and where they are."
#         }.get(video_type, query)

#         print(f">> [Gemini] Final prompt to model: {smart_prompt}")
#         combined_summary = summarize_frames_with_gemini(visual_analysis, smart_prompt, transcript)

#         return f"🎥 YouTube: {title}\n\n{combined_summary}"

#     except Exception as e:
#         print(">> [exception traceback]")
#         print(traceback.format_exc())
#         return f"[ERROR during YouTube video processing: {e}]"

#     finally:
#         # Moved outside `try` to make sure everything completes before cleanup
#         gc.collect()
#         for path in [video_path, raw_audio_path, converted_audio_path]:
#             if path and os.path.exists(path):
#                 try:
#                     os.remove(path)
#                     print(f">> [cleanup] Deleted temp file: {path}")
#                 except Exception as cleanup_error:
#                     print(f">> [cleanup warning] Failed to delete {path}: {cleanup_error}")

