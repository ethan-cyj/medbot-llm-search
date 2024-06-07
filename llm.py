import os
import json
from dotenv import load_dotenv
load_dotenv()
from ibm_watsonx_ai import Credentials
from ibm_watsonx_ai.foundation_models import Model

PROJECT_ID = os.getenv("PROJECT_ID")
SPACE_ID = os.getenv("SPACE_ID")
IBM_CLOUD_APIKEY = os.getenv("IBM_CLOUD_APIKEY")
IBM_CLOUD_REGION = os.getenv("IBM_CLOUD_REGION")


credentials = Credentials(
                   url = f"https://{IBM_CLOUD_REGION}.ml.cloud.ibm.com",
                   api_key = IBM_CLOUD_APIKEY,
                  )

model_id = "ibm/granite-13b-chat-v2"
parameters = {
    "decoding_method": "greedy",
    "max_new_tokens": 1000,
    "repetition_penalty": 1
}

class MedBot:
    def __init__(self, patient_id, visit_id):
        self.model = Model(
            model_id = model_id,
            params = parameters,
            credentials = credentials,
            project_id = PROJECT_ID,
            space_id = SPACE_ID
        )
        self.patient_id = patient_id
        self.visit_id = visit_id
        self.instruction = "Instruction: You are MedBot, a medical doctor and pharmacist and assistant chatbot at Tan Tock Seng Hospital, offering clear and comprehensive explanations on prescriptions and medical procedures. Your goal is to provide simplified answers to inquiries, catering to individuals with poor medical literacy. Answer may take reference to the provided context.\n"

    def build_prompt(self, user_query, prescription_info, visit_info, to_retrieve, handle_search):
        # Example of fetching data from a database
        # prescription_info = formatted_prescriptions(self.visit_id)
        # visit_info = formatted_visits(self.patient_id)
        return f"{self.instruction}\n\nInput: {user_query}\n\nPrescriptions: {prescription_info}\n\nVisits: {visit_info}\n\n{self.retrieve_information(to_retrieve, handle_search)}\nOutput:"

    def retrieve_information(self, input_text_list, handle_search):
        results = []
        n =6//len(input_text_list)
        for input_text in input_text_list:
            rag_info = handle_search(input_text, n, 8)
            results.append(rag_info[0])
        return "Retrieved information from hospital database: \n" + str(results)
    
    def generate_response(self, user_query, prescription_info, visit_info, handle_search, intent):
        if intent == "medicine":
            to_retrieve = prescription_info
        elif intent == "disease":
            to_retrieve = visit_info
        input_text = self.build_prompt(user_query,  prescription_info, visit_info, to_retrieve, handle_search)
        print(input_text)
        response = self.model.generate(prompt=input_text, guardrails=False)
        bot_response = response["results"][0]["generated_text"]
        return bot_response

# # Usage example:
# # Assuming dbfunctions and fetch_medication_info are already implemented and work as expected.
# patient_id = "S1234567A"
# visit_id = 1 # arthritis case
