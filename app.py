from flask import Flask, render_template, request, jsonify, session
import boto3
import uuid
import json
from datetime import datetime
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # Generate a random secret key

class BedrockAgentClient:
    def __init__(self, region_name='us-west-2'):
        self.client = boto3.client('bedrock-agent-runtime', region_name=region_name)
        self.active_sessions = {}  # Store active sessions
   
    def create_new_session(self, user_id=None):
        """Create a new session ID"""
        if user_id:
            session_id = f"user_{user_id}_{str(uuid.uuid4())[:8]}"
        else:
            session_id = str(uuid.uuid4())
       
        # Store session metadata if needed
        self.active_sessions[session_id] = {
            'created_at': datetime.now(),
            'user_id': user_id,
            'message_count': 0
        }
       
        return session_id
   
    def invoke_agent(self, agent_id, agent_alias_id, input_text, session_id=None):
        """Invoke the Bedrock agent"""
       
        # Generate new session if not provided
        if not session_id:
            session_id = self.create_new_session()
       
        try:
            
            response = self.client.invoke_agent(
                agentId=agent_id,
                agentAliasId=agent_alias_id,
                sessionId=session_id,
                inputText=input_text
            )
           
            # Process streaming response
            result = ""
            for event in response['completion']:
                if 'chunk' in event:
                    chunk = event['chunk']
                    if 'bytes' in chunk:
                        result += chunk['bytes'].decode('utf-8')
           
            # Update session metadata
            if session_id in self.active_sessions:
                self.active_sessions[session_id]['message_count'] += 1
           
            return {
                'response': result,
                'session_id': session_id
            }
           
        except Exception as e:
            print(f"Error invoking agent: {e}")
            return {
                'response': f"Sorry, I encountered an error: {str(e)}",
                'session_id': session_id,
                'error': True
            }

from dotenv import load_dotenv
import os

load_dotenv()
AGENT_ID = os.getenv("AGENT_ID")
AGENT_ALIAS_ID = os.getenv("AGENT_ALIAS_ID")

agent_client = BedrockAgentClient()


@app.route('/')
def index():
    """Render the main chat interface"""
    return render_template('chat.html')

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        # Get or create session ID
        bedrock_session_id = session.get('bedrock_session_id')
        
        # Initialize conversation history if not exists
        if 'conversation' not in session:
            session['conversation'] = []
        
        # Invoke the Bedrock agent
        result = agent_client.invoke_agent(
            agent_id=AGENT_ID,
            agent_alias_id=AGENT_ALIAS_ID,
            input_text=user_message,
            session_id=bedrock_session_id
        )
        
        if result:
            # Store the session ID for future requests
            session['bedrock_session_id'] = result['session_id']
            
            # Add to conversation history
            session['conversation'].append({
                'user': user_message,
                'bot': result['response'],
                'timestamp': datetime.now().isoformat()
            })
            
            # Keep only last 50 messages to prevent session from getting too large
            if len(session['conversation']) > 50:
                session['conversation'] = session['conversation'][-50:]
            
            return jsonify({
                'response': result['response'],
                'session_id': result['session_id'],
                'error': result.get('error', False)
            })
        else:
            return jsonify({'error': 'Failed to get response from agent'}), 500
            
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/clear', methods=['POST'])
def clear_conversation():
    """Clear the current conversation"""
    session.pop('bedrock_session_id', None)
    session.pop('conversation', None)
    return jsonify({'message': 'Conversation cleared'})

@app.route('/history')
def get_history():
    """Get conversation history"""
    conversation = session.get('conversation', [])
    return jsonify({'conversation': conversation})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)