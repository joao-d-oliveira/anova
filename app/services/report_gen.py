import os
import re
from typing import Dict, Any, List, Optional
from datetime import datetime
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.table import WD_ALIGN_VERTICAL

def generate_report(analysis_results: Dict[str, Any], simulation_results: Dict[str, Any]) -> str:
    """
    Generate a DOCX report based on analysis and simulation results
    
    Args:
        analysis_results: Dictionary containing analysis results
        simulation_results: Dictionary containing simulation results
        
    Returns:
        Path to the generated report
    """
    # Create a new Document
    doc = Document()
    
    # Set document properties
    doc.core_properties.title = f"{analysis_results.get('team_name', 'Team')} VS {analysis_results.get('opponent_name', 'Opponent')} - Anova Analysis"
    doc.core_properties.author = "Anova Basketball Analytics"
    
    # Add title
    add_title(doc, analysis_results)
    
    # Add matchup overview section
    add_matchup_overview(doc, analysis_results, simulation_results)
    
    # Add team comparison section
    add_team_comparison(doc, analysis_results)
    
    # Add game plan section
    add_game_plan(doc, analysis_results)
    
    # Add team analysis section
    add_team_analysis(doc, analysis_results)
    
    # Add opponent analysis section
    add_opponent_analysis(doc, analysis_results)
    
    # Add simulation results section
    add_simulation_results(doc, simulation_results)
    
    # Create output directory if it doesn't exist
    os.makedirs("app/temp/reports", exist_ok=True)
    
    # Generate filename
    team_name = analysis_results.get("team_name", "Team")
    opponent_name = analysis_results.get("opponent_name", "Opponent")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{team_name} VS {opponent_name} - Anova Analysis - {timestamp}.docx"
    filepath = os.path.join("app/temp/reports", filename)
    
    # Save the document
    doc.save(filepath)
    
    return filepath

def add_title(doc: Document, analysis_results: Dict[str, Any]) -> None:
    """
    Add title section to the document
    
    Args:
        doc: Document object
        analysis_results: Dictionary containing analysis results
    """
    team_name = analysis_results.get("team_name", "Team")
    opponent_name = analysis_results.get("opponent_name", "Opponent")
    
    # Add title
    title = doc.add_heading(f"{team_name} VS {opponent_name}", level=0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Add subtitle
    subtitle = doc.add_paragraph("Anova Basketball Analytics")
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    subtitle.style = "Subtitle"
    
    # Add date
    date_paragraph = doc.add_paragraph(datetime.now().strftime("%B %d, %Y"))
    date_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Add horizontal line
    doc.add_paragraph("_" * 50)
    
    # Add some space
    doc.add_paragraph()

def add_matchup_overview(doc: Document, analysis_results: Dict[str, Any], simulation_results: Dict[str, Any]) -> None:
    """
    Add matchup overview section to the document
    
    Args:
        doc: Document object
        analysis_results: Dictionary containing analysis results
        simulation_results: Dictionary containing simulation results
    """
    # Add section heading
    doc.add_heading("MATCHUP OVERVIEW", level=1)
    
    # Add matchup overview
    overview = doc.add_paragraph()
    overview.add_run(analysis_results.get("matchup_overview", "")).bold = True
    
    # Add win probability and projected score
    if "win_probability" in simulation_results:
        doc.add_paragraph(simulation_results.get("win_probability", ""))
    if "projected_score" in simulation_results:
        projected_score = doc.add_paragraph()
        projected_score.add_run("Projected Score: ").bold = True
        projected_score.add_run(simulation_results.get("projected_score", ""))
    
    # Add key matchup
    if "key_matchup" in analysis_results:
        key_matchup = doc.add_paragraph()
        key_matchup.add_run("Key Matchup: ").bold = True
        key_matchup.add_run(analysis_results.get("key_matchup", ""))
    
    # Add horizontal line
    doc.add_paragraph("_" * 50)

def add_team_comparison(doc: Document, analysis_results: Dict[str, Any]) -> None:
    """
    Add team comparison section to the document
    
    Args:
        doc: Document object
        analysis_results: Dictionary containing analysis results
    """
    # Add section heading
    doc.add_heading("TEAM COMPARISON", level=1)
    
    # Create a table for team comparison
    table = doc.add_table(rows=1, cols=3)
    table.style = "Table Grid"
    
    # Add header row
    header_cells = table.rows[0].cells
    header_cells[0].text = "STATISTIC"
    header_cells[1].text = analysis_results.get("team_name", "Team")
    header_cells[2].text = analysis_results.get("opponent_name", "Opponent")
    
    # Format header row
    for cell in header_cells:
        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        for run in cell.paragraphs[0].runs:
            run.bold = True
    
    # Add stats rows
    for i in range(1, 12):
        label = analysis_results.get(f"stat_label_{i}", "")
        team_stat = analysis_results.get(f"team_stat_{i}", "")
        opponent_stat = analysis_results.get(f"opponent_stat_{i}", "")
        
        if label:
            row_cells = table.add_row().cells
            row_cells[0].text = label
            row_cells[1].text = team_stat
            row_cells[2].text = opponent_stat
            
            # Center align the cells
            for cell in row_cells:
                cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Add some space
    doc.add_paragraph()
    
    # Add team strengths and weaknesses
    doc.add_heading(f"{analysis_results.get('team_name', 'Team')} Strengths", level=2)
    add_bullet_list(doc, analysis_results.get("team_strengths_summary", ""))
    
    doc.add_heading(f"{analysis_results.get('team_name', 'Team')} Weaknesses", level=2)
    add_bullet_list(doc, analysis_results.get("team_weaknesses_summary", ""))
    
    doc.add_heading(f"{analysis_results.get('opponent_name', 'Opponent')} Strengths", level=2)
    add_bullet_list(doc, analysis_results.get("opponent_strengths_summary", ""))
    
    doc.add_heading(f"{analysis_results.get('opponent_name', 'Opponent')} Weaknesses", level=2)
    add_bullet_list(doc, analysis_results.get("opponent_weaknesses_summary", ""))
    
    # Add horizontal line
    doc.add_paragraph("_" * 50)

def add_game_plan(doc: Document, analysis_results: Dict[str, Any]) -> None:
    """
    Add game plan section to the document
    
    Args:
        doc: Document object
        analysis_results: Dictionary containing analysis results
    """
    # Add section heading
    doc.add_heading("GAME PLAN", level=1)
    
    # Add game factors
    doc.add_heading("Game Factors", level=2)
    add_bullet_list(doc, analysis_results.get("game_factors", ""))
    
    # Add offensive keys
    doc.add_heading("Offensive Keys", level=2)
    add_bullet_list(doc, analysis_results.get("offensive_keys", ""))
    
    # Add defensive keys
    doc.add_heading("Defensive Keys", level=2)
    add_bullet_list(doc, analysis_results.get("defensive_keys", ""))
    
    # Add game plan
    doc.add_heading("Detailed Game Plan", level=2)
    add_formatted_text(doc, analysis_results.get("game_plan", ""))
    
    # Add situational adjustments
    doc.add_heading("Situational Adjustments", level=2)
    add_bullet_list(doc, analysis_results.get("situational_adjustments", ""))
    
    # Add rotation plan
    doc.add_heading("Rotation Plan", level=2)
    add_formatted_text(doc, analysis_results.get("rotation_plan", ""))
    
    # Add game keys
    doc.add_heading("Game Keys", level=2)
    add_bullet_list(doc, analysis_results.get("game_keys", ""))
    
    # Add horizontal line
    doc.add_paragraph("_" * 50)

def add_team_analysis(doc: Document, analysis_results: Dict[str, Any]) -> None:
    """
    Add team analysis section to the document
    
    Args:
        doc: Document object
        analysis_results: Dictionary containing analysis results
    """
    team_name = analysis_results.get("team_name", "Team")
    
    # Add section heading
    doc.add_heading(f"{team_name} PLAYER ANALYSIS", level=1)
    
    # Add player analysis overview
    overview = doc.add_paragraph()
    overview.add_run("Overview: ").bold = True
    overview.add_run(analysis_results.get("player_analysis_overview", ""))
    
    # Add player analysis for each player
    for i in range(1, 6):
        player_name = analysis_results.get(f"player_{i}_name", "")
        player_stats = analysis_results.get(f"player_{i}_stats", "")
        player_strengths = analysis_results.get(f"player_{i}_strengths", "")
        player_weaknesses = analysis_results.get(f"player_{i}_weaknesses", "")
        
        if player_name:
            # Add player heading
            doc.add_heading(player_name, level=2)
            
            # Add player stats
            stats = doc.add_paragraph()
            stats.add_run("Stats: ").bold = True
            stats.add_run(player_stats)
            
            # Add player strengths
            doc.add_heading("Strengths", level=3)
            add_bullet_list(doc, player_strengths)
            
            # Add player weaknesses
            doc.add_heading("Weaknesses", level=3)
            add_bullet_list(doc, player_weaknesses)
    
    # Add horizontal line
    doc.add_paragraph("_" * 50)

def add_opponent_analysis(doc: Document, analysis_results: Dict[str, Any]) -> None:
    """
    Add opponent analysis section to the document
    
    Args:
        doc: Document object
        analysis_results: Dictionary containing analysis results
    """
    opponent_name = analysis_results.get("opponent_name", "Opponent")
    
    # Add section heading
    doc.add_heading(f"{opponent_name} PLAYER ANALYSIS", level=1)
    
    # Add opponent scouting
    if "opponent_scouting" in analysis_results:
        scouting = doc.add_paragraph()
        scouting.add_run("Scouting Report: ").bold = True
        scouting.add_run(analysis_results.get("opponent_scouting", ""))
    
    # Add player analysis for each opponent player
    for i in range(1, 6):
        player_name = analysis_results.get(f"opponent_player_{i}_name", "")
        player_stats = analysis_results.get(f"opponent_player_{i}_stats", "")
        player_shooting = analysis_results.get(f"opponent_player_{i}_shooting", "")
        player_strengths = analysis_results.get(f"opponent_player_{i}_strengths", "")
        player_weaknesses = analysis_results.get(f"opponent_player_{i}_weaknesses", "")
        player_insight = analysis_results.get(f"opponent_player_{i}_insight", "")
        
        if player_name:
            # Add player heading
            doc.add_heading(player_name, level=2)
            
            # Add player stats
            stats = doc.add_paragraph()
            stats.add_run("Stats: ").bold = True
            stats.add_run(player_stats)
            
            # Add player shooting
            if player_shooting:
                shooting = doc.add_paragraph()
                shooting.add_run("Shooting: ").bold = True
                shooting.add_run(player_shooting)
            
            # Add player strengths
            doc.add_heading("Strengths", level=3)
            add_bullet_list(doc, player_strengths)
            
            # Add player weaknesses
            doc.add_heading("Weaknesses", level=3)
            add_bullet_list(doc, player_weaknesses)
            
            # Add player insight
            if player_insight:
                insight = doc.add_paragraph()
                insight.add_run("Insight: ").bold = True
                insight.add_run(player_insight)
    
    # Add horizontal line
    doc.add_paragraph("_" * 50)

def add_simulation_results(doc: Document, simulation_results: Dict[str, Any]) -> None:
    """
    Add simulation results section to the document
    
    Args:
        doc: Document object
        simulation_results: Dictionary containing simulation results
    """
    # Add section heading
    doc.add_heading("SIMULATION RESULTS", level=1)
    
    # Add simulation overview
    overview = doc.add_paragraph()
    overview.add_run("Overview: ").bold = True
    overview.add_run(simulation_results.get("sim_overall_summary", ""))
    
    # Add success factors
    doc.add_heading("Success Factors", level=2)
    add_bullet_list(doc, simulation_results.get("sim_success_factors", ""))
    
    # Add key matchups
    doc.add_heading("Key Matchups", level=2)
    add_bullet_list(doc, simulation_results.get("sim_key_matchups", ""))
    
    # Add win/loss patterns
    doc.add_heading("Win/Loss Patterns", level=2)
    add_bullet_list(doc, simulation_results.get("sim_win_loss_patterns", ""))
    
    # Add player simulation stats
    doc.add_heading("Player Simulation Stats", level=2)
    
    # Create a table for team player stats
    team_table = doc.add_table(rows=1, cols=7)
    team_table.style = "Table Grid"
    
    # Add header row for team players
    header_cells = team_table.rows[0].cells
    header_cells[0].text = "Player"
    header_cells[1].text = "PPG"
    header_cells[2].text = "RPG"
    header_cells[3].text = "APG"
    header_cells[4].text = "FG%"
    header_cells[5].text = "3P%"
    header_cells[6].text = "Role"
    
    # Format header row
    for cell in header_cells:
        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        for run in cell.paragraphs[0].runs:
            run.bold = True
    
    # Add team player rows
    for i in range(1, 6):
        name = simulation_results.get(f"team_p{i}_name", "")
        ppg = simulation_results.get(f"team_p{i}_ppg", "")
        rpg = simulation_results.get(f"team_p{i}_rpg", "")
        apg = simulation_results.get(f"team_p{i}_apg", "")
        fg = simulation_results.get(f"team_p{i}_fg", "")
        three_p = simulation_results.get(f"team_p{i}_3p", "")
        role = simulation_results.get(f"team_p{i}_role", "")
        
        if name:
            row_cells = team_table.add_row().cells
            row_cells[0].text = name
            row_cells[1].text = ppg
            row_cells[2].text = rpg
            row_cells[3].text = apg
            row_cells[4].text = fg
            row_cells[5].text = three_p
            row_cells[6].text = role
            
            # Center align the cells
            for cell in row_cells:
                cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Add some space
    doc.add_paragraph()
    
    # Create a table for opponent player stats
    opp_table = doc.add_table(rows=1, cols=7)
    opp_table.style = "Table Grid"
    
    # Add header row for opponent players
    header_cells = opp_table.rows[0].cells
    header_cells[0].text = "Player"
    header_cells[1].text = "PPG"
    header_cells[2].text = "RPG"
    header_cells[3].text = "APG"
    header_cells[4].text = "FG%"
    header_cells[5].text = "3P%"
    header_cells[6].text = "Role"
    
    # Format header row
    for cell in header_cells:
        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        for run in cell.paragraphs[0].runs:
            run.bold = True
    
    # Add opponent player rows
    for i in range(1, 6):
        name = simulation_results.get(f"opp_p{i}_name", "")
        ppg = simulation_results.get(f"opp_p{i}_ppg", "")
        rpg = simulation_results.get(f"opp_p{i}_rpg", "")
        apg = simulation_results.get(f"opp_p{i}_apg", "")
        fg = simulation_results.get(f"opp_p{i}_fg", "")
        three_p = simulation_results.get(f"opp_p{i}_3p", "")
        role = simulation_results.get(f"opp_p{i}_role", "")
        
        if name:
            row_cells = opp_table.add_row().cells
            row_cells[0].text = name
            row_cells[1].text = ppg
            row_cells[2].text = rpg
            row_cells[3].text = apg
            row_cells[4].text = fg
            row_cells[5].text = three_p
            row_cells[6].text = role
            
            # Center align the cells
            for cell in row_cells:
                cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

def add_bullet_list(doc: Document, text: str) -> None:
    """
    Add a bullet list to the document
    
    Args:
        doc: Document object
        text: Text containing bullet points (each line starting with "- ")
    """
    if not text:
        return
    
    # Split text into lines
    lines = text.split("\n")
    
    # Add each line as a bullet point
    for line in lines:
        # Remove leading "- " if present
        line = line.strip()
        if line.startswith("- "):
            line = line[2:]
        
        # Add bullet point
        if line:
            p = doc.add_paragraph(line, style="List Bullet")

def add_formatted_text(doc: Document, text: str) -> None:
    """
    Add formatted text to the document
    
    Args:
        doc: Document object
        text: Text to add
    """
    if not text:
        return
    
    # Split text into paragraphs
    paragraphs = text.split("\n\n")
    
    # Add each paragraph
    for paragraph_text in paragraphs:
        if paragraph_text.strip():
            p = doc.add_paragraph()
            
            # Check if it's a heading (all caps)
            if paragraph_text.strip().isupper():
                p.add_run(paragraph_text.strip()).bold = True
            else:
                # Split into lines
                lines = paragraph_text.split("\n")
                
                # Add each line
                for i, line in enumerate(lines):
                    # Check if it's a bullet point
                    if line.strip().startswith("- "):
                        # If it's the first line, add a new paragraph
                        if i > 0:
                            p = doc.add_paragraph()
                        
                        # Add bullet point
                        p.style = "List Bullet"
                        p.text = line.strip()[2:]  # Remove "- "
                    else:
                        # If it's not the first line, add a line break
                        if i > 0:
                            p.add_run("\n" + line.strip())
                        else:
                            p.add_run(line.strip())
