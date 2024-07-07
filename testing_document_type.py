import requests
import os
from transformers import BertTokenizer
# Initialize the tokenizer
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')

# Get the Hugging Face API key from environment variable
hf_inference_api_key = os.getenv("HF_INFERENCE_API_KEY")

# Define the API URL and headers
doc_type_API_URL = "https://api-inference.huggingface.co/models/jogoni/autotrain-cuad-document-type-2883884341"
doc_type_headers = {"Authorization": f"Bearer {hf_inference_api_key}"}

# Function to query the Hugging Face API
def query(payload):
    response = requests.post(doc_type_API_URL, headers=doc_type_headers, json=payload)
    return response.json()

# Define the input text
input_text = '''THIS AGREEMENT (“Agreement”), made and entered into this 17th day of November, 2015, by and between the
TOWN OF VINTON, VIRGINIA, a Virginia municipal corporation (“Grantor”), and ROANOKE GAS COMPANY, a Virginia
corporation (“Grantee”).
WHEREAS, Grantor has reviewed the proposal for a Gas Franchise of Grantee; and
WHEREAS, Grantor, at a duly authorized and regular meeting of its Town Council, did vote to grant a renewal of the Gas
Franchise to Grantee pursuant to provisions of the State Code and Town Charter.
NOW, THEREFORE, in consideration of said grant of renewal of the Gas Franchise, the parties agree as follows:
1. GRANT. Grantor hereby grants to Grantee and Grantee hereby accepts a franchise to construct, reconstruct, operate,
maintain, repair, and extend a Gas Distribution System within Grantor’s Territorial Limits in accordance with the terms and
conditions set forth below (“Franchise”). The Franchise is granted pursuant to Grantor’s Franchise Ordinance (Ordinance No.
967), adopted November 17, 2015, (“Ordinance”), which is incorporated by reference herein, including any applicable definitions.
2. TERM. The term of the Franchise shall be twenty (20) years, commencing on January 1, 2016.
'''
# Tokenize and truncate the input text
inputs = tokenizer.encode(input_text, truncation=True, max_length=512, return_tensors="pt")

# Convert tokens back to string
truncated_text = tokenizer.decode(inputs[0], skip_special_tokens=True)
# Query the API with the input text
output = query({"inputs": truncated_text})

# Extract the first label from the output
first_label = output[0][0]['label'] if output and isinstance(output, list) and output[0] else None

# Print the first label
print(first_label)
