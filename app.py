 import streamlit as st
import json
import os
from google import genai
from google.genai import types

st.set_page_config(page_title="Campus Bite Canteen Assistant", page_icon="🍔")
st.title("🍔 Campus Bite - Automated Ordering System")

api_key = os.environ.get("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")

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

# Display previous UI messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Type your order or query here..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        # Convert Streamlit message history to GenAI SDK history format
        history_contents = []
        for msg in st.session_state.messages[:-1]:
            role = "user" if msg["role"] == "user" else "model"
            history_contents.append(
                types.Content(
                    role=role,
                    parts=[types.Part.from_text(text=msg["content"])]
                )
            )

        # Fresh client and chat context on every execution (fixes closed client bug)
        client = genai.Client(api_key=api_key)
        chat = client.chats.create(
            model="gemini-2.0-flash",
            history=history_contents,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.2
            )
        )

        response = chat.send_message(prompt)
        
        with st.chat_message("assistant"):
            st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})

    except Exception as e:
        st.error(f"API Error: {str(e)}")
