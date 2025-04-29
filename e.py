import streamlit as st
import google.generativeai as genai

# Configure Gemini API
genai.configure(api_key="AIzaSyCYcfiDp7bM0dpvJadYxuh4_-yF1ONh2dc")

# Initialize the Gemini model
model = genai.GenerativeModel("gemini-1.5-flash")

# Streamlit app title
st.title("Recipe Finder with Gemini API")

# User input for ingredients
ingredients = st.text_input("Enter ingredients (comma-separated, e.g., chicken, rice, broccoli):")

# Button to generate recipe
if st.button("Find Recipe"):
    if not ingredients:
        st.error("Please enter at least one ingredient.")
    else:
        # Clean and process ingredients
        ingredients_list = [ing.strip() for ing in ingredients.split(",")]
        
        # Create prompt for Gemini API
        prompt = f"Generate a detailed recipe using the following ingredients: {', '.join(ingredients_list)}. Include a title, ingredients list, step-by-step instructions, and serving suggestions. If some ingredients are not typically used together, suggest reasonable substitutions or additions to make a cohesive dish."
        
        try:
            # Call Gemini API
            response = model.generate_content(prompt)
            
            # Display the recipe
            if response.text:
                st.markdown("### Generated Recipe")
                st.write(response.text)
            else:
                st.error("No recipe generated. Please try again or adjust your ingredients.")
                
        except Exception as e:
            st.error(f"An error occurred while contacting the Gemini API: {str(e)}")

# Instructions for users
st.markdown("""
**How to use:**
1. Enter a list of ingredients separated by commas (e.g., "tomato, pasta, cheese").
2. Click the "Find Recipe" button.
3. View the generated recipe with ingredients, instructions, and serving suggestions.

**Note:** Ensure the Gemini API key is valid and has sufficient quota.
""")
