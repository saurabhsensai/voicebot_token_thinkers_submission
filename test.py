import boto3
import uuid

def invoke_bedrock_agent(agent_id, alias_id, session_id, prompt, region='us-west-2'):
    bedrock_runtime_client = boto3.client('bedrock-agent-runtime', region_name=region)
    
    try:
        response = bedrock_runtime_client.invoke_agent(
            agentId=agent_id,
            agentAliasId=alias_id,
            sessionId=session_id,
            inputText=prompt,
            enableTrace=False
        )
        
        completion = ""
        for event in response.get('completion'):
            if 'chunk' in event:
                chunk = event['chunk']
                completion += chunk['bytes'].decode('utf-8')
        
        return completion
    
    except Exception as e:
        print(f"Error invoking agent: {e}")
        return None

# Generate a unique session ID
session_id = str(uuid.uuid4())  # Unique for each conversation

# Example usage
agent_id = 'BBOJZQZWOX'  # Replace with your Agent ID
alias_id = 'GZWUUA4ZOJ'  # Replace with your Agent Alias ID
prompt = 'Summarize the benefits of using AWS Bedrock for AI development.'
region = 'us-west-2'

response_text = invoke_bedrock_agent(agent_id, alias_id, session_id, prompt, region)
if response_text:
    print(f"Agent response: {response_text}")
else:
    print("Failed to get a response from the agent.")