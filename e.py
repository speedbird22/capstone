import streamlit as st
import requests

# Your API key and Search Engine ID (cx)
API_KEY = "AIzaSyDdc6sOMuxWKwfNI_DdMNYs_2Jk2bMtTzY"
SEARCH_ENGINE_ID = "772abe5b13e1f4ff4"

def get_recipes(ingredients):
    # Join ingredients into a single search query
    query = f"recipes with {', '.join(ingredients)}"
    url = f"https://www.googleapis.com/customsearch/v1?q={query}&cx={SEARCH_ENGINE_ID}&key={API_KEY}"

    # Call Google Custom Search API
    response = requests.get(url)
    if response.status_code != 200:
        return []

    data = response.json()
    recipes = []

    for item in data.get("items", []):
        recipes.append({
            "title": item.get("title"),
            "link": item.get("link"),
            "snippet": item.get("snippet")
        })

    return recipes

# Streamlit App UI
st.set_page_config(page_title="Recipe Finder", page_icon="🍲")
st.title("🍲 Recipe Finder by Ingredients")
st.write("Enter the ingredients you have, and get recipe ideas!")

# User input
ingredients_input = st.text_input("Enter ingredients (comma-separated)", placeholder="e.g. eggs, tomatoes, cheese")

if st.button("Find Recipes"):
    ingredients = [ing.strip() for ing in ingredients_input.split(",") if ing.strip()]
    
    if ingredients:
        st.subheader("🍽️ Recipes You Can Make")
        recipes = get_recipes(ingredients)
        if recipes:
            for recipe in recipes:
                st.markdown(f"### [{recipe['title']}]({recipe['link']})")
                st.write(recipe['snippet'])
                st.markdown("---")
        else:
            st.warning("No recipes found. Try more common ingredients or check your network.")
    else:
        st.error("Please enter at least one valid ingredient.")
