import boto3
import uuid
import json
from datetime import datetime
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
            return None

# Usage example
agent_client = BedrockAgentClient()

# Scenario 1: New conversation
result = agent_client.invoke_agent(
    agent_id="BBOJZQZWOX",
    agent_alias_id="UOSO33VZKJ",
    input_text="Hello, how can you help me?"
)

print(f"Response: {result['response']}")


# Scenario 2: Continue existing conversation
session_id = result['session_id']  # Use the same session ID
result2 = agent_client.invoke_agent(
    agent_id="BBOJZQZWOX",
    agent_alias_id="UOSO33VZKJ",
    input_text="I am investing in Borrowing",
    session_id=session_id  
)