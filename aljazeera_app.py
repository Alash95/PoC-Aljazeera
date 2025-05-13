import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

from chatbot_engine import generate_response, search_similar_articles, REGIONS, TOPICS

CHAT_LOG_PATH = "chat_history.json"
PREFS_PATH = "user_preferences.json"

# --- Streamlit Page Setup ---
st.set_page_config(
    page_title="📰 Al Jazeera News Assistant",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- Branding with Al Jazeera Logo and Title ---
st.markdown("""
<div style="display: flex; align-items: center; gap: 10px;">
    <img src="https://upload.wikimedia.org/wikinews/en/thumb/0/0f/Al_Jazeera.svg/1229px-Al_Jazeera.svg.png" alt="Al Jazeera Logo" width="40"/>
    <h1 style="margin-bottom: 0; font-family: 'Segoe UI', sans-serif; color: #0a0a0a;">Al Jazeera News Assistant</h1>
</div>
""", unsafe_allow_html=True)

# --- UI Styles Themed with Al Jazeera Palette ---
st.markdown("""
<style>
.stApp {
    background-color: #f5f5f5;
    padding: 0 10px;
    color: #b38f00;
    font-family: 'Segoe UI', sans-serif;
}
# .chat-container {
#     display: flex;
#     flex-direction: column;
#     gap: 10px;
#     background-color: #ffffff;
#     padding: 15px;
#     border-radius: 12px;
#     max-width: 100%;
#     overflow-x: hidden;
#     margin-bottom: 20px;
#     box-shadow: 0 2px 4px rgba(0,0,0,0.1);
#     color: #0a0a0a;
}
.message {
    border-radius: 18px;
    padding: 12px 16px;
    max-width: 85%;
    word-wrap: break-word;
    font-size: 15px;
    line-height: 1.5;
    position: relative;
    font-family: 'Segoe UI', sans-serif;
    color: #0a0a0a;
    margin-bottom: 12px
}
.user {
    align-self: flex-end;
    background-color: #fef4d9;
    margin-left: auto;
    border-bottom-right-radius: 4px;
    box-shadow: 0 1px 1px rgba(0,0,0,0.1);
    color: #0a0a0a;
}
.bot {
    align-self: flex-start;
    background-color: #f9f9f9;
    margin-right: auto;
    border-bottom-left-radius: 4px;
    box-shadow: 0 1px 1px rgba(0,0,0,0.1);
    color: #0a0a0a;
}
.read-more {
    font-size: 0.8rem;
    color: #b38f00;
    text-decoration: none;
}
.read-more:hover {
    text-decoration: underline;
}
.stButton > button {
    border-radius: 20px !important;
    padding: 8px 16px;
    font-weight: 500;
    background-color: #b38f00 !important;
    color: white !important;
    border: none;
}
.stButton > button:hover {
    background-color: #a07f00 !important;
    color: #fff !important;
}
</style>
""", unsafe_allow_html=True)

# --- Session State Initialization ---
if "saved_chat" not in st.session_state:
    st.session_state.saved_chat = False
if "saved_prefs" not in st.session_state:
    st.session_state.saved_prefs = False

# Initialize session state
for key, value in {
    "saved_chat": False,
    "saved_prefs": False,
    "stage": "welcome",
    "chat": [],
    "region": "",
    "topic": "",
    "bot_flags": set()
}.items():
    if key not in st.session_state:
        st.session_state[key] = value

# Utilities


def add_user_message(text):
    st.session_state.chat.append({"role": "user", "content": text})


def add_bot_message_once(key, text):
    if key not in st.session_state.bot_flags:
        st.session_state.chat.append({"role": "bot", "content": text})
        st.session_state.bot_flags.add(key)


def save_chat_history():
    try:
        history = st.session_state.chat.copy()
        all_chats = []
        if os.path.exists(CHAT_LOG_PATH):
            with open(CHAT_LOG_PATH, 'r') as file:
                all_chats = json.load(file)
        all_chats.append(
            {"timestamp": datetime.now().isoformat(), "chat": history})
        with open(CHAT_LOG_PATH, 'w') as file:
            json.dump(all_chats, file, indent=2)
        st.session_state.saved_chat = True
        st.success("✅ Chat history saved successfully.")
    except Exception as e:
        st.error(f"❌ Error saving chat history: {e}")


def save_user_preferences(region, topic):
    try:
        prefs = []
        if os.path.exists(PREFS_PATH):
            with open(PREFS_PATH, 'r') as file:
                current_data = json.load(file)
                prefs = current_data if isinstance(
                    current_data, list) else [current_data]
        prefs.append({"region": region, "topic": topic,
                     "timestamp": datetime.now().isoformat()})
        with open(PREFS_PATH, 'w') as file:
            json.dump(prefs, file, indent=2)
        st.session_state.saved_prefs = True
        st.success("✅ User preferences saved successfully.")
    except Exception as e:
        st.error(f"❌ Error saving user preferences: {e}")


# -- Sidebar functionality --
with st.sidebar:
    st.header("💾 Save Options")

    if st.button("📌 Save Preferences", key="save_prefs_btn"):
        if st.session_state.get("region") and st.session_state.get("topic"):
            save_user_preferences(st.session_state.region,
                                  st.session_state.topic)
        else:
            st.warning("⚠️ Please select both a region and topic first.")

    if st.session_state.saved_prefs:
        st.success("🔖 Preferences saved")

    if st.button("📝 Save Chat History", key="save_chat_btn"):
        if st.session_state.get("chat"):
            save_chat_history()
        else:
            st.warning("⚠️ No chat history available to save.")

    if st.session_state.saved_chat:
        st.success("🗂️ Chat log saved")

    st.markdown("---")
    st.subheader("🗃️ Saved Data")

    if os.path.exists(PREFS_PATH):
        with open(PREFS_PATH, 'r') as f:
            prefs_data = json.load(f)
            if isinstance(prefs_data, dict):
                prefs_data = [prefs_data]
            elif not isinstance(prefs_data, list):
                prefs_data = []
            st.write("**Preferences:**")
            for p in prefs_data[-3:]:
                ts = p.get("timestamp", "N/A")
                region = p.get("region", "-")
                topic = p.get("topic", "-")
                st.markdown(f"- `{ts}`: {region} / {topic}")

            prefs_json = json.dumps(prefs_data, indent=2)
            st.download_button("⬇️ Download Preferences JSON",
                               prefs_json, file_name="user_preferences.json")

    if os.path.exists(CHAT_LOG_PATH):
        with open(CHAT_LOG_PATH, 'r') as f:
            chat_data = json.load(f)
            if isinstance(chat_data, dict):
                chat_data = [chat_data]
            elif not isinstance(chat_data, list):
                chat_data = []
            st.write("**Chat Logs:**")
            for c in chat_data[-3:]:
                timestamp = c.get("timestamp", "N/A")
                messages = len(c.get("chat", []))
                st.markdown(f"- `{timestamp}` with {messages} messages")

            chat_json = json.dumps(chat_data, indent=2)
            st.download_button("⬇️ Download Chat History JSON",
                               chat_json, file_name="chat_history.json")


# Chat logic and rendering
if st.session_state.stage == "welcome":
    add_bot_message_once(
        "welcome_msg", "👋 Welcome to Al Jazeera News Assistant! How would you like to explore the news today?")
    add_bot_message_once("choose_mode", "📌 Please select a mode to continue:")

elif st.session_state.stage == "region":
    add_bot_message_once("region_msg", "🌍 Please choose a region:")

    cols = st.columns(3)
    for i, region in enumerate(REGIONS):
        if cols[i % 3].button(region, key=f"region_btn_{i}"):
            add_user_message(f"Region selected: {region}")
            st.session_state.region = region
            st.session_state.stage = "topic"
            st.rerun()

    # Back button
    if st.button("⬅️ Back", key="back_from_region"):
        st.session_state.stage = "welcome"
        st.rerun()


elif st.session_state.stage == "topic":
    add_bot_message_once(
        "topic_msg", f"📰 Now select a topic in {st.session_state.region}:")

    cols = st.columns(3)
    for i, topic in enumerate(TOPICS):
        if cols[i % 3].button(topic, key=f"topic_btn_{i}"):
            add_user_message(f"Topic selected: {topic}")
            st.session_state.topic = topic
            st.session_state.stage = "predefined_output"
            st.rerun()

    # Back button
    if st.button("⬅️ Back", key="back_from_topic"):
        st.session_state.stage = "welcome"
        st.rerun()

elif st.session_state.stage == "predefined_output":
    query = f"{st.session_state.topic} in {st.session_state.region}"
    add_bot_message_once("pre_output_msg", f"🔍 Fetching news for {query}...")
    results = search_similar_articles(query, k=3)
    if results.empty:
        add_bot_message_once(
            "no_articles", "❌ No articles found for this topic.")
    else:
        for _, row in results.iterrows():
            summary = f"**{row['Headline']}**\n\n{row['Summary']}\n\n[Read More]({row['URL']})"
            st.session_state.chat.append({"role": "bot", "content": summary})
    st.session_state.stage = "menu"
    st.rerun()

elif st.session_state.stage == "custom":
    add_bot_message_once(
        "custom_prompt", "✍️ What would you like to know about the news?")
    col1, col2 = st.columns([4, 1])
    with col1:
        question = st.text_input("Your question:", key="custom_input_final")
    with col2:
        if st.button("⬅️ Back", key="back_from_custom"):
            st.session_state.stage = "welcome"
            st.rerun()

    if st.button("Submit Question", key="submit_custom_query_final"):
        if question:
            add_user_message(question)
            answer = generate_response(question)
            st.session_state.chat.append({"role": "bot", "content": answer})
            st.session_state.stage = "menu"
            st.rerun()


elif st.session_state.stage == "menu":
    st.markdown("---")
    st.subheader("🔁 What would you like to do next?")
    col1, col2, col3 = st.columns(3)
    if col1.button("🔄 Restart Chat", key="restart_chat_button"):
        st.session_state.chat = []
        st.session_state.stage = "welcome"
        st.session_state.bot_flags = set()
        st.rerun()
    if col2.button("➕ Predefined Topic", key="new_search_button"):
        st.session_state.stage = "region"
        st.session_state.bot_flags = set()
        st.rerun()
    if col3.button("⬅️ Back", key="back_to_mode_button"):
        st.session_state.stage = "welcome"
        st.session_state.bot_flags = set()
        st.rerun()

# Display chat
st.markdown('<div class="chat-container">', unsafe_allow_html=True)
for msg in st.session_state.chat:
    role = "user" if msg["role"] == "user" else "bot"
    st.markdown(
        f'<div class="message {role}">{msg["content"]}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# UI triggers for stage-based buttons
if st.session_state.stage == "welcome":
    col1, col2 = st.columns(2)
    if col1.button("🗂️ Predefined Topics", key="predefined_button"):
        add_user_message("I want to browse by predefined topics")
        st.session_state.stage = "region"
        st.rerun()
    if col2.button("🧠 Custom Question", key="custom_button"):
        add_user_message("I want to ask a custom question")
        st.session_state.stage = "custom"
        st.rerun()

elif st.session_state.stage == "region":
    cols = st.columns(3)
    for i, region in enumerate(REGIONS):
        if cols[i % 3].button(region, key=f"region_btn_stage_region_{i}"):
            add_user_message(f"Region selected: {region}")
            st.session_state.region = region
            st.session_state.stage = "topic"
            st.rerun()


elif st.session_state.stage == "topic":
    cols = st.columns(3)
    for i, topic in enumerate(TOPICS):
        if cols[i % 3].button(topic, key=f"topic_btn_stage_topic_{i}"):
            add_user_message(f"Topic selected: {topic}")
            st.session_state.topic = topic
            st.session_state.stage = "predefined_output"
            st.rerun()

elif st.session_state.stage == "predefined_output":
    query = f"{st.session_state.topic} in {st.session_state.region}"
    add_bot_message_once("pre_output_msg", f"🔍 Fetching news for {query}...")
    results = search_similar_articles(query, k=3)
    if results.empty:
        add_bot_message_once(
            "no_articles", "❌ No articles found for this topic.")
    else:
        for _, row in results.iterrows():
            summary = f"**{row['Headline']}**\n\n{row['Summary']}\n\n[Read More]({row['URL']})"
            st.session_state.chat.append({"role": "bot", "content": summary})
    st.session_state.stage = "menu"
    st.rerun()

elif st.session_state.stage == "custom":
    add_bot_message_once(
        "custom_prompt", "✍️ What would you like to know about the news?")
    with st.form("custom_query"):
        question = st.text_input("Your question:", key="custom")
        submit = st.form_submit_button("Submit")
        if submit and question:
            add_user_message(question)
            answer = generate_response(question)
            st.session_state.chat.append({"role": "bot", "content": answer})
            st.session_state.stage = "menu"
            st.rerun()

elif st.session_state.stage == "menu":
    st.markdown("---")
    st.subheader("🔁 What would you like to do next?")
    col1, col2, col3 = st.columns(3)
    if col1.button("🔄 Restart Chat"):
        st.session_state.chat = []
        st.session_state.stage = "welcome"
        st.session_state.bot_flags = set()
        st.rerun()
    if col2.button("➕ Predefined Topic"):
        st.session_state.stage = "region"
        st.session_state.bot_flags = set()
        st.rerun()
    if col3.button("⬅️ Back"):
        st.session_state.stage = "welcome"
        st.session_state.bot_flags = set()
        st.rerun()

st.markdown("---")
st.markdown("*Powered by JADA Pioneers!*")
