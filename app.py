import streamlit as st
import json
import os
import requests

st.set_page_config(page_title="Campus Bite Canteen Assistant", page_icon="🍔")
st.title("🍔 Campus Bite - Automated Ordering System")

api_key = os.environ.get("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY", "").strip()

if not api_key:
    st.error("GEMINI_API_KEY missing! Please add it in Streamlit Secrets.")
    st.stop()

canteen_menu = [
    {"id": 101, "item": "Veg Samosa", "price": 15, "category": "Snacks", "available": True},
    {"id": 102, "item": "Paneer Patties", "price": 30, "category": "Snacks", "available": True},
    {"id": 103, "item": "Cold Coffee", "price": 50, "category": "Beverages", "available": True},
    {"id": 104, "item": "Masala Dosa", "price": 80, "category": "South Indian", "available": False},
    {"id": 105, "item": "Special Thali", "price": 120, "category": "Meals", "available": True}
]

system_prompt = f"""
You are the official automated ordering assistant for "Campus Bite" Canteen.
MENU: {json.dumps(canteen_menu)}
RULES:
1. Accept orders only for available menu items. Refuse out of stock items politely.
2. Out-of-topic guardrail: "I am programmed only to assist with Campus Bite Canteen menu details and order processing."
3. Provide itemized total bill and a pickup token (#CB-XXX) upon confirmation.
"""

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Type your order or query here..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        contents_payload = [{"role": "user", "parts": [{"text": system_prompt}]}]
        for msg in st.session_state.messages:
            role = "user" if msg["role"] == "user" else "model"
            contents_payload.append({"role": role, "parts": [{"text": msg["content"]}]})

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent?key={api_key}"
        headers = {"Content-Type": "application/json"}
        payload = {"contents": contents_payload}

        res = requests.post(url, headers=headers, json=payload)
        res_data = res.json()

        if res.status_code == 200:
            bot_reply = res_data["candidates"][0]["content"]["parts"][0]["text"]
            with st.chat_message("assistant"):
                st.markdown(bot_reply)
            st.session_state.messages.append({"role": "assistant", "content": bot_reply})
        else:
            error_msg = res_data.get("error", {}).get("message", "Unknown error")
            st.error(f"API Error ({res.status_code}): {error_msg}")

    except Exception as e:
        st.error(f"Request Error: {str(e)}")
