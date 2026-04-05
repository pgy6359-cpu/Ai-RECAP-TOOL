import streamlit as st
import yt_dlp
import whisper
import google.generativeai as genai
from gtts import gTTS
import os
from moviepy.editor import VideoFileClip, AudioFileClip, vfx

# Website ပုံစံ ပြင်ဆင်ခြင်း
st.set_page_config(page_title="Myanmar AI Recap", layout="wide")
st.title("🇲🇲 YouTube to Myanmar Recap (Copyright Free)")

# ဘေးဘောင် (Sidebar) မှာ Settings ထည့်ခြင်း
st.sidebar.header("Settings")
api_key = st.sidebar.text_input("Gemini API Key ထည့်ပါ", type="password")
voice_speed = st.sidebar.slider("အသံနှုန်း (Speed)", 0.8, 1.5, 1.0)

# URL ထည့်တဲ့နေရာ
youtube_url = st.text_input("YouTube URL ကို ဒီမှာ Paste ချပါ (ဥပမာ- https://youtu.be/...)")

if st.button("Recap ဗီဒီယို စတင်ထုတ်လုပ်မယ်") and youtube_url and api_key:
    with st.status("အလုပ်လုပ်နေပါတယ်... ခဏစောင့်ပေးပါ") as status:
        try:
            # ၁။ AI ချိတ်ဆက်ခြင်း
            genai.configure(api_key=api_key)
            ai_model = genai.GenerativeModel('gemini-1.5-flash')

            # ၂။ Video Download ဆွဲခြင်း
            st.write("📥 Video ဒေါင်းလုဒ်ဆွဲနေသည်...")
            ydl_opts = {'format': 'bestvideo[height<=480]+bestaudio/best', 'outtmpl': 'input_v.mp4', 'merge_output_format': 'mp4'}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([youtube_url])

            # ၃။ အသံကို စာသားပြောင်းခြင်း (Whisper)
            st.write("🔈 အသံကို နားထောင်ပြီး စာသားထုတ်နေသည်...")
            model = whisper.load_model("base")
            result = model.transcribe("input_v.mp4")

            # ၄။ Gemini AI နဲ့ မြန်မာ Recap Script ရေးခြင်း
            st.write("✍️ မြန်မာ Recap Script အချောသတ်နေသည်...")
            prompt = f"Summarize this video into an engaging Myanmar movie recap script. Keep it under 200 words. Context: {result['text']}"
            myanmar_script = ai_model.generate_content(prompt).text
            st.info(f"Script: {myanmar_script}")

            # ၅။ မြန်မာအသံသွင်းခြင်း (TTS)
            st.write("🎙️ မြန်မာအသံသွင်းနေသည်...")
            tts = gTTS(myanmar_script, lang='my')
            tts.save("recap_v.mp3")

            # ၆။ Video Edit (Copyright လွတ်အောင် Mirror + Speed)
            st.write("🎬 Video အချောသတ်နေသည်...")
            clip = VideoFileClip("input_v.mp4").subclip(0, 60) # ၁ မိနစ်ပဲ ဖြတ်ယူမယ်
            new_audio = AudioFileClip("recap_v.mp3")
            
            # ဗီဒီယိုကို Mirror (ဘယ်ညာလှန်) ပြီး Speed ၁၀% တင်လိုက်မယ်
            final_clip = clip.fx(vfx.mirror_x).fx(vfx.speedx, 1.1).set_audio(new_audio)
            final_clip.write_videofile("output.mp4", codec="libx264", audio_codec="aac")

            status.update(label="ဗီဒီယို အောင်မြင်စွာ ထုတ်လုပ်ပြီးပါပြီ!", state="complete")
            
            # ရလဒ်ပြသခြင်း
            st.video("output.mp4")
            with open("output.mp4", "rb") as file:
                st.download_button("Recap ဗီဒီယိုကို သိမ်းဆည်းရန် (Download)", data=file, file_name="recap.mp4")

        except Exception as e:
            st.error(f"အမှားတစ်ခုရှိနေပါသည်: {e}")
