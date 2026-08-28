import streamlit as st
import json
import os
import requests

st.set_page_config(page_title="Campus Bite Canteen Assistant", page_icon="🍔", layout="wide")
st.title("🍔 Campus Bite - Automated Ordering System")

api_key = os.environ.get("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY", "").strip()

if not api_key:
    st.error("GEMINI_API_KEY missing! Please add it in Streamlit Secrets.")
    st.stop()

# Updated menu with Image URLs
canteen_menu = [
    {
        "id": 101, 
        "item": "Veg Samosa", 
        "price": 15, 
        "category": "Snacks", 
        "available": True,
        "image": "https://images.unsplash.com/photo-1601050690597-df0568f70950?w=500"
    },
    {
        "id": 102, 
        "item": "Paneer Patties", 
        "price": 30, 
        "category": "Snacks", 
        "available": True,
        "image": "https://images.unsplash.com/photo-1626132647523-66f5bf380027?w=500"
    },
    {
        "id": 103, 
        "item": "Cold Coffee", 
        "price": 50, 
        "category": "Beverages", 
        "available": True,
        "image": "https://images.unsplash.com/photo-1517701604599-bb29b565090c?w=500"
    },
    {
        "id": 104, 
        "item": "Masala Dosa", 
        "price": 80, 
        "category": "South Indian", 
        "available": False,
        "image": "https://images.unsplash.com/photo-1668236543090-82eba5ee5976?w=500"
    },
    {
        "id": 105, 
        "item": "Special Thali", 
        "price": 120, 
        "category": "Meals", 
        "available": True,
        "image": "https://images.unsplash.com/photo-1546833999-b9f581a1996d?w=500"
    }
]

# --- SIDEBAR MENU WITH PHOTOS ---
st.sidebar.title("📜 Campus Bite Menu")
for item in canteen_menu:
    status = "✅ Available" if item["available"] else "❌ Out of Stock"
    st.sidebar.subheader(f"{item['item']} - ₹{item['price']}")
    st.sidebar.caption(f"Category: {item['category']} | Status: {status}")
    st.sidebar.image(item["image"], use_container_width=True)
    st.sidebar.divider()

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
