import streamlit as st
import json
from google import genai
from google.genai import types

st.set_page_config(page_title="Campus Bite Canteen Assistant", page_icon="🍔")
st.title("🍔 Campus Bite - Automated Ordering System")

 import os

 client = genai.Client(api_key=os.getenv("GEMINI_API_KEY")) 

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

if "chat" not in st.session_state:
    st.session_state.chat = client.chats.create(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.2
        )
    )

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Type your order or query here..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    response = st.session_state.chat.send_message(prompt)
    
    with st.chat_message("assistant"):
        st.markdown(response.text)
    st.session_state.messages.append({"role": "assistant", "content": response.text})
