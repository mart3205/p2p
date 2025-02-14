from boto3.session import Session
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
import json
import os
from requests import request
import base64

# Set AWS profile and region
os.environ["AWS_PROFILE"] = "default"
theRegion = "us-west-2"
os.environ["AWS_REGION"] = theRegion
region = os.environ.get("AWS_REGION")

# Agent details
agentId = "HUQTPLRJOU"  # INPUT YOUR AGENT ID HERE
agentAliasId = "THD1M8AE6I"  # INPUT YOUR AGENT ALIAS ID HERE


def sigv4_request(
    url,
    method='GET',
    body=None,
    headers=None,
    service='execute-api',
    region=os.environ['AWS_REGION'],
    credentials=Session().get_credentials().get_frozen_credentials()
):
    """Sends an HTTP request signed with SigV4"""

    req = AWSRequest(
        method=method,
        url=url,
        data=body,
        headers=headers
    )
    SigV4Auth(credentials, service, region).add_auth(req)
    req = req.prepare()

    # Send request
    return request(
        method=req.method,
        url=req.url,
        headers=req.headers,
        data=req.body
    )

def askQuestion(question, url, endSession=False):
    # Prepare the payload
    payload = {
        "inputText": question,
        "enableTrace": False,
        "endSession": endSession
    }

    # Send the request to Bedrock Agent
    response = sigv4_request(
        url,
        method='POST',
        service='bedrock',
        headers={
            'content-type': 'application/json',
            'accept': 'application/json',
        },
        region=theRegion,
        body=json.dumps(payload)
    )

    print("RAW RESPONSE:", response.text)  # Debugging line

    return decode_response(response)
# Initiates the decoding reponse

def decode_response(response):

    # Convert stream in lines
    lines = list(response.iter_lines())
    if not lines:
        return "Error: La respuesta de Bedrock está vacía."
    
    print("RAW RESPONSE LINES:", lines)  # To debugging

    json_payload = ""
    # Looks for the line that contains character {
    for line in lines:
        try:
            decoded_line = line.decode('utf-8', errors='ignore')
        except Exception as e:
            print("Error al decodificar la línea:", e)
            continue
        pos = decoded_line.find('{')
        if pos != -1:
            json_payload = decoded_line[pos:]
            break

    if not json_payload:
        return "Error: No se encontró ningún payload JSON en el event stream."

    print("Extracted JSON payload:", json_payload)  # To Debug

    # JSONDecoder para extraer el primer objeto JSON y omitir datos extra
    try:
        decoder = json.JSONDecoder()
        response_json, idx = decoder.raw_decode(json_payload)
    except json.JSONDecodeError as e:
        return f"Error: Falló la decodificación del JSON. Detalle: {str(e)}"

    # Procesar la respuesta según el contenido
    if "bytes" in response_json:
        encoded_response = response_json["bytes"]
        missing_padding = len(encoded_response) % 4
        if missing_padding:
            encoded_response += "=" * (4 - missing_padding)
        try:
            decoded_response = base64.b64decode(encoded_response).decode('utf-8')
            return decoded_response
        except Exception as e:
            return f"Error en base64 decoding: {str(e)}"
    elif "text" in response_json:
        return response_json["text"]

    return "No valid response found."

# Example usage
def lambda_handler(event, context):
    sessionId = event["sessionId"]
    question = event["question"]
    endSession = event.get("endSession", False)

    url = f'https://bedrock-agent-runtime.{theRegion}.amazonaws.com/agents/{agentId}/agentAliases/{agentAliasId}/sessions/{sessionId}/text'
    print("URL:", url)
    try:
        response = askQuestion(question, url, endSession)
        return {
            "status_code": 200,
            "body": json.dumps({"response": response})
        }
    except Exception as e:
        print(f"Error in lambda_handler: {e}")  # Add error logging here
        return {
            "status_code": 500,
            "body": json.dumps({"error": str(e)})
        }
