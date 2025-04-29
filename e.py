import streamlit as st
import google.generativeai as genai

# Configure the API key
genai.configure(api_key="AIzaSyDdc6sOMuxWKwfNI_DdMNYs_2Jk2bMtTzY")

# Set up the model
model = genai.GenerativeModel("gemini-pro")

# Streamlit interface
st.title("Recipe Suggestion App")
st.write("Enter your ingredients below, and I'll suggest some recipes you can make!")

# Get user input for ingredients
ingredients = st.text_input("Enter your ingredients (comma-separated):")

# Generate recipe suggestions
if ingredients:
    prompt = f"I have these ingredients: {ingredients}. What can I cook with them? Suggest 2 recipes with steps."
    
    # Generate the response from the API
    response = model.generate_content(prompt)

    # Display the response
    st.subheader("Recipe Suggestions:")
    st.write(response.text)
else:
    st.write("Please enter some ingredients to get started.")
