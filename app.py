from flask import Flask, request, jsonify
from search import Search
from llm import MedBot
from cloudant import CloudantClient
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
    history = data.get('history')
    additional_info = data.get('additional_info')

    es = Search()
    med_bot = MedBot(patient_id, visit_id)
    handle_search = es.handle_search
    response = med_bot.generate_response(user_question, prescription_info, visit_info, handle_search, intent, history, additional_info)
    
    return jsonify({"response": response})

@app.route('/get_patient', methods=['POST'])
def get_patient():
    data = request.get_json()
    patient_id = data.get('patient_id')
    visit_id = data.get('visit_id')

    cloudant_client = CloudantClient()
    patient_info = cloudant_client.query_patient_info(patient_id, visit_id)

    if "error" in patient_info:
        return jsonify({"error": patient_info["error"]}), 404

    return jsonify(patient_info)

if __name__ == '__main__':
    print("Starting server...")
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))


# curl -X POST https://medbot-llm-search.1gpmytaegikv.us-south.codeengine.appdomain.cloud[/](https://medbot-llm-search.1gpmytaegikv.us-south.codeengine.appdomain.cloud/)[generate_response](http://localhost:8081/generate_response) \

# curl -X POST http://localhost:8080/generate_response \
#      -H "Content-Type: application/json" \
#      -d '{
#            "user_question": "What does my medication for this visit do?",
#            "prescription_info": ["Methotrexate", "Ibuprofen", "Folic Acid"],
#            "visit_info": ["Arthritis"],
#            "patient_id": "S1234567A",
#            "visit_id": 1,
#            "intent": "medicine",
#            "history": []
#            "additional_info": ["smoker", "seafood allergy", "nut allergy", "pregnant"]"
#          }'


# curl -X POST http://localhost:8080/get_patient \
#      -H "Content-Type: application/json" \
#      -d '{
#            "patient_id": 1,
#            "visit_id": 1,
#          }'