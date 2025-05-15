# aljazeera_app_beta.py

import streamlit as st
import json
import os
from datetime import datetime
from chatbot_engine_final import generate_response, get_predefined_articles, REGIONS, TOPICS

CHAT_LOG_PATH = "chat_history.json"
PREFS_PATH = "user_preferences.json"

# --- Streamlit Setup ---
st.set_page_config(page_title="📰 Al Jazeera News Assistant", layout="centered")

# --- Language Selection ---
st.sidebar.markdown("## 🌐 Language")
st.session_state.language = st.sidebar.selectbox("Choose a language", ["🇬🇧 English", "🇸🇦 العربية"])
LANG = st.session_state.language
IS_AR = LANG == "🇸🇦 العربية"

# --- Direction for Arabic ---
if IS_AR:
    st.markdown("""
    <style>
    html, body, [class*="css"] { direction: RTL; text-align: right; }
    .stButton>button { direction: RTL; }
    </style>
    """, unsafe_allow_html=True)

# --- Branding ---
st.markdown("""
<div style="display: flex; align-items: center; gap: 10px;">
    <img src="https://upload.wikimedia.org/wikinews/en/thumb/0/0f/Al_Jazeera.svg/1229px-Al_Jazeera.svg.png" width="40"/>
    <h1 style="margin-bottom: 0; font-family: 'Segoe UI'; color: #b38f00;">Al Jazeera News Assistant</h1>
</div>
""", unsafe_allow_html=True)

# --- CSS Styling ---
st.markdown("""
<style>
.stApp {
    background-color: #ffffff;
    padding: 0 10px;
    font-family: 'Segoe UI', sans-serif;
    color: #000000;
}
.message {
    border-radius: 18px;
    padding: 12px 16px;
    max-width: 85%;
    word-wrap: break-word;
    font-size: 15px;
    line-height: 1.5;
    position: relative;
    margin-bottom: 12px;
    color: #000000;
}
.user {
    align-self: flex-end;
    background-color: #b38f00;
    margin-left: auto;
    border-bottom-right-radius: 4px;
    box-shadow: 0 1px 1px rgba(0,0,0,0.1);
    color: #000000;
}
.bot {
    align-self: flex-start;
    background-color: #ffffff;
    margin-right: auto;
    border-bottom-left-radius: 4px;
    box-shadow: 0 1px 1px rgba(0,0,0,0.1);
    color: #000000;
}
.chat-container {
    display: flex;
    flex-direction: column;
    gap: 10px;
    background-color: #ffffff;
    padding: 15px;
    border-radius: 12px;
    max-width: 100%;
    overflow-x: hidden;
    margin-bottom: 20px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    color: #000000;
}
.stButton > button {
    border-radius: 20px !important;
    padding: 10px 20px;
    font-weight: 600;
    font-size: 15px;
    background-color: #b38f00 !important;
    color: white !important;
    border: none;
    margin-top: 8px;
}
.stButton > button:hover {
    background-color: #a07f00 !important;
    color: white !important;
}
</style>
""", unsafe_allow_html=True)

# --- Safe JSON Loader ---
def safe_load_json(path):
    if not os.path.exists(path):
        return []
    with open(path, 'r') as f:
        try:
            data = json.load(f)
            if isinstance(data, dict):
                return [data]
            return data if isinstance(data, list) else []
        except json.JSONDecodeError:
            return []

# --- Display Saved Data in Sidebar ---
st.sidebar.markdown("---")
st.sidebar.subheader("📁 Saved Chat History")
for entry in safe_load_json(CHAT_LOG_PATH)[-3:]:
    timestamp = entry.get("timestamp", "N/A")
    msg_count = len(entry.get("chat", []))
    st.sidebar.markdown(f"- `{timestamp}`: {msg_count} messages")

st.sidebar.markdown("---")
st.sidebar.subheader("📌 Saved Preferences")
for pref in safe_load_json(PREFS_PATH)[-3:]:
    ts = pref.get("timestamp", "N/A")
    region = pref.get("region", "-")
    topic = pref.get("topic", "-")
    st.sidebar.markdown(f"- `{ts}`: {region} / {topic}")

# --- Session State Initialization ---
for key, default in {
    "stage": "welcome",
    "chat": [],
    "region": "",
    "topic": "",
    "bot_flags": set()
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# --- Chat Display ---
st.markdown('<div class="chat-container">', unsafe_allow_html=True)
for msg in st.session_state.chat:
    st.markdown(f'<div class="message {msg["role"]}">{msg["content"]}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- Translations ---
TEXTS = {
    "🇬🇧 English": {
        "welcome": "👋 Welcome to Al Jazeera News Assistant! How would you like to explore the news today?",
        "choose_mode": "📌 Please select a mode to continue:",
        "predefined_topics": "🗂️ Predefined Topics",
        "custom_question": "🧠 Custom Question",
        "choose_region": "🌍 Please choose a region:",
        "choose_topic": "📰 Now select a topic in",
        "enter_question": "✍️ What would you like to know about the news?",
        "submit": "Submit",
        "back": "⬅️ Back",
        "what_next": "🔁 What would you like to do next?",
        "restart": "🔄 Restart Chat",
        "new_topic": "➕ New Topic"
    },
    "🇸🇦 العربية": {
        "welcome": "👋 مرحبا بك في مساعد أخبار الجزيرة! كيف ترغب في استكشاف الأخبار اليوم؟",
        "choose_mode": "📌 يرجى اختيار الوضع للمتابعة:",
        "predefined_topics": "🗂️ مواضيع محددة مسبقاً",
        "custom_question": "🧠 سؤال مخصص",
        "choose_region": "🌍 الرجاء اختيار المنطقة:",
        "choose_topic": "📰 اختر نوع الأخبار في",
        "enter_question": "✍️ ما الذي ترغب في معرفته عن الأخبار؟",
        "submit": "إرسال",
        "back": "⬅️ العودة",
        "what_next": "🔁 ماذا ترغب أن تفعل بعد ذلك؟",
        "restart": "🔄 إعادة المحادثة",
        "new_topic": "➕ موضوع جديد"
    }
}
T = TEXTS[LANG]

# --- Utilities ---
def add_user_message(msg):
    st.session_state.chat.append({"role": "user", "content": msg})

def add_bot_message_once(flag, msg):
    if flag not in st.session_state.bot_flags:
        st.session_state.chat.append({"role": "bot", "content": msg})
        st.session_state.bot_flags.add(flag)

# --- Chat Logic ---
if st.session_state.stage == "welcome":
    add_bot_message_once("welcome", T["welcome"])
    add_bot_message_once("choose_mode", T["choose_mode"])
    col1, col2 = st.columns(2)
    if col1.button(T["predefined_topics"]):
        st.session_state.stage = "region"
        st.rerun()
    if col2.button(T["custom_question"]):
        st.session_state.stage = "custom"
        st.rerun()

elif st.session_state.stage == "region":
    add_bot_message_once("region_msg", T["choose_region"])
    cols = st.columns(3)
    for i, region in enumerate(REGIONS):
        if cols[i % 3].button(region):
            add_user_message(region)
            st.session_state.region = region
            st.session_state.stage = "topic"
            st.rerun()
    if st.button(T["back"]):
        st.session_state.stage = "welcome"
        st.rerun()

elif st.session_state.stage == "topic":
    add_bot_message_once("topic_msg", f"{T['choose_topic']} {st.session_state.region}:")
    cols = st.columns(3)
    for i, topic in enumerate(TOPICS):
        if cols[i % 3].button(topic):
            add_user_message(topic)
            st.session_state.topic = topic
            st.session_state.stage = "predefined_output"
            st.rerun()
    if st.button(T["back"]):
        st.session_state.stage = "region"
        st.rerun()

elif st.session_state.stage == "predefined_output":
    lang_code = "ar" if IS_AR else "en"
    responses = get_predefined_articles(st.session_state.region, st.session_state.topic, lang_code)
    st.session_state.chat.extend(responses)
    st.session_state.stage = "menu"
    st.rerun()

elif st.session_state.stage == "custom":
    question = st.text_input(T["enter_question"])
    if st.button(T["submit"]) and question:
        add_user_message(question)
        answer = generate_response(question, language="ar" if IS_AR else "en")
        st.session_state.chat.append({"role": "bot", "content": answer})
        st.session_state.stage = "menu"
        st.rerun()
    if st.button(T["back"]):
        st.session_state.stage = "welcome"
        st.rerun()

elif st.session_state.stage == "menu":
    st.subheader(T["what_next"])
    col1, col2, col3 = st.columns(3)
    if col1.button(T["restart"]):
        st.session_state.chat = []
        st.session_state.stage = "welcome"
        st.session_state.bot_flags = set()
        st.rerun()
    if col2.button(T["new_topic"]):
        st.session_state.stage = "region"
        st.session_state.bot_flags = set()
        st.rerun()
    if col3.button(T["back"]):
        st.session_state.stage = "welcome"
        st.session_state.bot_flags = set()
        st.rerun()

st.markdown("---")
st.markdown("*Powered by JADA Pioneers*")
