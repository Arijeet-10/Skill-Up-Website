from flask import Flask, render_template, request, jsonify
import pickle
import re
import logging
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load resources from JSON file
def load_resources():
    try:
        with open('resources/resources.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logging.error("resources.json not found!")
        return {}

resources_db = load_resources()

# Job openings data
def load_job_openings():
    try:
        with open('resources/job_openings.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logging.error("job_openings.json not found!")
        return {}

# Load job openings from JSON file
job_openings = load_job_openings()

job_titles = set(job_openings.keys())

# Load translations from JSON
def load_translations():
    try:
        with open('resources/translations.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logging.error("translations.json not found!")
        return {}

translations = load_translations()

# Load the trained ML model if available
def load_model():
    try:
        with open('emails.pkl', 'rb') as file:
            return pickle.load(file)
    except FileNotFoundError:
        logging.warning("No ML model found. Using basic logic.")
        return None

model = load_model()

# Translation function
def translate_text(text, target_language):
    if target_language in translations and text in translations[target_language]:
        return translations[target_language][text]
    return text  # Return original if translation not found

@app.route('/')
def index():
    """Render the main input page."""
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    """Predict resources based on user input."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        role = data.get('role', '').strip().lower()
        skills = [skill.strip().lower() for skill in data.get('skills', '').split(',') if skill.strip()] if data.get('skills') else []
        skill_gaps = data.get('skill_gaps', '').strip().lower()
        career_ambitions = data.get('career_ambitions', '').strip().lower()
        language = data.get('language', '').strip().lower()

        # Combine inputs to determine resources
        recommendations = {"courses": [], "videos": [], "jobs": [], "roadmap": []}
        combined_inputs_string = ' '.join(skills + [role, skill_gaps, career_ambitions]).strip()

        # Create regex patterns for all resource keys
        resource_patterns = {key: re.compile(r'\b' + re.escape(key) + r'\b') for key in resources_db}

        # Search resources based on input words/phrases
        for resource_key, pattern in resource_patterns.items():
            if pattern.search(combined_inputs_string):
                recommendations["courses"].extend(resources_db[resource_key].get("courses", []))
                recommendations["videos"].extend(resources_db[resource_key].get("videos", []))
                recommendations["roadmap"].extend(resources_db[resource_key].get("roadmap", []))

        # Search job openings based on exact matches of job titles
        job_title_patterns = {key: re.compile(r'\b' + re.escape(key) + r'\b') for key in job_titles}
        for job_title, pattern in job_title_patterns.items():
            if pattern.search(combined_inputs_string):
                recommendations["jobs"].extend(job_openings.get(job_title, []))

        # Remove duplicates
        recommendations["courses"] = list({v["name"]: v for v in recommendations["courses"]}.values())
        recommendations["videos"] = list({v["name"]: v for v in recommendations["videos"]}.values())
        recommendations["jobs"] = list({v["title"]: v for v in recommendations["jobs"]}.values())
        recommendations["roadmap"] = list({v["step"]: v for v in recommendations["roadmap"]}.values())

        # Translate content
        for course in recommendations["courses"]:
            course["name"] = translate_text(course["name"], language)
        for video in recommendations["videos"]:
            video["name"] = translate_text(video["name"], language)
        for job in recommendations["jobs"]:
            job["title"] = translate_text(job["title"], language)
        for step in recommendations["roadmap"]:
            step["step"] = translate_text(step["step"], language)
            step["description"] = translate_text(step["description"], language)

        # Add a message
        if language:
            recommendations['message'] = f"{translate_text('Resources tailored for you in', language)} {language}!"
        else:
            recommendations['message'] = "Resources tailored for you!"

        return jsonify(recommendations)

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=os.getenv('FLASK_DEBUG', 'False').lower() == 'true')