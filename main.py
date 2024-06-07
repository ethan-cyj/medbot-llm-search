from search import Search
from llm import MedBot
user_question = "What does my medication for this visit do?"
prescription_info = ["Methotrexate","Ibuprofen","Folic Acid"]
visit_info = ["Arthritis"]
patient_id = "S1234567A"
visit_id = 1
intent = "medicine"

es = Search()
med_bot = MedBot(patient_id, visit_id)
handle_search = es.handle_search
response = med_bot.generate_response(user_question, prescription_info, visit_info, handle_search, intent)
print(response)
