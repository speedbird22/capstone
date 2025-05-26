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
    tab1, tab2, tab3 = st.tabs(["Generate Weekly Menu", "Menu Dashboard", "Chef Recipe Submission"])

    # --- TAB 1: Generate Weekly Menu ---
    with tab1:
        st.header("Generate Weekly Menu")
        
        # Fetch ingredients from Firestore
        try:
            docs = db.collection("ingredient_inventory").stream()
        except Exception as e:
            st.error(f"Failed to fetch ingredients from Firestore: {str(e)}")
            docs = []
        available_ingredients = []
        today = datetime.today()
        ingredient_data = []

        for doc in docs:
            data = doc.to_dict()
            ingredient_name = data.get("Ingredient", "").strip()
            expiry_str = data.get("Expiry Date", "01/01/2100")
            quantity = data.get("Quantity", 0)  # Assuming quantity is stored
            if not ingredient_name or not expiry_str:
                st.warning(f"Skipping document {doc.id}: Missing 'Ingredient' or 'Expiry Date'")
                continue
            try:
                expiry_date = parse(expiry_str, dayfirst=True, fuzzy=False)
                if expiry_date > today and ingredient_name not in available_ingredients:
                    available_ingredients.append(ingredient_name)
                    ingredient_data.append({
                        "name": ingredient_name,
                        "expiry_date": expiry_date,
                        "quantity": quantity,
                        "days_to_expiry": (expiry_date - today).days
                    })
            except (ValueError, TypeError) as e:
                st.warning(f"Skipping ingredient '{ingredient_name}' due to invalid expiry date: {expiry_str}")
                continue

        if not available_ingredients:
            st.error("No valid ingredients found in inventory. Please add ingredients to Firestore.")
            st.stop()

        # Select top 4 ingredients (close to expiry or high quantity)
        sorted_ingredients = sorted(ingredient_data, key=lambda x: (x["days_to_expiry"], -x["quantity"]))
        top_ingredients = [ing["name"] for ing in sorted_ingredients[:4]]
        selected_ingredients = st.multiselect(
            "Select up to 4 priority ingredients (sorted by expiry date and quantity)",
            available_ingredients,
            default=top_ingredients[:4],
            max_selections=4
        )

        # Seasonal ingredients (hard-coded for simplicity; could be dynamic)
        month = today.month
        seasonal_ingredients = {
            1: ["kale", "brussels sprouts", "citrus fruits"],  # Winter
            2: ["kale", "brussels sprouts", "citrus fruits"],
            3: ["asparagus", "spinach", "radishes"],  # Spring
            4: ["asparagus", "spinach", "radishes"],
            5: ["asparagus", "spinach", "radishes"],
            6: ["strawberries", "zucchini", "peas"],  # Summer
            7: ["strawberries", "zucchini", "peas"],
            8: ["strawberries", "zucchini", "peas"],
            9: ["apples", "pumpkin", "squash"],  # Fall
            10: ["apples", "pumpkin", "squash"],
            11: ["apples", "pumpkin", "squash"],
            12: ["kale", "brussels sprouts", "citrus fruits"]
        }.get(month, ["tomatoes", "cucumbers"])  # Default

        if st.button("Generate Weekly Menu"):
            with st.spinner("Generating weekly menu..."):
                # Clear existing weekly menu
                for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
                    db.collection("weekly_menu").document(day).delete()

                # Generate menu: Special Items, Seasonal Items, Normal Items
                menu_items = []
                required_fields = ["name", "ingredients", "diet", "types", "flavor_profile", "cook_time", "prep_time", "price_usd", "allergens", "description", "category"]

                # Special Items (based on selected ingredients)
                if selected_ingredients:
                    for i in range(2):  # Generate 2 special dishes
                        prompt = f"""
Using the following priority ingredients: {', '.join(selected_ingredients)},
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
  "category": "Special Items"
}}
"""
                        try:
                            response = model.generate_content(prompt)
                            output = response.text
                            json_match = re.search(r'\{.*\}', output, re.DOTALL)
                            if not json_match:
                                st.error(f"No valid JSON found for special dish {i+1}.")
                                continue
                            dish = json.loads(json_match.group(0))
                            dish['category'] = "Special Items"
                            dish['source'] = 'Gemini'
                            dish['created_at'] = datetime.now().isoformat()
                            dish['rating'] = None
                            if all(field in dish and dish[field] for field in required_fields):
                                if db.collection("menu").where("name", "==", dish["name"]).get():
                                    st.warning(f"Dish '{dish['name']}' already exists. Skipping.")
                                    continue
                                db.collection("menu").add(dish)
                                db.collection("recipe_archive").add(dish)
                                menu_items.append(dish)
                        except (exceptions.GoogleAPIError, json.JSONDecodeError) as e:
                            st.error(f"Error generating special dish {i+1}: {str(e)}")
                            continue

                # Seasonal Items
                for i in range(2):  # Generate 2 seasonal dishes
                    sample_seasonal = random.sample(seasonal_ingredients, min(2, len(seasonal_ingredients)))
                    prompt = f"""
Using the following seasonal ingredients: {', '.join(sample_seasonal)},
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
  "category": "Seasonal Items"
}}
"""
                    try:
                        response = model.generate_content(prompt)
                        output = response.text
                        json_match = re.search(r'\{.*\}', output, re.DOTALL)
                        if not json_match:
                            st.error(f"No valid JSON found for seasonal dish {i+1}.")
                            continue
                        dish = json.loads(json_match.group(0))
                        dish['category'] = "Seasonal Items"
                        dish['source'] = 'Gemini'
                        dish['created_at'] = datetime.now().isoformat()
                        dish['rating'] = None
                        if all(field in dish and dish[field] for field in required_fields):
                            if db.collection("menu").where("name", "==", dish["name"]).get():
                                st.warning(f"Dish '{dish['name']}' already exists. Skipping.")
                                continue
                            db.collection("menu").add(dish)
                            db.collection("recipe_archive").add(dish)
                            menu_items.append(dish)
                    except (exceptions.GoogleAPIError, json.JSONDecodeError) as e:
                        st.error(f"Error generating seasonal dish {i+1}: {str(e)}")
                        continue

                # Normal Items
                for i in range(3):  # Generate 3 normal dishes
                    sample_ings = random.sample(available_ingredients, min(4, len(available_ingredients)))
                    prompt = f"""
Using the following ingredients: {', '.join(sample_ings)},
create a standard dish suitable for a weekly restaurant menu.

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
  "category": "Normal Items"
}}
"""
                    try:
                        response = model.generate_content(prompt)
                        output = response.text
                        json_match = re.search(r'\{.*\}', output, re.DOTALL)
                        if not json_match:
                            st.error(f"No valid JSON found for normal dish {i+1}.")
                            continue
                        dish = json.loads(json_match.group(0))
                        dish['category'] = "Normal Items"
                        dish['source'] = 'Gemini'
                        dish['created_at'] = datetime.now().isoformat()
                        dish['rating'] = None
                        if all(field in dish and dish[field] for field in required_fields):
                            if db.collection("menu").where("name", "==", dish["name"]).get():
                                st.warning(f"Dish '{dish['name']}' already exists. Skipping.")
                                continue
                            db.collection("menu").add(dish)
                            db.collection("recipe_archive").add(dish)
                            menu_items.append(dish)
                    except (exceptions.GoogleAPIError, json.JSONDecodeError) as e:
                        st.error(f"Error generating normal dish {i+1}: {str(e)}")
                        continue

                # Assign menu to all days
                if menu_items:
                    for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
                        db.collection("weekly_menu").document(day).set({
                            "dishes": [dish["name"] for dish in menu_items],
                            "day": day
                        })
                    st.success(f"Generated weekly menu with {len(menu_items)} dishes and assigned to all days!")
                    for dish in menu_items:
                        st.markdown(f"**{dish['name']}** ({dish['category']}) - {dish['description']}")
                        st.json(dish)
                else:
                    st.error("No dishes generated. Check ingredient inventory or try again.")

        # Display Weekly Menu
        st.subheader("Current Weekly Menu")
        for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
            planner_doc = db.collection("weekly_menu").document(day).get()
            if planner_doc.exists:
                dishes = planner_doc.to_dict().get("dishes", [])
                st.markdown(f"**{day}**: {', '.join(dishes) if dishes else 'No dishes assigned'}")
            else:
                st.markdown(f"**{day}**: No dishes assigned")

    # --- TAB 2: Menu Dashboard ---
    with tab2:
        st.header("Menu Dashboard")
        show_category = st.selectbox("Filter by Category", ["All", "Special Items", "Seasonal Items", "Normal Items", "Chef Special Items"])

        # Fetch menu items
        menu_items = []
        query = db.collection("menu")
        if show_category != "All":
            query = query.where("category", "==", show_category)
        for doc in query.stream():
            dish = doc.to_dict()
            menu_items.append({
                "Name": dish.get("name", ""),
                "Category": dish.get("category", ""),
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

        # Visualize dish categories
        if menu_items:
            category_counts = pd.DataFrame(menu_items)["Category"].value_counts()
            plt.figure(figsize=(8, 6))
            category_counts.plot(kind="bar", color="skyblue")
            plt.title("Distribution of Dish Categories")
            plt.xlabel("Category")
            plt.ylabel("Count")
            plt.grid(True)
            plt.savefig("dish_categories.png")
            st.image("dish_categories.png")
            plt.close()

    # --- TAB 3: Chef Recipe Submission ---
    with tab3:
        st.header("Chef Recipe Submission")
        
        # Check for weekly submission prompt
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
                        "category": "Chef Special Items",
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
                "Category": dish.get("category", ""),
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
- Pulls current, valid ingredients from Firebase and allows selection of up to 4 priority ingredients (sorted by expiry date and quantity).
- Generates a weekly menu with Special Items (using priority ingredients), Seasonal Items (using seasonal ingredients), and Normal Items, applied to all days.
- Stores all generated dishes in both `menu` and `recipe_archive` collections with a `category` field (Special Items, Seasonal Items, Normal Items, Chef Special Items).
- Allows chefs to submit recipes weekly, which are rated by Gemini and stored in `menu` and `recipe_archive` as Chef Special Items.
- Displays a visual dashboard of menu items with category filtering and a dish category chart.
- Shows an archive of all recipes with their category, source, and ratings.

**Coming Next:**
- Enhanced AI-based dish scoring with customer feedback integration
""")
