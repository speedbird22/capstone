import streamlit as st
import google.generativeai as genai

# Configure the new API key
genai.configure(api_key="AIzaSyCYcfiDp7bM0dpvJadYxuh4_-yF1ONh2dc")

# Set up the model (using a commonly available model like 'text-bison')
model = genai.GenerativeModel("text-bison")

# Streamlit interface
st.title("Recipe Suggestion App")
st.write("Enter your ingredients below, and I'll suggest some recipes you can make!")

# Get user input for ingredients
ingredients = st.text_input("Enter your ingredients (comma-separated):")

# Generate recipe suggestions
if ingredients:
    prompt = f"I have these ingredients: {ingredients}. What can I cook with them? Suggest 2 recipes with steps."
    
    try:
        # Generate the response from the API
        response = model.generate_content(prompt)

        # Display the response
        st.subheader("Recipe Suggestions:")
        st.write(response.text)
    except Exception as e:
        st.write("Error: Unable to fetch recipe suggestions. Please try again later.")
        st.write(f"Details: {str(e)}")
else:
    st.write("Please enter some ingredients to get started.")
