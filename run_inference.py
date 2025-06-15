import pandas as pd
import boto3
import uuid
import yaml
from modules.response_gen import BedrockAgentClient

def load_config():
    """Load configuration from config.yaml"""
    with open('config/config.yaml', 'r') as file:
        return yaml.safe_load(file)

def process_test_data(input_file):
    """Process test.csv and update it with responses"""
    config = load_config()
    agent_client = BedrockAgentClient(region_name=config['aws']['region'])
    
    # Read test data
    try:
        df = pd.read_csv(input_file)
        if 'Questions' not in df.columns:
            raise ValueError("Input CSV must contain a 'Questions' column")
    except Exception as e:
        print(f"Error reading test.csv: {e}")
        return
    
    # Initialize responses list
    responses = []
    
    # Process each question
    for question in df['Questions']:
        session_id = str(uuid.uuid4())  # New session for each question
        result = agent_client.invoke_agent(
            agent_id=config['aws']['agent_id'],
            agent_alias_id=config['aws']['agent_alias_id'],
            input_text=question,
            session_id=session_id
        )
        responses.append(result['response'])
    
    # Add Responses column to DataFrame
    df['Responses'] = responses
    
    # Save updated DataFrame back to test.csv
    try:
        df.to_csv(input_file, index=False)
        print(f"Updated {input_file} with Responses column")
    except Exception as e:
        print(f"Error saving to {input_file}: {e}")

if __name__ == "__main__":
    input_file = "test.csv"
    process_test_data(input_file)