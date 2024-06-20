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

model_id = "meta-llama/llama-3-70b-instruct" #"ibm/granite-13b-chat-v2"
parameters = {
    "decoding_method": "greedy",
    "max_new_tokens": 400,
    "repetition_penalty": 1,
    "stop_sequence": ["[End]", "[Stop]"]
}

class MedBot:
    def __init__(self, patient_id, visit_id):
        self.model = Model(
            model_id=model_id,
            params=parameters,
            credentials=credentials,
            project_id=PROJECT_ID,
            space_id=SPACE_ID
        )
        self.patient_id = patient_id
        self.visit_id = visit_id
        self.instruction = ("<|system|>\nInstruction: You are MedBot, a medical doctor and assistant chatbot at Tan Tock Seng Hospital, "
                            "offering clear and comprehensive explanations on prescriptions and medical procedures. "
                            "Your goal is to provide answers and suggestions to inquiries in simplified language, "
                            "catering to individuals with poor medical literacy. There is no need to introduce yourself. "
                            "Answer should take reference to the available context if suitable. "
                            "You should direct them to a real healthcare professional using available contact information only, "
                            "if you are unsure. Do not make up information or use placeholders, "
                            "do not tell me to insert contact information. Your response is concise, non-repetitive and summarized. "
                            "Do use point-form if necessary.\n")

    def build_prompt(self, user_query, prescription_info, visit_info, to_retrieve, handle_search, history, additional_info):
        if not history:
            history = ""
        
        rag_output_text, rag_output_sources = self.retrieve_information(to_retrieve, handle_search)
        
        document_section = (f"<|user|>\n[Document]\n{history}"
                            f"Prescriptions: {prescription_info}\n\n"
                            f"Visits: {visit_info}\n\n"
                            f"Additional Patient Info: {additional_info}\n\n"
                            f"Retrieved information from hospital database: {rag_output_text}\n[End]\n"
                            f"User query: {user_query}\n<|assistant|>\n[Start]")
        
        return f"{self.instruction}\n\n{document_section}", rag_output_sources

    def retrieve_information(self, input_text_list, handle_search):
        results = []
        sources = []
        n = 6 // len(input_text_list)
        for input_text in input_text_list:
            rag_info = handle_search(input_text, n, 8)
            for i in rag_info:
                results.append(i[0])
                if i[1] not in sources:
                    sources.append(i[1])
        return str(results), sources

    def format_history(self, history):
        output = "Last Query History:\n"
        for entry in history:
            output += f"\n- User: {entry["user_question"]}\n- Response: {entry["response"]}\n"
        return output + "\n\n"
    
    def generate_response(self, user_query, prescription_info, visit_info, handle_search, intent, history=None, additional_info=[]):
        if intent == "medicine":
            to_retrieve = prescription_info
        elif intent == "disease":
            to_retrieve = visit_info
        else:
            to_retrieve = user_query
        
        if history:
            history = self.format_history(history)
        input_text, sources = self.build_prompt(user_query, prescription_info, visit_info, to_retrieve, handle_search, history, additional_info)
        
        print(input_text)
        response = self.model.generate(prompt=input_text, guardrails=False)
        #print(response)
        bot_response = response["results"][0]["generated_text"]
        return {
            "text": bot_response,
            "sources": sources
        }
