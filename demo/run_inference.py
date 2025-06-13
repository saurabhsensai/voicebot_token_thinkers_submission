import pandas as pd
import os
from modules.asr_module import WhisperASR

def main():
    # Initialize ASR model
    asr = WhisperASR()
    
    # Read test.csv (assuming it has a column 'Audio_Path' with audio file paths)
    test_data = pd.read_csv("test.csv")
    audio_paths = test_data["Questions"].tolist()  # Assuming Questions column contains audio file paths
    
    # Generate transcriptions
    transcriptions = asr.process_batch(audio_paths)
    
    # Save results to output.csv
    output_df = pd.DataFrame({
        "Questions": audio_paths,
        "Responses": transcriptions
    })
    output_df.to_csv("output.csv", index=False)

if __name__ == "__main__":
    main()