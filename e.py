import streamlit as st
import google.generativeai as genai
import firebase_admin
from firebase_admin import credentials, firestore
import json
import random
from datetime import datetime
import tempfile

# --- CONFIGURATION ---
# Gemini API Key
genai.configure(api_key="AIzaSyCYcfiDp7bM0dpvJadYxuh4_-yF1ONh2dc")

# --- STREAMLIT UI ---
st.title("Weekly Menu Generator with Gemini + Firebase")

# Upload Firebase Credentials
uploaded_file = st.file_uploader("Upload Firebase Admin SDK JSON", type="json")

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_file_path = tmp_file.name

    # Firebase Admin Init
    cred = credentials.Certificate(tmp_file_path)
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)
    db = firestore.client()

    # Initialize Gemini Model
    model = genai.GenerativeModel("gemini-1.5-flash")

    if st.button("Generate Weekly Chef Specials"):
        st.info("Fetching ingredients from Firebase and generating chef specials...")

        # Step 1: Pull ingredients from Firestore
        docs = db.collection("ingredient_inventory").stream()
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

# Instructions
st.markdown("""
---
**What This Does:**
- Prompts you to upload your Firebase Admin SDK credentials.
- Pulls current, valid ingredients from Firebase.
- Uses Gemini to create new chef-special recipes.
- Uploads each dish to the `menu` collection in Firestore.

**Coming Next:**
- Weekly planner integration
- Visual dashboard of menu items
- Ratings and AI-based dish scoring
""")
