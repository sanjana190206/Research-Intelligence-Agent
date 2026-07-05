import os
from dotenv import load_dotenv
from ibm_watsonx_ai import Credentials
from ibm_watsonx_ai.foundation_models import ModelInference

load_dotenv()

credentials = Credentials(
    url=os.getenv("IBM_URL"),
    api_key=os.getenv("IBM_API_KEY")
)

print("Connection successful")