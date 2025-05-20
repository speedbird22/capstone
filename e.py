import streamlit as st
import google.generativeai as genai
import firebase_admin
from firebase_admin import credentials, firestore
import json
import random
from datetime import datetime
from dateutil.parser import parse
import re
from google.api_core import exceptions

# --- CONFIGURATION ---
# Gemini API Key (unchanged as per request)
genai.configure(api_key="AIzaSyCYcfiDp7bM0dpvJadYxuh4_-yF1ONh2dc")

# Firebase Service Account Key (unchanged as per request)
FIREBASE_CREDENTIALS = {
    "type": "service_account",
    "project_id": "restaurant-data-backend",
    "private_key_id": "c3ad6ad3e0e2a802c3284ea8b722170323f9b6a8",
    "private_key": """-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQDy2znPpLQIHOQ5\n3VyGtk+szjT3/S8QZc5GhndxvVHA7jFm50cJCqJjvaY2HFRHsQ+RVWnRBzMZedDI\nwSTtvMH1YjgTNVZbV2llczW/tJZxAc1rSeIFaLxwUhMtpZiBfhblxakDpo6gE+Pu\nDK9qi++u2f4YE8SBYE8A3ZyKMBVDF0ENJkzGb7TRStEoECxfm0tdhqlwq4Q3/Zbr\n7JodiKc6td2ckAnpLiFu4lcF9GDt4o5SPw7tyUEvhrV6euGXGRBrOPLFuJHAsGRR\ntpYc2TSJvq0VPeQGqoDEcMrGhWmGwsadfAnkaH16L38bxAkDDs8GPZ6DpAxogrvv\nCHPU1jNnAgMBAAECggEAXevVuE2wyIBv7UcETR79wk1/Y7b5eCR/OXwwfn7iurQD\nzBG+warosZ07Rir/lzhNVn4LbekUZJJdYf58ayr4cg95s0gJ7UppevArBchv9CVn\nzcnljQT7945uV1V3HQFoFpWybzR/bT40BLDIOHMFD4DECYi/ku9trl6Gd1TwLCD1\nwEZi2Ny8XLzy38AXi2dfww1cLYSvPQQ/qXXZEpwGN5dq+Fu/WxZ6uLCYyxocHQse\nvyKAp358FI3YXk+iNwVzonsAUQfGp+xUD4uZGPTCHjgT2svaHX1qOJg4HCsKUjUn\nTG7lNU7njwcBarV3BOrWnYZPq08H7Fc7Lu9JSWto1QKBgQD/Kz7nr6J46iQrgwNH\nQixPHmNIXTg542YSGh5dQqZDmS83arHf89jDbNo2K4Mlg82iMG6jEI07ojWDGLKu\ncx2wdjK+jaOkDSDbKnsMh/AOHtL6nUVhRbe/W3mDUd8vVDx3kvqjlAgKJc/EKzy1\nxH+15JrgRrRaXnMDHHg0vgi2MwKBgQDzpbbSHY7bTDzgfiYjUs4QW3f3w+fsGgZW\nuBriZWpiBM5+KLWouagm8Z7Tn5+gS7ZlDoPJXmmLInc14p4pXelCF0Sv6yLIzsGW\nqKXFqdca3O6it+OdKGQuVnuXq1JDQULrMpT6Vqh3wRbOSi+lcArWho4Ck4KNmSrk\nTuPGTRxR/QKBgEL16EYIUwyD9QXuFXgnp1UD1m3w+IZIZEqvy/QRP2xR0JAsUY1B\ngkqWUBUTChFYKyg6qW3lNArIIF7MpmcdEldyTRKwPJcaUtrwpOW+7oHmGNtnVgOW\ntgdjS9noLDdRVaTTTy6J9ColjgYeionwjMsAuJvOMhnc2zWfzPOaQtL9AoGAbT6r\nR3DbYfbAAQRvAz2YiXsJwn0DmzhcCTwJSeOhHIv9LlIAicOc4sFJrqeOwifQg2VL\nr9l2R11PyEhxFCk4clrOgHZUpWcXI/9APO2XNkNDeJAtLYUzzhcW2X2GqAM2BxEp\n/UknxnI8UIiw7mPbaC7ys7MCQY0gzzeUJ5Dhlt0CgYASh1/ny0dOX6tgFtRh0yUk\n9B+Fl7kFTwfnX2PzVl/YTWHRSASsSMq+P1fG53RV6eo+eWHgTwxKp4sv2nkWXXOM\nLxLm0WQqZEiz+62HYqlZvAfmp3VES8+g0xHC4kgNMDfeMAFN00LTPJkCF6cufXSg\ntEnGfO8DTxGWgXj6md7kYg==\n-----END PRIVATE KEY-----\n""",
    "client_email": "firebase-adminsdk-fbsvc@restaurant-data-backend.iam.gserviceaccount.com",
    "client_id": "115855681795792637429",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40restaurant-data-backend.iam.gserviceaccount.com",
    "universe_domain": "googleapis.com"
}

# --- STREAMLIT UI ---
st.title("Weekly Menu Generator with Gemini + Firebase")

try:
    # Firebase Admin Initialization
    try:
        firebase_admin.get_app(name="restaurant-app")
    except ValueError:
        cred = credentials.Certificate(FIREBASE_CREDENTIALS)
        firebase_admin.initialize_app(cred, name="restaurant-app")
    db = firestore.client(app=firebase_admin.get_app(name="restaurant-app"))

    # Firestore connection test
    try:
        db.collection("ingredient_inventory").limit(1).get()
        st.success("✅ Successfully connected to Firestore.")
    except Exception as e:
        st.error(f"❌ Firestore access error: {str(e)}")
        st.stop()

    # Initialize Gemini Model
    model = genai.GenerativeModel("gemini-1.5-flash")

    # User input for number of dishes
    num_dishes = st.number_input("Number of chef specials to generate", min_value=1, max_value=10, value=3)

    if st.button("Generate Weekly Chef Specials"):
        with st.spinner("Fetching ingredients and generating chef specials..."):
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
                ingredient_name = data.get("Ingredient", "").strip()
                expiry_str = data.get("Expiry Date", "01/01/2100")
                if not ingredient_name or not expiry_str:
                    st.warning(f"Skipping document {doc.id}: Missing 'Ingredient' or 'Expiry Date'")
                    continue
                try:
                    expiry_date = parse(expiry_str, dayfirst=True, fuzzy=False)
                    if expiry_date > today and ingredient_name not in available_ingredients:
                        available_ingredients.append(ingredient_name)
                except (ValueError, TypeError) as e:
                    st.warning(f"Skipping ingredient '{ingredient_name}' due to invalid expiry date: {expiry_str}")
                    continue

            if len(available_ingredients) < 4:
                st.warning(f"Only {len(available_ingredients)} ingredient(s) available. Dishes may be limited.")
            if not available_ingredients:
                st.error("No valid ingredients found in inventory. Please add ingredients to Firestore.")
                st.stop()

            # Step 2: Generate Chef Special Dishes
            chef_specials = []
            required_fields = ["name", "ingredients", "diet", "types", "flavor_profile", "cook_time", "prep_time", "price_usd", "allergens", "description"]

            for i in range(num_dishes):
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
  "cook_time": int,
  "prep_time": int,
  "price_usd": float,
  "allergens": "...",
  "description": "...",
  "chef_special": true
}}
"""

                try:
                    response = model.generate_content(prompt)
                    output = response.text
                except exceptions.RetryError:
                    st.error(f"Gemini API rate limit exceeded for dish {i+1}. Please try again later.")
                    continue
                except exceptions.GoogleAPIError as e:
                    st.error(f"Gemini API error for dish {i+1}: {str(e)}")
                    continue

                # Extract and validate JSON
                try:
                    json_match = re.search(r'\{.*\}', output, re.DOTALL)
                    if not json_match:
                        st.error(f"No valid JSON found in Gemini response for dish {i+1}.")
                        continue
                    json_text = json_match.group(0)
                    dish = json.loads(json_text)
                    dish['chef_special'] = True
                except json.JSONDecodeError as e:
                    st.error(f"Failed to parse JSON for dish {i+1}: {str(e)}")
                    continue

                # Validate dish JSON
                if all(field in dish and dish[field] for field in required_fields):
                    # Type validation
                    if not (isinstance(dish["cook_time"], int) and
                            isinstance(dish["prep_time"], int) and
                            isinstance(dish["price_usd"], (int, float)) and
                            isinstance(dish["name"], str)):
                        st.error(f"Invalid field types in dish: {dish['name']}")
                        continue
                    # Check for duplicate dish names
                    if db.collection("menu").where("name", "==", dish["name"]).get():
                        st.warning(f"Dish '{dish['name']}' already exists in menu. Skipping.")
                        continue
                    # Upload to Firestore
                    db.collection("menu").add(dish)
                    chef_specials.append(dish)
                else:
                    st.error(f"Invalid dish format for dish {i+1}: Missing or empty required fields")
                    continue

            if chef_specials:
                st.success(f"Generated and uploaded {len(chef_specials)} chef specials successfully!")
                for d in chef_specials:
                    st.markdown(f"**{d['name']}** - {d['description']}")
                    st.json(d)
            else:
                st.error("No chef specials were generated. Check ingredient inventory or try again.")

except Exception as e:
    st.error(f"❌ App initialization failed: {str(e)}")

# Instructions
st.markdown("""
---
**What This Does:**
- Pulls current, valid ingredients from Firebase.
- Uses Gemini to create new chef-special recipes.
- Validates and uploads each dish to the `menu` collection in Firestore.

**Coming Next:**
- Weekly planner integration
- Visual dashboard of menu items
- Ratings and AI-based dish scoring
""")
