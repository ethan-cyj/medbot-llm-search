from flask import Flask, request, jsonify
from search import Search
from llm import MedBot
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = Flask(__name__)

@app.route('/generate_response', methods=['POST'])
def generate_response():
    data = request.get_json()
    user_question = data.get('user_question')
    prescription_info = data.get('prescription_info')
    visit_info = data.get('visit_info')
    patient_id = data.get('patient_id')
    visit_id = data.get('visit_id')
    intent = data.get('intent')

    es = Search()
    med_bot = MedBot(patient_id, visit_id)
    handle_search = es.handle_search
    response = med_bot.generate_response(user_question, prescription_info, visit_info, handle_search, intent)
    
    return jsonify({"response": response})

if __name__ == '__main__':
    print("Starting server...")
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
