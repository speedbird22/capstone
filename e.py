import streamlit as st
import google.generativeai as genai
import firebase_admin
from firebase_admin import credentials, firestore
import json
import random
from datetime import datetime, timedelta
from dateutil.parser import parse
import re
from google.api_core import exceptions
import pandas as pd
import matplotlib.pyplot as plt

# --- CONFIGURATION ---
# Gemini API Key
genai.configure(api_key="AIzaSyCYcfiDp7bM0dpvJadYxuh4_-yF1ONh2dc")

# Firebase Service Account Key
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
st.title("Weekly Menu Generator with Recipe Archive")

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

    # Tabs for different functionalities
    tab1, tab2, tab3, tab4 = st.tabs(["Generate Menu", "Weekly Planner", "Menu Dashboard", "Chef Recipe Submission"])

    # --- TAB 1: Generate Chef Specials ---
    with tab1:
        st.header("Generate Weekly Chef Specials")
        num_dishes = st.number_input("Number of chef specials to generate", min_value=1, max_value=10, value=3)

        if st.button("Generate Chef Specials"):
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
                        dish['source'] = 'Gemini'
                        dish['created_at'] = datetime.now().isoformat()
                        dish['rating'] = None  # No rating for Gemini-generated dishes
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
                        # Upload to Firestore menu and recipe_archive
                        db.collection("menu").add(dish)
                        db.collection("recipe_archive").add(dish)
                        chef_specials.append(dish)
                    else:
                        st.error(f"Invalid dish format for dish {i+1}: Missing or empty required fields")
                        continue

                if chef_specials:
                    st.success(f"Generated and uploaded {len(chef_specials)} chef specials to menu and recipe archive successfully!")
                    for d in chef_specials:
                        st.markdown(f"**{d['name']}** - {d['description']}")
                        st.json(d)
                else:
                    st.error("No chef specials were generated. Check ingredient inventory or try again.")

    # --- TAB2: Weekly Planner ---
    with tab2:
        st.header("Weekly Planner")
        days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        selected_day = st.selectbox("Select day to assign chef specials", days_of_week)
        selected_dishes = st.multiselect("Select chef specials to assign", 
                                        [doc.to_dict().get("name") for doc in db.collection("menu").where("chef_special", "==", True).stream()])

        if st.button("Assign to Weekly Planner"):
            with st.spinner(f"Assigning dishes to {selected_day}..."):
                # Check existing planner entries for the day
                planner_ref = db.collection("weekly_planner").document(selected_day)
                existing = planner_ref.get()
                existing_dishes = existing.to_dict().get("dishes", []) if existing.exists else []

                # Avoid duplicates
                new_dishes = [dish for dish in selected_dishes if dish not in existing_dishes]
                if not new_dishes:
                    st.warning(f"No new dishes to add to {selected_day}.")
                else:
                    updated_dishes = existing_dishes + new_dishes
                    planner_ref.set({"dishes": updated_dishes, "day": selected_day})
                    st.success(f"Assigned {len(new_dishes)} dishes to {selected_day} successfully!")

        # Display Weekly Planner
        st.subheader("Current Weekly Planner")
        for day in days_of_week:
            planner_doc = db.collection("weekly_planner").document(day).get()
            if planner_doc.exists:
                dishes = planner_doc.to_dict().get("dishes", [])
                st.markdown(f"**{day}**: {', '.join(dishes) if dishes else 'No dishes assigned'}")
            else:
                st.markdown(f"**{day}**: No dishes assigned")

    # --- TAB 3: Menu Dashboard ---
    with tab3:
        st.header("Menu Dashboard")
        show_only_chef_specials = st.checkbox("Show only chef specials", value=False)

        # Fetch menu items
        menu_items = []
        query = db.collection("menu").where("chef_special", "==", True) if show_only_chef_specials else db.collection("menu")
        for doc in query.stream():
            dish = doc.to_dict()
            menu_items.append({
                "Name": dish.get("name", ""),
                "Type": dish.get("types", ""),
                "Diet": dish.get("diet", ""),
                "Price (USD)": dish.get("price_usd", 0.0),
                "Cook Time (min)": dish.get("cook_time", 0),
                "Prep Time (min)": dish.get("prep_time", 0),
                "Allergens": dish.get("allergens", ""),
                "Rating": dish.get("rating", "N/A")
            })

        # Display table
        if menu_items:
            st.dataframe(pd.DataFrame(menu_items), use_container_width=True)
        else:
            st.info("No menu items found.")

        # Visualize dish types
        if menu_items:
            type_counts = pd.DataFrame(menu_items)["Type"].value_counts()
            plt.figure(figsize=(8, 6))
            type_counts.plot(kind="bar", color="skyblue")
            plt.title("Distribution of Dish Types")
            plt.xlabel("Dish Type")
            plt.ylabel("Count")
            plt.grid(True)
            plt.savefig("dish_types.png")
            st.image("dish_types.png")
            plt.close()

    # --- TAB 4: Chef Recipe Submission ---
    with tab4:
        st.header("Chef Recipe Submission")
        
        # Check if it's time to prompt for weekly submissions
        last_submission_check = db.collection("config").document("last_submission_check").get()
        today = datetime.today()
        should_prompt = False

        if last_submission_check.exists:
            last_check = parse(last_submission_check.to_dict().get("date", "2000-01-01"))
            if today >= last_check + timedelta(days=7):
                should_prompt = True
        else:
            should_prompt = True

        if should_prompt:
            st.info("It's time for chefs to submit their weekly recipes! Please enter your recipe below.")
            db.collection("config").document("last_submission_check").set({"date": today.isoformat()})

        # Chef recipe input form
        with st.form("chef_recipe_form"):
            chef_name = st.text_input("Chef Name")
            dish_name = st.text_input("Dish Name")
            ingredients = st.text_area("Ingredients (comma-separated)")
            diet = st.selectbox("Diet", ["Vegetarian", "Vegan", "Gluten-Free", "Non-Vegetarian", "Other"])
            dish_type = st.selectbox("Type", ["main", "side", "dessert"])
            flavor_profile = st.text_input("Flavor Profile")
            cook_time = st.number_input("Cook Time (minutes)", min_value=1, value=30)
            prep_time = st.number_input("Prep Time (minutes)", min_value=1, value=15)
            price_usd = st.number_input("Price (USD)", min_value=0.0, value=10.0, step=0.5)
            allergens = st.text_input("Allergens (comma-separated)")
            description = st.text_area("Description")
            submitted = st.form_submit_button("Submit Recipe")

            if submitted:
                if not all([chef_name, dish_name, ingredients, diet, dish_type, flavor_profile, cook_time, prep_time, price_usd, allergens, description]):
                    st.error("All fields are required!")
                else:
                    # Prepare dish data
                    dish = {
                        "name": dish_name,
                        "ingredients": ingredients,
                        "diet": diet,
                        "types": dish_type,
                        "flavor_profile": flavor_profile,
                        "cook_time": int(cook_time),
                        "prep_time": int(prep_time),
                        "price_usd": float(price_usd),
                        "allergens": allergens,
                        "description": description,
                        "chef_special": True,
                        "source": f"Chef {chef_name}",
                        "created_at": datetime.now().isoformat(),
                        "rating": None
                    }

                    # Rate the dish with Gemini
                    rating_prompt = f"""
Evaluate the following chef-submitted recipe and provide a rating out of 10 based on creativity, feasibility, and appeal:
- Name: {dish_name}
- Ingredients: {ingredients}
- Diet: {diet}
- Type: {dish_type}
- Flavor Profile: {flavor_profile}
- Description: {description}

Provide a JSON response:
{{
  "rating": int,
  "comment": "..."
}}
"""
                    try:
                        response = model.generate_content(rating_prompt)
                        rating_output = response.text
                        json_match = re.search(r'\{.*\}', rating_output, re.DOTALL)
                        if json_match:
                            rating_data = json.loads(json_match.group(0))
                            dish["rating"] = rating_data.get("rating", 0)
                            dish["rating_comment"] = rating_data.get("comment", "")
                        else:
                            st.warning("Could not parse Gemini rating response. Saving dish without rating.")
                    except exceptions.GoogleAPIError as e:
                        st.error(f"Gemini API error while rating dish: {str(e)}")
                        dish["rating_comment"] = "Rating failed due to API error."

                    # Check for duplicate dish names
                    if db.collection("menu").where("name", "==", dish["name"]).get():
                        st.warning(f"Dish '{dish['name']}' already exists in menu. Skipping.")
                    else:
                        # Save to menu and recipe_archive
                        db.collection("menu").add(dish)
                        db.collection("recipe_archive").add(dish)
                        st.success(f"Recipe '{dish_name}' submitted and rated successfully! Rating: {dish.get('rating', 'N/A')}")
                        if dish.get("rating_comment"):
                            st.markdown(f"**Gemini Comment**: {dish['rating_comment']}")

        # Display archived recipes
        st.subheader("Recipe Archive")
        archive_items = []
        for doc in db.collection("recipe_archive").stream():
            dish = doc.to_dict()
            archive_items.append({
                "Name": dish.get("name", ""),
                "Source": dish.get("source", ""),
                "Rating": dish.get("rating", "N/A"),
                "Type": dish.get("types", ""),
                "Created At": dish.get("created_at", "")
            })

        if archive_items:
            st.dataframe(pd.DataFrame(archive_items), use_container_width=True)
        else:
            st.info("No recipes in archive yet.")

except Exception as e:
    st.error(f"❌ App initialization failed: {str(e)}")

# Instructions
st.markdown("""
---
**What This Does:**
- Pulls current, valid ingredients from Firebase.
- Uses Gemini to create new chef-special recipes and stores them in both `menu` and `recipe_archive` collections.
- Allows chefs to submit recipes weekly, which are rated by Gemini and stored in `menu` and `recipe_archive`.
- Assigns chef specials to a weekly planner for specific days.
- Displays a visual dashboard of menu items with filtering and a dish type chart.
- Shows an archive of all recipes with their source and ratings.

**Coming Next:**
- Enhanced AI-based dish scoring with customer feedback integration
""")
