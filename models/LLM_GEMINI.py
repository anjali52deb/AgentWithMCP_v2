import os
import tempfile
import threading

from langchain.memory import ConversationBufferMemory
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

from moviepy.editor import VideoFileClip
from PIL import Image
from base64 import b64encode

from dotenv import load_dotenv
load_dotenv()

GEMINI_KEY = os.getenv("GEMINI_API_KEY")
# ==================================================================
# from LLM_LangChain import history_manager
# from attachment_handlers import *
# from models import attachment_handlers

from models.attachment_handlers import *

# ==================================================================
class InMemoryHistoryManager:
    def __init__(self):
        self.sessions = {}
        self.lock = threading.Lock()

    def get_memory(self, session_id):
        with self.lock:
            if session_id not in self.sessions:
                self.sessions[session_id] = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
            return self.sessions[session_id]

    def clear_memory(self, session_id):
        with self.lock:
            if session_id in self.sessions:
                del self.sessions[session_id]

history_manager = InMemoryHistoryManager()
# ==================================================================
def summarize_frames_with_gemini(frame_descriptions, user_query, transcript_text=None):
    try:
        visual_bullets = "\n".join([f"- {desc}" for desc in frame_descriptions.split("\n\n") if desc.strip()])
        
        prompt_parts = [f"These are visual observations from the video:\n{visual_bullets}"]
        if transcript_text:
            prompt_parts.append(f"The transcript of the audio is:\n{transcript_text[:1500]}")
        prompt_parts.append(f"Based on both the visuals and audio, summarize or respond to:\n{user_query}")
        
        final_prompt = "\n\n".join(prompt_parts)

        llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.7, google_api_key=GEMINI_KEY)
        response = llm.invoke([HumanMessage(content=final_prompt)])
        return f"🧠 Gemini Summary:\n{response.content.strip()}"

    except Exception as e:
        return f"[Gemini summarization failed: {e}]"
# ==================================================================
def classify_video_content_type(transcript, visuals):
    try:
        prompt = f"""
                You are analyzing a YouTube video.
                Based on the following transcript and visual description, classify what kind of video this is. Choose one:
                - song
                - cooking
                - lecture
                - interview
                - vlog
                - other
                Transcript (partial): {transcript[:1000]}
                Visuals (partial): {visuals[:1000]}
                """

        llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.3, google_api_key=GEMINI_KEY)
        response = llm.invoke([HumanMessage(content=prompt)])
        return response.content.strip().lower()
    
    except Exception as e:
        return "other"

# ==================================================================
def analyze_video_frames(video_path, filename, query, interval=2):
    try:
        clip = VideoFileClip(video_path)
        duration = int(clip.duration)
        frames = []

        max_frames = 5
        for t in range(0, min(duration, 20), interval):
            if len(frames) >= max_frames:
                break
            frame = clip.get_frame(t)
            img = Image.fromarray(frame)
            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp_img:
                img.save(tmp_img.name, format="JPEG")
                with open(tmp_img.name, "rb") as f:
                    encoded = b64encode(f.read()).decode("utf-8")
                    frames.append(encoded)

        frame_descriptions = []
        memory = history_manager.get_memory("frame_analysis_" + filename)

        for img_data in frames:
            try:
                result = handle_gemini(
                    query,
                    use_vision=True,
                    image_payloads=[{"mime_type": "image/jpeg", "data": img_data}],
                    attachment_texts=[],
                    memory=memory
                )
                frame_descriptions.append(result)
            except Exception as e:
                frame_descriptions.append(f"[Gemini failed to analyze frame: {e}]")

        return "\n\n".join(frame_descriptions[:5])
    except Exception as e:
        return f"[Error extracting frames from {filename}: {e}]"

# ==================================================================
def build_gemini_vision_prompt(image_payloads, attachment_texts, query):
    return [
        HumanMessage(content=[
            *[
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img['data']}"}}
                for img in image_payloads
            ],
            {"type": "text", "text": "\n\n".join(attachment_texts + [query])}
        ])
    ]    

# ==================================================================
def handle_gemini(query, use_vision, image_payloads, attachment_texts, memory, temperature=0.6):
    google_api_key = GEMINI_KEY
    if not google_api_key:
        return "Missing GOOGLE_API_KEY environment variable."

    # llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.7, google_api_key=google_api_key)
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=temperature, google_api_key=google_api_key)
    model_tag = "**<Gemini Vision>**" if use_vision else "**<Gemini>**"

    if use_vision:
        contents = build_gemini_vision_prompt(image_payloads, attachment_texts, query)
        memory.chat_memory.add_user_message("[User uploaded image(s) + query]")
        response = llm.invoke(contents)
    else:
        full_query = query + "\n".join(attachment_texts)
        memory.chat_memory.add_user_message(full_query)
        response = llm.invoke(memory.chat_memory.messages)

    result_text = response.content.strip()
    memory.chat_memory.add_ai_message(result_text)
    return f"{model_tag} \n{result_text}"
# ==================================================================
# END
# ==================================================================
