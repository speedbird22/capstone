import streamlit as st
import google.generativeai as genai
import firebase_admin
from firebase_admin import credentials, firestore
import json
import random
from datetime import datetime

# --- CONFIGURATION ---
# Gemini API Key
genai.configure(api_key="AIzaSyCYcfiDp7bM0dpvJadYxuh4_-yF1ONh2dc")

# --- STREAMLIT UI ---
st.title("Weekly Menu Generator with Gemini + Firebase")

# Firebase Admin Init from static file path
FIREBASE_KEY_PATH = "restaurant-data-backend-firebase-adminsdk-fbsvc-bdeb44e4a8.json"

try:
    cred = credentials.Certificate(FIREBASE_KEY_PATH)
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)
    db = firestore.client()

    # 🔍 Firestore connection test
    try:
        test_docs = db.collection("ingredient_inventory").limit(1).stream()
        for test_doc in test_docs:
            st.success("✅ Successfully connected to Firestore.")
            break
    except Exception as e:
        st.error(f"❌ Firestore access error: {e}")
        st.stop()

    # Initialize Gemini Model
    model = genai.GenerativeModel("gemini-1.5-flash")

    if st.button("Generate Weekly Chef Specials"):
        st.info("Fetching ingredients from Firebase and generating chef specials...")

        # Step 1: Pull ingredients from Firestore
        try:
            docs = db.collection("ingredient_inventory").stream()
        except Exception as e:
            st.error(f"Failed to fetch ingredients from Firestore: {str(e)}")
            docs = []
        available_ingredients = []
        today = datetime.today()

        for doc in docs:
            data = doc.to_dict()
            expiry_str = data.get("Expiry Date", "01/01/2100")
            try:
                expiry_date = datetime.strptime(expiry_str, "%d/%m/%Y")
                if expiry_date > today:
                    ingredient_name = data.get("Ingredient", "").strip()
                    if ingredient_name:
                        available_ingredients.append(ingredient_name)
            except:
                continue

        if len(available_ingredients) < 4:
            st.error("Not enough valid ingredients found in inventory.")
        else:
            # Step 2: Generate 3 Chef Special Dishes
            chef_specials = []
            for i in range(3):
                sample_ings = random.sample(available_ingredients, min(4, len(available_ingredients)))

                prompt = f"""
Using the following ingredients: {', '.join(sample_ings)},
create a creative dish suitable for a weekly restaurant menu.

Output the recipe in the following JSON format:
{{
  "name": "...",
  "ingredients": "...",
  "diet": "...",
  "types": "main/side/dessert",
  "flavor_profile": "...",
  "cook_time": int (in minutes),
  "prep_time": int (in minutes),
  "price_usd": float,
  "allergens": "...",
  "description": "...",
  "chef_special": true
}}
"""

                try:
                    response = model.generate_content(prompt)
                    output = response.text

                    # Try to extract JSON from response
                    start = output.find('{')
                    end = output.rfind('}') + 1
                    json_text = output[start:end]
                    dish = json.loads(json_text)
                    dish['chef_special'] = True

                    # Add to Firestore
                    db.collection("menu").add(dish)
                    chef_specials.append(dish)

                except Exception as e:
                    st.error(f"Failed to generate or upload dish: {str(e)}")

            if chef_specials:
                st.success("Chef specials generated and uploaded successfully!")
                for d in chef_specials:
                    st.markdown(f"**{d['name']}** - {d['description']}")
                    st.json(d)

except Exception as e:
    st.error(f"❌ App initialization failed: {e}")

# Instructions
st.markdown("""
---
**What This Does:**
- Auto-loads Firebase Admin SDK credentials.
- Pulls current, valid ingredients from Firebase.
- Uses Gemini to create new chef-special recipes.
- Uploads each dish to the `menu` collection in Firestore.

**Coming Next:**
- Weekly planner integration
- Visual dashboard of menu items
- Ratings and AI-based dish scoring
""")
