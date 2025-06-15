import boto3
from datetime import datetime
import uuid

class BedrockAgentClient:
    def __init__(self, region_name='us-west-2'):
        self.client = boto3.client('bedrock-agent-runtime', region_name=region_name)
        self.active_sessions = {}
   
    def create_new_session(self, user_id=None):
        """Create a new session ID"""
        if user_id:
            session_id = f"user_{user_id}_{str(uuid.uuid4())[:8]}"
        else:
            session_id = str(uuid.uuid4())
       
        self.active_sessions[session_id] = {
            'created_at': datetime.now(),
            'user_id': user_id,
            'message_count': 0
        }
       
        return session_id
   
    def invoke_agent(self, agent_id, agent_alias_id, input_text, session_id=None):
        """Invoke the Bedrock agent"""
        if not session_id:
            session_id = self.create_new_session()
       
        try:
            response = self.client.invoke_agent(
                agentId=agent_id,
                agentAliasId=agent_alias_id,
                sessionId=session_id,
                inputText=input_text
            )
            result = ""
            for event in response['completion']:
                if 'chunk' in event:
                    chunk = event['chunk']
                    if 'bytes' in chunk:
                        result += chunk['bytes'].decode('utf-8')
           
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