import os
import traceback
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from google import genai

# Load environment variables
load_dotenv()

app = Flask(__name__)

# --- API Setup ---
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY is not set. Check your .env file.")

client = genai.Client(api_key=GOOGLE_API_KEY)


# --- Helper: clean text ---
def clean_text(text):
    if not text:
        return ""
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    return "\n".join(lines)


# --- Routes ---

@app.route("/")
def home():
    return render_template("index.html")


# GENERATE 
@app.route("/generate", methods=["POST"])
def generate_recipe():
    try:
        data = request.get_json()

        ingredients = clean_text(str(data.get("ingredients", "")))
        dietary_style = clean_text(str(data.get("diet", "any")))

        if not ingredients:
            return jsonify({"error": "No ingredients provided."}), 400

        prompt = f"""
You are an expert and caring home cook from North India, skilled at making simple and comforting "ghar jaisa khana".

Create a delicious, authentic North Indian recipe.

Ingredients: {ingredients}
Dietary style: {dietary_style}

Guidelines:
- Keep it authentically North Indian
- Use simple home-style cooking methods
- Write in friendly, easy language (like explaining to a friend)
- Use common Indian kitchen words when appropriate (like tadka, bhunna)
- Assume basic pantry items are available (oil, ghee, haldi, jeera, dhania powder, mirch)

Format EXACTLY:

### Recipe Title

### Ingredients
- include clear quantities

### Instructions
1. step-by-step, practical and easy
"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        if not response.text:
            return jsonify({"error": "Empty response from AI"}), 500

        return jsonify({"recipe": response.text})

    except Exception as e:
        traceback.print_exc()
        return jsonify({
            "error": "Failed to generate recipe",
            "details": str(e)
        }), 500


# MODIFY
@app.route("/modify", methods=["POST"])
def modify_recipe():
    try:
        data = request.get_json()

        original_recipe = clean_text(data.get("original_recipe"))
        modification_request = clean_text(data.get("modification_request"))

        if not original_recipe or not modification_request:
            return jsonify({"error": "Missing data for modification."}), 400

        prompt = f"""
You are a caring North Indian home cook.

Here is a recipe:
{original_recipe}

User request:
{modification_request}

Modify the recipe accordingly, while keeping it:
- simple
- practical
- authentic "ghar jaisa khana"

Do not unnecessarily rewrite everything — only adjust what is needed.

Return FULL updated recipe in same format:

### Recipe Title
### Ingredients
### Instructions
"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        if not response.text:
            return jsonify({"error": "Empty response from AI"}), 500

        return jsonify({"recipe": response.text})

    except Exception as e:
        traceback.print_exc()
        return jsonify({
            "error": "Failed to modify recipe",
            "details": str(e)
        }), 500


if __name__ == "__main__":
    app.run(debug=True)