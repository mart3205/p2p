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
agentAliasId = "XOWGBA2XMH"  # INPUT YOUR AGENT ALIAS ID HERE


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

def decode_response(response):
    response_content = ""

    try:
        for line in response.iter_lines():
            try:
                decoded_line = line.decode('utf-8').strip()
                if decoded_line and not decoded_line.startswith(":"):
                    response_content += decoded_line
            except UnicodeDecodeError:
                continue  # Ignorar líneas que no se puedan decodificar

        print("RAW RESPONSE (CLEAN):", response_content)  # Depuración

        # Intenta convertir la respuesta en JSON después de limpiar metadatos
        response_json = json.loads(response_content)

        # Manejo de datos en base64
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

        if "text" in response_json:
            return response_json["text"]

    except json.JSONDecodeError as e:
        return f"Error: Respuesta no es un JSON válido. Detalle: {str(e)}"

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
