import os
import base64
import json
from typing import Dict, Any, List, Optional
import anthropic
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Anthropic client
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPICS_API_KEY"))

def encode_pdf_to_base64(file_path: str) -> str:
    """
    Encode a PDF file to base64
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        Base64 encoded string
    """
    with open(file_path, "rb") as pdf_file:
        encoded_string = base64.b64encode(pdf_file.read()).decode("utf-8")
    return encoded_string

def analyze_team_pdf(file_path: str, is_our_team: bool, prompt_path: str=None ) -> Dict[str, Any]:
    """
    Analyze a team's PDF using Claude 3.7 Anthropic API
    
    Args:
        file_path: Path to the PDF file
        is_our_team: Whether this is our team (True) or opponent (False)
        
    Returns:
        Dictionary containing analysis results
    """
    # Load prompt template
    if prompt_path is None:
        prompt_path = os.path.join("app/prompts", "team_analysis_prompt.txt")
    with open(prompt_path, "r") as file:
        prompt_template = file.read()
    
    # Encode PDF to base64
    pdf_base64 = encode_pdf_to_base64(file_path)
    
    # Create message with PDF attachment
    message = client.messages.create(
        model="claude-3-7-sonnet-20250219",
        max_tokens=4000,
        temperature=0.0,
        system=f"You are an expert basketball analyst. You are analyzing a PDF containing basketball statistics for a {'team' if is_our_team else 'opponent team'}.",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "document",
                        "source": {
                            "type": "base64",
                            "media_type": "application/pdf",
                            "data": pdf_base64
                        }
                    },
                    {
                        "type": "text",
                        "text": prompt_template
                    }
                ]
            }
        ]
    )
    
    # Extract and parse JSON from response
    try:
        # Look for JSON in the response
        response_text = message.content[0].text
        json_start = response_text.find('{')
        json_end = response_text.rfind('}') + 1
        
        if json_start >= 0 and json_end > json_start:
            json_str = response_text[json_start:json_end]
            analysis = json.loads(json_str)
            
            # Post-process to ensure team stats are populated
            analysis = post_process_team_stats(analysis)
            
            return analysis
        else:
            # If no JSON found, return empty dict
            return {}
    except Exception as e:
        print(f"Error parsing JSON from Claude response: {e}")
        return {}

def post_process_team_stats(analysis: Dict[str, Any]) -> Dict[str, Any]:
    """
    Post-process team statistics to ensure all fields are populated
    
    Args:
        analysis: Dictionary containing team analysis
        
    Returns:
        Dictionary with post-processed team statistics
    """
    # Check if team_stats exists
    if "team_stats" not in analysis:
        analysis["team_stats"] = {}
    
    # Get players data
    players = analysis.get("players", [])
    
    # Calculate missing team stats from player stats if needed
    if players:
        # Calculate PPG if it's 0 or missing
        if analysis["team_stats"].get("PPG", 0) == 0:
            total_ppg = sum(player.get("stats", {}).get("PPG", 0) for player in players)
            # If we have player PPG, use it as an estimate
            if total_ppg > 0:
                analysis["team_stats"]["PPG"] = round(total_ppg, 1)
        
        # Calculate REB if it's 0 or missing
        if analysis["team_stats"].get("REB", 0) == 0:
            total_rpg = sum(player.get("stats", {}).get("RPG", 0) for player in players)
            if total_rpg > 0:
                analysis["team_stats"]["REB"] = round(total_rpg, 1)
        
        # Calculate AST if it's 0 or missing
        if analysis["team_stats"].get("AST", 0) == 0:
            total_apg = sum(player.get("stats", {}).get("APG", 0) for player in players)
            if total_apg > 0:
                analysis["team_stats"]["AST"] = round(total_apg, 1)
        
        # Calculate STL if it's 0 or missing
        if analysis["team_stats"].get("STL", 0) == 0:
            total_spg = sum(player.get("stats", {}).get("SPG", 0) for player in players)
            if total_spg > 0:
                analysis["team_stats"]["STL"] = round(total_spg, 1)
        
        # Calculate BLK if it's 0 or missing
        if analysis["team_stats"].get("BLK", 0) == 0:
            total_bpg = sum(player.get("stats", {}).get("BPG", 0) for player in players)
            if total_bpg > 0:
                analysis["team_stats"]["BLK"] = round(total_bpg, 1)
        
        # Calculate TO if it's 0 or missing
        if analysis["team_stats"].get("TO", 0) == 0:
            total_topg = sum(player.get("stats", {}).get("TOPG", 0) for player in players)
            if total_topg > 0:
                analysis["team_stats"]["TO"] = round(total_topg, 1)
        
        # Estimate OREB and DREB if REB is available but they're not
        if analysis["team_stats"].get("REB", 0) > 0:
            if analysis["team_stats"].get("OREB", 0) == 0 and analysis["team_stats"].get("DREB", 0) == 0:
                # Typical split is about 30% offensive, 70% defensive
                reb = analysis["team_stats"]["REB"]
                analysis["team_stats"]["OREB"] = round(reb * 0.3, 1)
                analysis["team_stats"]["DREB"] = round(reb * 0.7, 1)
    
    return analysis

def simulate_game(team_analysis: Dict[str, Any], opponent_analysis: Dict[str, Any]) -> Dict[str, Any]:
    """
    Simulate a game between two teams using Claude 3.7 Anthropic API
    
    Args:
        team_analysis: Dictionary containing our team analysis
        opponent_analysis: Dictionary containing opponent team analysis
        
    Returns:
        Dictionary containing simulation results
    """
    # Load prompt template
    prompt_path = os.path.join("app/prompts", "game_simulation_prompt.txt")
    with open(prompt_path, "r") as file:
        prompt_template = file.read()
    
    # Create combined analysis for the prompt
    combined_analysis = {
        "team": team_analysis,
        "opponent": opponent_analysis
    }
    
    # Create message
    message = client.messages.create(
        model="claude-3-7-sonnet-20250219",
        max_tokens=4000,
        temperature=0.2,  # Slightly higher temperature for simulation variety
        system="You are an expert basketball analyst and simulator. You are simulating a game between two basketball teams based on their statistics.",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt_template + "\n\n" + json.dumps(combined_analysis, indent=2)
                    }
                ]
            }
        ]
    )
    
    # Extract and parse JSON from response
    try:
        # Look for JSON in the response
        response_text = message.content[0].text
        json_start = response_text.find('{')
        json_end = response_text.rfind('}') + 1
        
        if json_start >= 0 and json_end > json_start:
            json_str = response_text[json_start:json_end]
            return json.loads(json_str)
        else:
            # If no JSON found, return empty dict
            return {}
    except Exception as e:
        print(f"Error parsing JSON from Claude response: {e}")
        return {}
