from flask import Flask, render_template, request, redirect, url_for, flash
import google.generativeai as genai
import os
import logging
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a strong secret key

# Configure logging
logging.basicConfig(level=logging.ERROR)

# Set up the generative AI model
model = genai.GenerativeModel('gemini-pro')

# Fetch the API key from the environment variable
my_api_key_gemini = os.getenv('GEMINI_API_KEY')
if not my_api_key_gemini:
    raise ValueError("API key is not set in the environment variables.")

genai.configure(api_key=my_api_key_gemini)

# Define your 404 error handler to redirect to the index page
@app.errorhandler(404)
def page_not_found(e):
    return redirect(url_for('index'))

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        # Retrieve emotion and user input
        emotion = request.form.get('emotion')
        prompt = request.form.get('prompt', '').strip()
        
        if not emotion or not prompt:
            flash("Both emotion and detailed input are required!")
            return redirect(url_for('index'))
        
        # Construct a customized prompt for Gemini based on user input
        full_prompt = (
            f"You are an empathetic virtual assistant. The user is feeling {emotion}. "
            f"Respond in a caring, emotional way to the following situation: {prompt}."
        )

        try:
            response = model.generate_content(full_prompt)
            if response.text:
                formatted_response = format_response(response.text)
                return render_template('index.html', response=formatted_response)
            else:
                flash("Sorry, but Gemini couldn't provide an answer.")
        except Exception as e:
            logging.error(f"Error while generating content: {e}")
            flash("An error occurred while processing your request.")
    return render_template('index.html')

def format_response(text):
    """
    Format the response to improve readability with proper HTML tags.
    Replace markdown-like formatting (** and *) with HTML tags.
    """
    formatted = text.replace("**", "<strong>").replace("*", "<li>").replace("\n", "<br>")
    return f"<p>{formatted}</p>"

if __name__ == '__main__':
    app.run(debug=True)
