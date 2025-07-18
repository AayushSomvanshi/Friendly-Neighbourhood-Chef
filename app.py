import os
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai

# Initialize the Flask application
app = Flask(__name__)

# --- AI and API Configuration ---
try:
    # Get the API key from environment variables
    GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
    genai.configure(api_key=GOOGLE_API_KEY)
except TypeError:
    # This error occurs if the API key is not set
    print("\nERROR: The GOOGLE_API_KEY environment variable is not set.")
    print("Please get your API key from https://aistudio.google.com/app/apikey")
    exit()

# Create the Generative AI model
model = genai.GenerativeModel('gemini-1.5-flash') # Using the fast and capable Flash model

# --- Application Routes ---

@app.route("/")
def home():
    """
    Serves the main HTML page for the application.
    Flask will automatically look for 'index.html' in a 'templates' folder.
    """
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate_recipe():
    """
    Handles the recipe generation request from the frontend.
    """
    try:
        # Get the data sent from the frontend JavaScript
        data = request.get_json()
        ingredients = data.get("ingredients")
        dietary_style = data.get("diet", "any") # Default to 'any' if not provided

        if not ingredients:
            return jsonify({"error": "No ingredients provided."}), 400

        # Craft a detailed prompt for the AI
        prompt = f"""
        You are an expert and caring home cook from North India, skilled at making simple and comforting "ghar jaisa khana" (homemade food).
        Your task is to create a delicious, authentic North Indian recipe using the ingredients provided.

        **Provided Ingredients:** {ingredients}
        **Dietary Style:** {dietary_style}

        The recipe must be:
        - **Authentically North Indian** in style.
        - **Simple to make** with standard kitchen equipment.
        - **Written in plain, easy-to-understand language**, as if you were explaining it to a friend.

        Assume the user has basic Indian pantry staples like: oil, ghee, salt, turmeric (haldi), cumin seeds (jeera), coriander powder (dhania powder), and red chili powder (lal mirch).

        Please format the response with these exact sections:
        ### Recipe Title
        A simple and clear name for the dish.

        ### Ingredients
        - A bulleted list of all ingredients with exact quantities (e.g., 1 cup, 2 tsp).

        ### Instructions
        1. Numbered, step-by-step instructions that are very easy to follow.
        """

        # Send the prompt to the AI model
        response = model.generate_content(prompt)
        
        # Return the AI's generated text in a JSON response
        return jsonify({"recipe": response.text})

    except Exception as e:
        # Handle any potential errors during the API call
        print(f"An error occurred: {e}")
        return jsonify({"error": "Failed to generate recipe from AI."}), 500


@app.route("/modify", methods=["POST"])
def modify_recipe():
    """
    Handles a follow-up request to modify an existing recipe.
    """
    try:
        data = request.get_json()
        original_recipe = data.get("original_recipe")
        modification_request = data.get("modification_request")

        if not original_recipe or not modification_request:
            return jsonify({"error": "Missing data for modification."}), 400

        # This prompt provides the AI with the conversational context
        prompt = f"""
        You are a helpful North Indian home cook assistant.
        A user was given the following recipe:

        ---
        **Original Recipe:**
        {original_recipe}
        ---

        Now, the user has a follow-up request: "{modification_request}"

        Please rewrite the entire recipe from scratch to incorporate the user's request.
        For example, if they need a substitute, replace the ingredient and adjust the instructions accordingly. And mention the changes made like- "you may use this instead of that" or "no problem, can be made without this item too" etc
        If they want it spicier, add more chili and note it in the instructions.

        Respond with the complete, updated recipe. Maintain the exact same formatting as before, with "### Recipe Title", "### Ingredients", and "### Instructions" sections.
        """
        
        response = model.generate_content(prompt)
        
        return jsonify({"recipe": response.text})

    except Exception as e:
        print(f"An error occurred during modification: {e}")
        return jsonify({"error": "Failed to modify recipe."}), 500

if __name__ == "__main__":
    # Runs the Flask app in debug mode for development
    app.run(debug=True)