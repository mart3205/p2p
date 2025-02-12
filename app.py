from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from invoke_agent import askQuestion
import os
import logging

# Initialize Flask app
app = Flask(__name__, static_folder='static')
CORS(app)  # Allow requests from all origins for simplicity

# Agent details
agentId = "HUQTPLRJOU"  # INPUT YOUR AGENT ID HERE
agentAliasId = "SLUWQOMCK0"  # INPUT YOUR AGENT ALIAS ID HERE
theRegion = "us-west-2"

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')
logger = logging.getLogger()


@app.route('/')
def serve_index():
    """Serve the index.html page."""
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/chatbot')
def serve_chatbot():
    """Serve the chatbot.html page."""
    return send_from_directory(app.static_folder, 'chatbot.html')


@app.route('/ask', methods=['POST'])
def ask():
    """Endpoint to handle chatbot questions."""
    data = request.json
    question = data.get('question')
    session_id = data.get('sessionId', 'defaultSession')
    end_session = data.get('endSession', False)

    url = f'https://bedrock-agent-runtime.{theRegion}.amazonaws.com/agents/{agentId}/agentAliases/{agentAliasId}/sessions/{session_id}/text'
    print("URL:", url)
    try:
        # Log the incoming request for debugging
        logger.info(f"Received question: {question}")
        response = askQuestion(question, url, end_session)
        logger.info(f"Response: {response}")
        return jsonify({"response": response})
    except Exception as e:
        logger.error(f"Error occurred: {e}")
        return jsonify({"error": "An error occurred while processing your request."}), 500


if __name__ == '__main__':
    # Ensure debug mode is off in production
    app.run(debug=False, host='0.0.0.0', port=5000)
