import os
import uuid
import shutil
import json
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks, Form, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import List, Optional, Dict, Any
from pathlib import Path
from datetime import datetime
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

from services.anthropic_api import analyze_team_pdf, simulate_game
from services.report_gen import generate_report
from database.connection import (
    insert_team, insert_team_stats, insert_player, insert_player_stats,
    insert_team_analysis, insert_game, insert_game_simulation, insert_report,
    get_recent_analyses, execute_query, insert_player_raw_stats,
    insert_player_projections, insert_simulation_details, find_player_by_name
)

# Set up Jinja2 templates
root = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(root, "../templates"))

router = APIRouter(
    prefix="/api",
    tags=["upload"],
    responses={404: {"description": "Not found"}},
)

# Dictionary to store processing status
processing_tasks = {}

# Processing steps for progress tracking
PROCESSING_STEPS = [
    "Analyzing team statistics",
    "Analyzing opponent statistics",
    "Storing data in database",
    "Generating team analysis report",
    "Generating opponent analysis report",
    "Simulating game",
    "Generating final report"
]

@router.get("/analyses", response_class=HTMLResponse)
async def get_analyses(request: Request):
    """
    Get recent analyses and display them on a webpage
    """
    # Get current user from request state
    user = getattr(request.state, "user", None)
    user_id = None
    
    # If user is authenticated, get or create user in database
    if user and "sub" in user and user["sub"]:
        from database.connection import get_or_create_user
        user_id = get_or_create_user(user["sub"], user.get("email", ""), user.get("name", ""))
    
    # Get analyses filtered by user_id
    analyses = get_recent_analyses(limit=10, user_id=user_id)
    
    return templates.TemplateResponse(
        "analyses.html", 
        {
            "request": request, 
            "analyses": analyses
        }
    )

@router.post("/upload/")
async def upload_files(
    background_tasks: BackgroundTasks,
    request: Request,
    team_files: UploadFile = File(...),
    opponent_files: UploadFile = File(...),
    team_name: Optional[str] = Form(None),
    opponent_name: Optional[str] = Form(None),
    use_local_simulation: Optional[bool] = Form(False)
):
    """
    Upload PDF files for analysis - one for our team and one for the opponent
    """
    # Validate files are PDFs
    if not team_files.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail=f"Team file {team_files.filename} is not a PDF")
    
    if not opponent_files.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail=f"Opponent file {opponent_files.filename} is not a PDF")
    
    # Create a unique task ID
    task_id = str(uuid.uuid4())
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    task_dir = f"/app/temp/uploads/{task_id}"
    os.makedirs(task_dir, exist_ok=True)
    
    # Save uploaded files
    file_paths = []
    
    # Save team file
    team_file_path = f"{task_dir}/team_{team_files.filename}"
    with open(team_file_path, "wb") as buffer:
        shutil.copyfileobj(team_files.file, buffer)
    file_paths.append(team_file_path)
    
    # Save opponent file
    opponent_file_path = f"{task_dir}/opponent_{opponent_files.filename}"
    with open(opponent_file_path, "wb") as buffer:
        shutil.copyfileobj(opponent_files.file, buffer)
    file_paths.append(opponent_file_path)
    
    # Initialize task status
    processing_tasks[task_id] = {
        "status": "processing",
        "files": [team_files.filename, opponent_files.filename],
        "timestamp": timestamp,
        "team_name": team_name,
        "opponent_name": opponent_name,
        "report_path": None,
        "current_step": 0,
        "total_steps": len(PROCESSING_STEPS),
        "step_description": PROCESSING_STEPS[0]
    }
    
    # Get current user from request state
    user = getattr(request.state, "user", None)
    
    # Process files in background
    background_tasks.add_task(
        process_files, 
        task_id, 
        file_paths, 
        team_name, 
        opponent_name,
        use_local_simulation,
        user
    )
    
    return {"task_id": task_id, "status": "processing"}

@router.get("/status/{task_id}")
async def get_status(task_id: str):
    """
    Get the status of a processing task
    """
    if task_id not in processing_tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return processing_tasks[task_id]

@router.get("/download/{task_id}")
async def download_report(task_id: str):
    """
    Download the generated report
    """
    # First check if task_id is in processing_tasks
    if task_id in processing_tasks:
        task = processing_tasks[task_id]
        
        if task["status"] != "completed":
            raise HTTPException(status_code=400, detail="Report not ready yet")
        
        if not task["report_path"] or not os.path.exists(task["report_path"]):
            raise HTTPException(status_code=404, detail="Report file not found")
        
        return FileResponse(
            path=task["report_path"],
            filename=os.path.basename(task["report_path"]),
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
    else:
        # If not in processing_tasks, check if it's a report ID in the database
        query = """
        SELECT r.file_path
        FROM reports r
        WHERE r.id = %s
        """
        
        result = execute_query(query, (task_id,))
        
        if not result or not result[0]["file_path"] or not os.path.exists(result[0]["file_path"]):
            raise HTTPException(status_code=404, detail="Report not found")
        
        return FileResponse(
            path=result[0]["file_path"],
            filename=os.path.basename(result[0]["file_path"]),
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

@router.get("/download-team-analysis/{task_id}")
async def download_team_analysis(task_id: str):
    """
    Download the team analysis report
    """
    # First check if task_id is in processing_tasks
    if task_id in processing_tasks:
        task = processing_tasks[task_id]
        
        if task["status"] != "completed":
            raise HTTPException(status_code=400, detail="Reports not ready yet")
        
        if not task.get("team_analysis_path") or not os.path.exists(task.get("team_analysis_path", "")):
            raise HTTPException(status_code=404, detail="Team analysis report not found")
        
        return FileResponse(
            path=task["team_analysis_path"],
            filename=os.path.basename(task["team_analysis_path"]),
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
    else:
        # If not in processing_tasks, check if it's a report ID in the database
        query = """
        SELECT r.file_path
        FROM reports r
        JOIN games g ON r.game_id = g.id
        WHERE r.id = %s AND r.report_type = 'team_analysis'
        """
        
        result = execute_query(query, (task_id,))
        
        if not result or not result[0]["file_path"] or not os.path.exists(result[0]["file_path"]):
            raise HTTPException(status_code=404, detail="Team analysis report not found")
        
        return FileResponse(
            path=result[0]["file_path"],
            filename=os.path.basename(result[0]["file_path"]),
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

@router.get("/download-opponent-analysis/{task_id}")
async def download_opponent_analysis(task_id: str):
    """
    Download the opponent analysis report
    """
    # First check if task_id is in processing_tasks
    if task_id in processing_tasks:
        task = processing_tasks[task_id]
        
        if task["status"] != "completed":
            raise HTTPException(status_code=400, detail="Reports not ready yet")
        
        if not task.get("opponent_analysis_path") or not os.path.exists(task.get("opponent_analysis_path", "")):
            raise HTTPException(status_code=404, detail="Opponent analysis report not found")
        
        return FileResponse(
            path=task["opponent_analysis_path"],
            filename=os.path.basename(task["opponent_analysis_path"]),
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
    else:
        # If not in processing_tasks, check if it's a report ID in the database
        query = """
        SELECT r.file_path
        FROM reports r
        JOIN games g ON r.game_id = g.id
        WHERE r.id = %s AND r.report_type = 'opponent_analysis'
        """
        
        result = execute_query(query, (task_id,))
        
        if not result or not result[0]["file_path"] or not os.path.exists(result[0]["file_path"]):
            raise HTTPException(status_code=404, detail="Opponent analysis report not found")
        
        return FileResponse(
            path=result[0]["file_path"],
            filename=os.path.basename(result[0]["file_path"]),
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

@router.get("/download-by-path")
async def download_by_path(path: str):
    """
    Download a report by its file path
    """
    if not path or not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Report file not found")
    
    return FileResponse(
        path=path,
        filename=os.path.basename(path),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

def generate_team_analysis_report(analysis: Dict[str, Any], timestamp: str) -> str:
    """
    Generate a DOCX report for team analysis
    
    Args:
        analysis: Dictionary containing team analysis
        timestamp: Timestamp string for the filename
        
    Returns:
        Path to the generated report
    """
    team_name = analysis.get("team_name", "Team")
    
    # Create a new document
    doc = Document()
    
    # Add title
    title = doc.add_heading(f"{team_name} - Team Analysis", 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Add team info section
    doc.add_heading("Team Information", 1)
    doc.add_paragraph(f"Team: {team_name}")
    doc.add_paragraph(f"Record: {analysis.get('team_record', 'N/A')}")
    if analysis.get('team_ranking'):
        doc.add_paragraph(f"Ranking: {analysis.get('team_ranking')}")
    
    # Add team stats section
    doc.add_heading("Team Statistics", 1)
    team_stats = analysis.get("team_stats", {})
    stats_table = doc.add_table(rows=1, cols=2)
    stats_table.style = 'Table Grid'
    
    # Add header row
    header_cells = stats_table.rows[0].cells
    header_cells[0].text = "Statistic"
    header_cells[1].text = "Value"
    
    # Add stats rows
    for stat, value in team_stats.items():
        row_cells = stats_table.add_row().cells
        row_cells[0].text = stat
        row_cells[1].text = str(value)
    
    # Add team strengths section
    doc.add_heading("Team Strengths", 1)
    for strength in analysis.get("team_strengths", []):
        doc.add_paragraph(f"• {strength}", style='List Bullet')
    
    # Add team weaknesses section
    doc.add_heading("Team Weaknesses", 1)
    for weakness in analysis.get("team_weaknesses", []):
        doc.add_paragraph(f"• {weakness}", style='List Bullet')
    
    # Add key players section
    doc.add_heading("Key Players", 1)
    for player in analysis.get("key_players", []):
        doc.add_paragraph(f"• {player}", style='List Bullet')
    
    # Add playing style section
    if analysis.get("playing_style"):
        doc.add_heading("Playing Style", 1)
        doc.add_paragraph(analysis.get("playing_style"))
    
    # Add offensive keys section
    doc.add_heading("Offensive Keys", 1)
    for key in analysis.get("offensive_keys", []):
        doc.add_paragraph(f"• {key}", style='List Bullet')
    
    # Add defensive keys section
    doc.add_heading("Defensive Keys", 1)
    for key in analysis.get("defensive_keys", []):
        doc.add_paragraph(f"• {key}", style='List Bullet')
    
    # Add game factors section
    doc.add_heading("Game Factors", 1)
    for factor in analysis.get("game_factors", []):
        doc.add_paragraph(f"• {factor}", style='List Bullet')
    
    # Add rotation plan section
    if analysis.get("rotation_plan"):
        doc.add_heading("Rotation Plan", 1)
        doc.add_paragraph(analysis.get("rotation_plan"))
    
    # Add situational adjustments section
    doc.add_heading("Situational Adjustments", 1)
    for adjustment in analysis.get("situational_adjustments", []):
        doc.add_paragraph(f"• {adjustment}", style='List Bullet')
    
    # Add game keys section
    doc.add_heading("Game Keys", 1)
    for key in analysis.get("game_keys", []):
        doc.add_paragraph(f"• {key}", style='List Bullet')
    
    # Add player details section
    doc.add_heading("Player Details", 1)
    for player in analysis.get("players", [])[:5]:  # Top 5 players
        player_name = player.get("name", "")
        player_number = player.get("number", "")
        
        doc.add_heading(f"{player_name} #{player_number}", 2)
        
        # Add player stats
        stats = player.get("stats", {})
        player_stats_table = doc.add_table(rows=1, cols=2)
        player_stats_table.style = 'Table Grid'
        
        # Add header row
        header_cells = player_stats_table.rows[0].cells
        header_cells[0].text = "Statistic"
        header_cells[1].text = "Value"
        
        # Add stats rows
        for stat, value in stats.items():
            row_cells = player_stats_table.add_row().cells
            row_cells[0].text = stat
            row_cells[1].text = str(value)
        
        # Add player strengths
        doc.add_heading("Strengths", 3)
        for strength in player.get("strengths", []):
            doc.add_paragraph(f"• {strength}", style='List Bullet')
        
        # Add player weaknesses
        doc.add_heading("Weaknesses", 3)
        for weakness in player.get("weaknesses", []):
            doc.add_paragraph(f"• {weakness}", style='List Bullet')
    
    # Save the document
    report_dir = "/app/temp/reports"
    os.makedirs(report_dir, exist_ok=True)
    report_filename = f"{team_name} - Team Analysis - {timestamp}.docx"
    report_path = os.path.join(report_dir, report_filename)
    doc.save(report_path)
    
    return report_path

async def process_files(task_id: str, file_paths: List[str], team_name: Optional[str], opponent_name: Optional[str], use_local_simulation: bool = False, user: Optional[Dict] = None):
    """
    Process uploaded PDF files and generate a report
    """
    try:
        # Find team and opponent file paths
        team_file_path = next((path for path in file_paths if "team_" in os.path.basename(path)), None)
        opponent_file_path = next((path for path in file_paths if "opponent_" in os.path.basename(path)), None)
        
        if not team_file_path or not opponent_file_path:
            raise ValueError("Could not identify team and opponent files")
        
        print("-"*40 + "\n" + f"DEBUG - Processing team file: {team_file_path}")
        print(f"DEBUG - Processing opponent file: {opponent_file_path}")
        
        # Step 1: Analyze team PDF
        processing_tasks[task_id]["current_step"] = 0
        processing_tasks[task_id]["step_description"] = PROCESSING_STEPS[0]
        team_analysis = analyze_team_pdf(team_file_path, is_our_team=True)
        print("Generated team analysis")
        # print("-"*40 + "\n" + "DEBUG - Team Analysis:", team_analysis)

        # Step 2: Analyze opponent PDF
        processing_tasks[task_id]["current_step"] = 1
        processing_tasks[task_id]["step_description"] = PROCESSING_STEPS[1]
        opponent_analysis = analyze_team_pdf(opponent_file_path, is_our_team=False)
        print("Generated opponent analysis")
        # print("-"*40 + "\n" + "DEBUG - Opponent Analysis:", opponent_analysis)

        # Override team names if provided
        if team_name:
            team_analysis["team_name"] = team_name
        if opponent_name:
            opponent_analysis["team_name"] = opponent_name
        
        # Step 3: Store data in database
        processing_tasks[task_id]["current_step"] = 2
        processing_tasks[task_id]["step_description"] = PROCESSING_STEPS[2]
        
        # Insert teams into database
        print("DEBUG - Inserting teams into database")
        team_id = insert_team(team_analysis)
        opponent_id = insert_team(opponent_analysis)
        
        print(f"DEBUG - Team ID: {team_id}, Opponent ID: {opponent_id}")
        
        if team_id and opponent_id:
            # Insert team stats
            print("DEBUG - Inserting team stats into database")
            team_stats_id = insert_team_stats(team_id, team_analysis)
            opponent_stats_id = insert_team_stats(opponent_id, opponent_analysis)
            print(f"DEBUG - Team Stats ID: {team_stats_id}, Opponent Stats ID: {opponent_stats_id}")
            
            # Insert players and their stats
            print("DEBUG - Inserting players and their stats into database")
            for player in team_analysis.get("players", []):
                player_id = insert_player(team_id, player)
                print(f"DEBUG - Team Player ID: {player_id}, Name: {player.get('name')}")
                if player_id:
                    # Insert raw stats first
                    raw_stats_id = insert_player_raw_stats(player_id, player)
                    print(f"DEBUG - Team Player Raw Stats ID: {raw_stats_id}")
                    # Then insert processed stats with reference to raw stats
                    player_stats_id = insert_player_stats(player_id, player, player_raw_stats_id=raw_stats_id)
                    print(f"DEBUG - Team Player Stats ID: {player_stats_id}")
            
            for player in opponent_analysis.get("players", []):
                player_id = insert_player(opponent_id, player)
                print(f"DEBUG - Opponent Player ID: {player_id}, Name: {player.get('name')}")
                if player_id:
                    # Insert raw stats first
                    raw_stats_id = insert_player_raw_stats(player_id, player)
                    print(f"DEBUG - Opponent Player Raw Stats ID: {raw_stats_id}")
                    # Then insert processed stats with reference to raw stats
                    player_stats_id = insert_player_stats(player_id, player, player_raw_stats_id=raw_stats_id)
                    print(f"DEBUG - Opponent Player Stats ID: {player_stats_id}")
            
            # Insert team analysis
            print("DEBUG - Inserting team analysis into database")
            team_analysis_id = insert_team_analysis(team_id, team_analysis)
            opponent_analysis_id = insert_team_analysis(opponent_id, opponent_analysis)
            print(f"DEBUG - Team Analysis ID: {team_analysis_id}, Opponent Analysis ID: {opponent_analysis_id}")
            
            # Insert game with user ID if available
            print("DEBUG - Inserting game into database")
            user_id = None
            if user and "sub" in user and user["sub"]:
                from database.connection import get_or_create_user
                user_id = get_or_create_user(user["sub"], user.get("email", ""), user.get("name", ""))
                print(f"DEBUG - User ID: {user_id}")
            
            game_id = insert_game(team_id, opponent_id, user_id)
            print(f"DEBUG - Game ID: {game_id}")
            
            # Step 4: Generate team analysis report
            processing_tasks[task_id]["current_step"] = 3
            processing_tasks[task_id]["step_description"] = PROCESSING_STEPS[3]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            team_analysis_path = generate_team_analysis_report(team_analysis, timestamp)
            
            # Step 5: Generate opponent analysis report
            processing_tasks[task_id]["current_step"] = 4
            processing_tasks[task_id]["step_description"] = PROCESSING_STEPS[4]
            opponent_analysis_path = generate_team_analysis_report(opponent_analysis, timestamp)
            
            # print("-"*40 + "\n" + f"DEBUG - Team Analysis Report Path: {team_analysis_path}")
            # print("-"*40 + "\n" + f"DEBUG - Opponent Analysis Report Path: {opponent_analysis_path}")
            
            # Insert reports
            if game_id:
                print("DEBUG - Inserting reports into database")
                team_report_id = insert_report(game_id, "team_analysis", team_analysis_path)
                opponent_report_id = insert_report(game_id, "opponent_analysis", opponent_analysis_path)
                print(f"DEBUG - Team Report ID: {team_report_id}, Opponent Report ID: {opponent_report_id}")
            
            # Step 6: Simulate game
            processing_tasks[task_id]["current_step"] = 5
            processing_tasks[task_id]["step_description"] = PROCESSING_STEPS[5]
            simulation_results = simulate_game(team_analysis, opponent_analysis, use_local=use_local_simulation)
            # print("-"*40 + "\n" + "DEBUG - Simulation Results:", simulation_results)
            
            # Check if simulation_results contains the required fields
            required_fields = ["win_probability", "projected_score", "sim_overall_summary", 
                              "sim_success_factors", "sim_key_matchups", "sim_win_loss_patterns"]
            
            missing_fields = [field for field in required_fields if field not in simulation_results]
            if missing_fields:
                print(f"WARNING - Missing required fields in simulation_results: {missing_fields}")
                # Add default values for missing fields
                for field in missing_fields:
                    simulation_results[field] = f"No data available for {field}"
                print("DEBUG - Added default values for missing fields")
            
            # Insert game simulation
            if game_id:
                print("DEBUG - Inserting game simulation into database")
                simulation_id = insert_game_simulation(game_id, simulation_results)
                print(f"DEBUG - Simulation ID: {simulation_id}")
                
                # If using local simulation, insert simulation details
                if use_local_simulation and "numSimulations" in simulation_results:
                    print("DEBUG - Inserting simulation details into database")
                    simulation_details_id = insert_simulation_details(
                        simulation_id, 
                        game_id, 
                        team_id,  # home team
                        opponent_id,  # away team
                        simulation_results
                    )
                    print(f"DEBUG - Simulation Details ID: {simulation_details_id}")
                
                # Insert player projections
                print("DEBUG - Inserting player projections into database")
                
                # Process team player projections
                for i in range(1, 6):  # Assuming up to 5 players
                    player_key = f"team_p{i}_name"
                    if player_key in simulation_results:
                        # Find player ID by name
                        player_name = simulation_results[f"team_p{i}_name"]
                        player_id = find_player_by_name(player_name, team_id)
                        
                        if player_id:
                            projection_data = {
                                "ppg": simulation_results.get(f"team_p{i}_ppg", 0),
                                "rpg": simulation_results.get(f"team_p{i}_rpg", 0),
                                "apg": simulation_results.get(f"team_p{i}_apg", 0),
                                "fg": simulation_results.get(f"team_p{i}_fg", "0%"),
                                "3p": simulation_results.get(f"team_p{i}_3p", "0%"),
                                "role": simulation_results.get(f"team_p{i}_role", "")
                            }
                            
                            projection_id = insert_player_projections(
                                simulation_id,
                                player_id,
                                team_id,
                                game_id,
                                projection_data,
                                True  # is_home_team
                            )
                            print(f"DEBUG - Team Player Projection ID: {projection_id}, Player: {player_name}")
                
                # Process opponent player projections
                for i in range(1, 6):  # Assuming up to 5 players
                    player_key = f"opp_p{i}_name"
                    if player_key in simulation_results:
                        # Find player ID by name
                        player_name = simulation_results[f"opp_p{i}_name"]
                        player_id = find_player_by_name(player_name, opponent_id)
                        
                        if player_id:
                            projection_data = {
                                "ppg": simulation_results.get(f"opp_p{i}_ppg", 0),
                                "rpg": simulation_results.get(f"opp_p{i}_rpg", 0),
                                "apg": simulation_results.get(f"opp_p{i}_apg", 0),
                                "fg": simulation_results.get(f"opp_p{i}_fg", "0%"),
                                "3p": simulation_results.get(f"opp_p{i}_3p", "0%"),
                                "role": simulation_results.get(f"opp_p{i}_role", "")
                            }
                            
                            projection_id = insert_player_projections(
                                simulation_id,
                                player_id,
                                opponent_id,
                                game_id,
                                projection_data,
                                False  # is_home_team
                            )
                            print(f"DEBUG - Opponent Player Projection ID: {projection_id}, Player: {player_name}")
        
        # Step 7: Generate final report
        processing_tasks[task_id]["current_step"] = 6
        processing_tasks[task_id]["step_description"] = PROCESSING_STEPS[6]
        
        # Prepare analysis results in the format expected by report_gen
        analysis_results = {
            "team_name": team_analysis.get("team_name", "Team"),
            "opponent_name": opponent_analysis.get("team_name", "Opponent"),
            "team_record": team_analysis.get("team_record", ""),
            "opponent_record": opponent_analysis.get("team_record", ""),
            "matchup_overview": f"Game between {team_analysis.get('team_name', 'Team')} and {opponent_analysis.get('team_name', 'Opponent')}.",
            "team_strengths_summary": "\n".join([f"- {strength}" for strength in team_analysis.get("team_strengths", [])]),
            "team_weaknesses_summary": "\n".join([f"- {weakness}" for weakness in team_analysis.get("team_weaknesses", [])]),
            "opponent_strengths_summary": "\n".join([f"- {strength}" for strength in opponent_analysis.get("team_strengths", [])]),
            "opponent_weaknesses_summary": "\n".join([f"- {weakness}" for weakness in opponent_analysis.get("team_weaknesses", [])])
        }
        
        # Add game factors, offensive keys, defensive keys
        if "game_factors" in team_analysis:
            analysis_results["game_factors"] = "\n".join([f"- {factor}" for factor in team_analysis.get("game_factors", [])])
        
        if "offensive_keys" in team_analysis:
            analysis_results["offensive_keys"] = "\n".join([f"- {key}" for key in team_analysis.get("offensive_keys", [])])
        
        if "defensive_keys" in team_analysis:
            analysis_results["defensive_keys"] = "\n".join([f"- {key}" for key in team_analysis.get("defensive_keys", [])])
        
        if "rotation_plan" in team_analysis:
            analysis_results["rotation_plan"] = team_analysis.get("rotation_plan", "")
        
        if "situational_adjustments" in team_analysis:
            analysis_results["situational_adjustments"] = "\n".join([f"- {adj}" for adj in team_analysis.get("situational_adjustments", [])])
        
        if "game_keys" in team_analysis:
            analysis_results["game_keys"] = "\n".join([f"- {key}" for key in team_analysis.get("game_keys", [])])
        
        # Add player information
        team_players = team_analysis.get("players", [])
        opponent_players = opponent_analysis.get("players", [])
        
        # Add team players
        for i, player in enumerate(team_players[:5], 1):
            analysis_results[f"player_{i}_name"] = f"{player.get('name', '')} #{player.get('number', '')}"
            analysis_results[f"player_{i}_stats"] = f"{player.get('stats', {}).get('PPG', 0)} PPG, {player.get('stats', {}).get('FG%', '0%')} FG, {player.get('stats', {}).get('3FG%', '0%')} 3PT"
            analysis_results[f"player_{i}_strengths"] = "\n".join([f"- {strength}" for strength in player.get("strengths", [])])
            analysis_results[f"player_{i}_weaknesses"] = "\n".join([f"- {weakness}" for weakness in player.get("weaknesses", [])])
        
        # Add opponent players
        for i, player in enumerate(opponent_players[:5], 1):
            analysis_results[f"opponent_player_{i}_name"] = f"{player.get('name', '')} #{player.get('number', '')}"
            analysis_results[f"opponent_player_{i}_stats"] = f"{player.get('stats', {}).get('PPG', 0)} PPG, {player.get('stats', {}).get('FG%', '0%')} FG, {player.get('stats', {}).get('3FG%', '0%')} 3PT"
            analysis_results[f"opponent_player_{i}_shooting"] = f"{player.get('stats', {}).get('FG%', '0%')} FG, {player.get('stats', {}).get('3FG%', '0%')} 3PT, {player.get('stats', {}).get('FT%', '0%')} FT"
            analysis_results[f"opponent_player_{i}_strengths"] = "\n".join([f"- {strength}" for strength in player.get("strengths", [])])
            analysis_results[f"opponent_player_{i}_weaknesses"] = "\n".join([f"- {weakness}" for weakness in player.get("weaknesses", [])])
            analysis_results[f"opponent_player_{i}_insight"] = f"Key player for {opponent_analysis.get('team_name', 'Opponent')}"
        
        # Add stat comparison
        stat_labels = [
            "Points Per Game", "FG %", "3PT %", "FT %", 
            "Steals", "Blocks", "Rebounds", 
            "Defensive Rebounds", "Offensive Rebounds", 
            "Assists", "Assist-to-Turnover Ratio"
        ]
        
        team_stats = team_analysis.get("team_stats", {})
        opponent_stats = opponent_analysis.get("team_stats", {})
        
        for i, label in enumerate(stat_labels, 1):
            analysis_results[f"stat_label_{i}"] = label
            
            if label == "Points Per Game":
                analysis_results[f"team_stat_{i}"] = str(team_stats.get("PPG", 0))
                analysis_results[f"opponent_stat_{i}"] = str(opponent_stats.get("PPG", 0))
            elif label == "FG %":
                analysis_results[f"team_stat_{i}"] = team_stats.get("FG%", "0%")
                analysis_results[f"opponent_stat_{i}"] = opponent_stats.get("FG%", "0%")
            elif label == "3PT %":
                analysis_results[f"team_stat_{i}"] = team_stats.get("3FG%", "0%")
                analysis_results[f"opponent_stat_{i}"] = opponent_stats.get("3FG%", "0%")
            elif label == "FT %":
                analysis_results[f"team_stat_{i}"] = team_stats.get("FT%", "0%")
                analysis_results[f"opponent_stat_{i}"] = opponent_stats.get("FT%", "0%")
            elif label == "Steals":
                analysis_results[f"team_stat_{i}"] = str(team_stats.get("STL", 0))
                analysis_results[f"opponent_stat_{i}"] = str(opponent_stats.get("STL", 0))
            elif label == "Blocks":
                analysis_results[f"team_stat_{i}"] = str(team_stats.get("BLK", 0))
                analysis_results[f"opponent_stat_{i}"] = str(opponent_stats.get("BLK", 0))
            elif label == "Rebounds":
                analysis_results[f"team_stat_{i}"] = str(team_stats.get("REB", 0))
                analysis_results[f"opponent_stat_{i}"] = str(opponent_stats.get("REB", 0))
            elif label == "Defensive Rebounds":
                analysis_results[f"team_stat_{i}"] = str(team_stats.get("DREB", 0))
                analysis_results[f"opponent_stat_{i}"] = str(opponent_stats.get("DREB", 0))
            elif label == "Offensive Rebounds":
                analysis_results[f"team_stat_{i}"] = str(team_stats.get("OREB", 0))
                analysis_results[f"opponent_stat_{i}"] = str(opponent_stats.get("OREB", 0))
            elif label == "Assists":
                analysis_results[f"team_stat_{i}"] = str(team_stats.get("AST", 0))
                analysis_results[f"opponent_stat_{i}"] = str(opponent_stats.get("AST", 0))
            elif label == "Assist-to-Turnover Ratio":
                analysis_results[f"team_stat_{i}"] = str(team_stats.get("A/TO", 0))
                analysis_results[f"opponent_stat_{i}"] = str(opponent_stats.get("A/TO", 0))
        
        # Generate combined report
        report_path = generate_report(analysis_results, simulation_results)
        print("Generated final report")
        # print("-"*40 + "\n" + "DEBUG - Combined Report Path:", report_path)
        
        # Insert combined report
        if game_id:
            insert_report(game_id, "game_analysis", report_path)
        
        # Update task status
        processing_tasks[task_id]["status"] = "completed"
        processing_tasks[task_id]["report_path"] = report_path
        processing_tasks[task_id]["team_analysis_path"] = team_analysis_path
        processing_tasks[task_id]["opponent_analysis_path"] = opponent_analysis_path
        processing_tasks[task_id]["game_id"] = game_id if game_id else None
        
        # Get the report ID from the database
        if game_id:
            report_query = """
            SELECT id FROM reports 
            WHERE game_id = %s AND report_type = 'game_analysis'
            ORDER BY created_at DESC LIMIT 1
            """
            report_result = execute_query(report_query, (game_id,))
            if report_result:
                processing_tasks[task_id]["report_id"] = report_result[0]["id"]
        
    except Exception as e:
        # Update task status with error
        processing_tasks[task_id]["status"] = "failed"
        processing_tasks[task_id]["error"] = str(e)
        print("-" * 40)
        print(f"ERROR: {str(e)}")
