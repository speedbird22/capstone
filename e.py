import streamlit as st
import requests
import urllib.parse

# Streamlit page configuration
st.set_page_config(page_title="Recipe Generator", page_icon="🍳", layout="wide")

# Google API credentials (replace with your own)
GOOGLE_API_KEY = "YOUR_API_KEY"  # Replace with your new Google API key
GOOGLE_CSE_ID = "YOUR_CSE_ID"    # Replace with your Custom Search Engine ID

# Title and description
st.title("Multi-Cuisine Recipe Generator")
st.markdown("Enter the ingredients you have, and I'll find recipes you can make! Powered by Google Custom Search.")

# Function to search for recipes using Google Custom Search API
def search_recipes(ingredients):
    if not GOOGLE_API_KEY or GOOGLE_API_KEY == "YOUR_API_KEY" or not GOOGLE_CSE_ID or GOOGLE_CSE_ID == "YOUR_CSE_ID":
        st.error("Please set valid Google API Key and CSE ID in the code.")
        return []
    
    query = f"recipes with {ingredients}"
    encoded_query = urllib.parse.quote(query)
    url = f"https://www.googleapis.com/customsearch/v1?key={GOOGLE_API_KEY}&cx={GOOGLE_CSE_ID}&q={encoded_query}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        results = response.json().get("items", [])
        return results
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching recipes: {str(e)}")
        return []

# Input form for ingredients
with st.form("ingredient_form"):
    ingredients = st.text_area(
        "Enter available ingredients (separated by commas, e.g., carrots, chicken, garlic):",
        placeholder="carrots, chicken, garlic"
    )
    submitted = st.form_submit_button("Find Recipes")

# Process form submission
if submitted and ingredients:
    st.subheader("Recipes You Can Make")
    ingredients_cleaned = ingredients.strip()
    if not ingredients_cleaned:
        st.warning("Please enter at least one ingredient.")
    else:
        # Search for recipes
        recipes = search_recipes(ingredients_cleaned)
        
        if not recipes:
            st.info("No recipes found. Try different ingredients or check your API setup.")
        else:
            # Display recipes
            for idx, recipe in enumerate(recipes, 1):
                title = recipe.get("title", "No title")
                link = recipe.get("link", "#")
                snippet = recipe.get("snippet", "No description available.")
                
                with st.expander(f"{idx}. {title}"):
                    st.markdown(f"**Link**: [{title}]({link})")
                    st.markdown(f"**Description**: {snippet}")
                    st.markdown("---")
else:
    st.info("Enter ingredients and click 'Find Recipes' to see what you can cook!")

# Footer
st.markdown("---")
st.markdown("Built with ❤️ using Streamlit and Google Custom Search API.")
