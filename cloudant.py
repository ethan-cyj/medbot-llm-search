from ibmcloudant.cloudant_v1 import CloudantV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_cloud_sdk_core import ApiException
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize Cloudant client
class CloudantClient:
    def __init__(self):
        self.api_key = os.getenv("IBM_CLOUD_APIKEY")
        self.url = os.getenv("CLOUDANT_URL")
        self.authenticator = IAMAuthenticator(self.api_key)
        self.client = CloudantV1(authenticator=self.authenticator)
        self.client.set_service_url(self.url)
        self.db_name = "patient_info"

    def query_patient_info(self, patient_id, visit_id):
        selector = {
            "patient_id": patient_id,
            "visits": {
                "$elemMatch": {
                    "visit_id": visit_id
                }
            }
        }

        try:
            response = self.client.post_find(
                db=self.db_name,
                selector=selector
            ).get_result()

            if response['docs']:
                patient_doc = response['docs'][0]
                visit_info = next(visit for visit in patient_doc['visits'] if visit['visit_id'] == visit_id)
                return {
                    "visit_id": visit_id,
                    "prescription_info": visit_info['prescription_info'],
                    "visit_info": visit_info['visit_info'],
                    "patient_id": patient_doc['patient_id'],
                    "NRIC": patient_doc['nric'],
                    "first_name": patient_doc['first_name'],
                    "last_name": patient_doc['last_name'],
                    "email": patient_doc['email'],
                    "additional_info": patient_doc['additional_info']
                }
            else:
                return {"error": "No documents found."}
        except ApiException as ae:
            return {"error": str(ae)}