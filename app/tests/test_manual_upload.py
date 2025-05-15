import requests
import os
import time
import json

# Base URL of the API
BASE_URL = "http://127.0.0.1:8000"

def run_upload_test(use_local_simulation: bool = False):
    """
    Test the upload endpoint with the PDF files from data/input_samples
    
    Args:
        use_local_simulation: Whether to use local statistical simulation instead of AI
    """
    # Paths to the PDF files
    team_file_path = "../data/input_samples/SCARSDALE Last 5 games individual stats.pdf"
    opponent_file_path = "../data/input_samples/ARLINGTON Last 5 games INDIVIDUAL stats.pdf"
    
    # Check if the files exist
    if not os.path.exists(team_file_path):
        print(f"Team file not found: {team_file_path}")
        return
    
    if not os.path.exists(opponent_file_path):
        print(f"Opponent file not found: {opponent_file_path}")
        return
    
    # Prepare the files and data for the request
    files = {
        "team_files": open(team_file_path, "rb"),
        "opponent_files": open(opponent_file_path, "rb")
    }
    
    data = {
        "team_name": "Scarsdale",
        "opponent_name": "Arlington",
        "use_local_simulation": use_local_simulation
    }
    
    try:
        # Send the POST request
        print("Uploading files...")
        response = requests.post(f"{BASE_URL}/api/upload/", files=files, data=data)
        
        # Close the file handles
        files["team_files"].close()
        files["opponent_files"].close()
        
        # Check the response
        if response.status_code == 200:
            result = response.json()
            task_id = result.get("task_id")
            print(f"Upload successful. Task ID: {task_id}")
            
            # Poll the status endpoint until the processing is complete
            print("Waiting for processing to complete...")
            status = "processing"
            while status == "processing":
                time.sleep(5)  # Wait for 5 seconds before checking again
                status_response = requests.get(f"{BASE_URL}/api/status/{task_id}")
                if status_response.status_code == 200:
                    status_result = status_response.json()
                    status = status_result.get("status")
                    print(f"Current status: {status}")
                else:
                    print(f"Error checking status: {status_response.status_code}")
                    break
            
            # If processing is complete, download the reports
            if status == "completed":
                print("Processing complete. Downloading reports...")
                
                # Download the combined report
                report_response = requests.get(f"{BASE_URL}/api/download/{task_id}")
                if report_response.status_code == 200:
                    with open("combined_report.docx", "wb") as f:
                        f.write(report_response.content)
                    print("Combined report downloaded: combined_report.docx")
                else:
                    print(f"Error downloading combined report: {report_response.status_code}")
                
                # Download the team analysis report
                team_report_response = requests.get(f"{BASE_URL}/api/download-team-analysis/{task_id}")
                if team_report_response.status_code == 200:
                    with open("team_analysis.docx", "wb") as f:
                        f.write(team_report_response.content)
                    print("Team analysis report downloaded: team_analysis.docx")
                else:
                    print(f"Error downloading team analysis report: {team_report_response.status_code}")
                
                # Download the opponent analysis report
                opponent_report_response = requests.get(f"{BASE_URL}/api/download-opponent-analysis/{task_id}")
                if opponent_report_response.status_code == 200:
                    with open("opponent_analysis.docx", "wb") as f:
                        f.write(opponent_report_response.content)
                    print("Opponent analysis report downloaded: opponent_analysis.docx")
                else:
                    print(f"Error downloading opponent analysis report: {opponent_report_response.status_code}")
                
                # Check the analyses endpoint
                print("Checking analyses endpoint...")
                analyses_response = requests.get(f"{BASE_URL}/api/analyses")
                if analyses_response.status_code == 200:
                    print("Analyses endpoint working")
                else:
                    print(f"Error accessing analyses endpoint: {analyses_response.status_code}")
            else:
                print(f"Processing failed with status: {status}")
                if "error" in status_result:
                    print(f"Error message: {status_result['error']}")
        else:
            print(f"Upload failed with status code: {response.status_code}")
            print(f"Response: {response.text}")
    
    except Exception as e:
        print(f"Error: {e}")

def test_upload():
    """
    Run tests for both AI and local simulation methods
    """
    print("\n=== Testing AI-based simulation ===")
    run_upload_test(use_local_simulation=False)
    
    print("\n=== Testing local statistical simulation ===")
    run_upload_test(use_local_simulation=True)

if __name__ == "__main__":
    test_upload()
