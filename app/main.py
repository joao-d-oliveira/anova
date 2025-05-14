import os
import json
from datetime import datetime
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path

from app.database.init_db import init_db
from app.middleware.auth_middleware import AuthMiddleware
from app.middleware.path_middleware import PathMiddleware

# Create FastAPI app
app = FastAPI(
    title="Basketball PDF Analysis Pipeline",
    description="A web application for analyzing basketball PDFs and generating game predictions",
    version="1.0.0"
)

# Add middlewares
app.add_middleware(AuthMiddleware)
app.add_middleware(PathMiddleware)

# Initialize database
@app.on_event("startup")
async def startup_event():
    """
    Initialize the database when the application starts
    """
    init_db()

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Set up Jinja2 templates with custom context
templates = Jinja2Templates(directory="app/templates")

# Add root_path to all templates
@app.middleware("http")
async def add_root_path_to_templates(request: Request, call_next):
    # Get root_path from environment or use empty string
    root_path = os.getenv("ROOT_PATH", "")
    request.state.root_path = root_path
    response = await call_next(request)
    return response

# Create temp directories if they don't exist
os.makedirs("app/temp/uploads", exist_ok=True)
os.makedirs("app/temp/reports", exist_ok=True)

# Import routers after app is created to avoid circular imports
from app.routers import upload, auth

# Include routers
app.include_router(upload.router)
app.include_router(auth.router)

def get_version_date():
    """
    Read the VERSION_DEPLOYMENT.JSON file and return the last_updated date
    """
    try:
        with open("app/VERSION_DEPLOYMENT.JSON", "r") as f:
            version_data = json.load(f)
            return version_data.get("last_updated", "Unknown")
    except (FileNotFoundError, json.JSONDecodeError):
        return "Unknown"

@app.get("/", response_class=HTMLResponse)
async def landing(request: Request):
    """
    Root endpoint that renders the new landing page
    """
    version_date = get_version_date()
    return templates.TemplateResponse("landing.html", {"request": request, "version_date": version_date})

@app.get("/app", response_class=HTMLResponse)
async def app_page(request: Request):
    """
    App endpoint that renders the main application page with the file upload form
    
    This route is protected by the AuthMiddleware and requires authentication.
    If Cognito is unavailable, users will be redirected to the login page with an error.
    """
    # Check if user is authenticated (this should be handled by AuthMiddleware,
    # but we add an extra check here for clarity)
    user = getattr(request.state, "user", None)
    if not user:
        return RedirectResponse(url="/auth/login")
        
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/analyses", response_class=HTMLResponse)
async def analyses_page(request: Request):
    """
    Redirect to the analyses API endpoint
    """
    return RedirectResponse(url="/api/analyses")

@app.get("/report/{report_id}", response_class=HTMLResponse)
async def report_view(request: Request, report_id: str):
    """
    View a specific report
    """
    from app.database.connection import execute_query, get_or_create_user
    from app.middleware.auth_middleware import get_current_user
    
    # Get current user
    user = get_current_user(request)
    user_id = None
    
    if user and "sub" in user and user["sub"]:
        user_id = get_or_create_user(user["sub"], user.get("email", ""), user.get("name", ""))
    
    # Get report details with user filtering
    if user_id:
        query = """
        SELECT r.id, r.game_id, r.report_type, r.file_path, r.created_at,
               g.id as game_id, 
               ht.name as home_team, 
               at.name as away_team,
               gs.win_probability, 
               gs.projected_score,
               gs.sim_overall_summary,
               gs.sim_success_factors,
               gs.sim_key_matchups,
               gs.sim_win_loss_patterns
        FROM reports r
        JOIN games g ON r.game_id = g.id
        JOIN teams ht ON g.home_team_id = ht.id
        JOIN teams at ON g.away_team_id = at.id
        LEFT JOIN game_simulations gs ON g.id = gs.game_id
        WHERE r.id = %s AND g.user_id = %s
        """
        report = execute_query(query, (report_id, user_id))
    else:
        # If no user_id, fall back to the original query (for development/testing)
        query = """
        SELECT r.id, r.game_id, r.report_type, r.file_path, r.created_at,
               g.id as game_id, 
               ht.name as home_team, 
               at.name as away_team,
               gs.win_probability, 
               gs.projected_score,
               gs.sim_overall_summary,
               gs.sim_success_factors,
               gs.sim_key_matchups,
               gs.sim_win_loss_patterns
        FROM reports r
        JOIN games g ON r.game_id = g.id
        JOIN teams ht ON g.home_team_id = ht.id
        JOIN teams at ON g.away_team_id = at.id
        LEFT JOIN game_simulations gs ON g.id = gs.game_id
        WHERE r.id = %s
        """
        report = execute_query(query, (report_id,))
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found or you don't have access to it")
    
    report = report[0]
    
    # Get team analysis
    team_analysis_query = """
    SELECT ta.* 
    FROM team_analysis ta
    JOIN games g ON ta.team_id = g.home_team_id
    JOIN reports r ON g.id = r.game_id
    WHERE r.id = %s
    """
    
    team_analysis = execute_query(team_analysis_query, (report_id,))
    
    # Get opponent analysis
    opponent_analysis_query = """
    SELECT ta.* 
    FROM team_analysis ta
    JOIN games g ON ta.team_id = g.away_team_id
    JOIN reports r ON g.id = r.game_id
    WHERE r.id = %s
    """
    
    opponent_analysis = execute_query(opponent_analysis_query, (report_id,))
    
    # Prepare template context
    context = {
        "request": request,
        "report_id": report_id,
        "home_team": report["home_team"],
        "away_team": report["away_team"],
        "created_at": report["created_at"],
        "win_probability": report["win_probability"],
        "projected_score": report["projected_score"],
        "sim_overall_summary": report["sim_overall_summary"],
        "sim_success_factors": report["sim_success_factors"].split("\n") if report["sim_success_factors"] else [],
        "sim_key_matchups": report["sim_key_matchups"].split("\n") if report["sim_key_matchups"] else [],
        "sim_win_loss_patterns": report["sim_win_loss_patterns"].split("\n") if report["sim_win_loss_patterns"] else [],
        "team_analysis": team_analysis[0] if team_analysis else {},
        "opponent_analysis": opponent_analysis[0] if opponent_analysis else {},
        # "home_team_key_stats": ["Strong 3-point shooting", "Excellent free throw shooting", "Good ball movement"],
        # "away_team_key_stats": ["Strong 3-point shooting", "Good free throw percentage", "Efficient shooting"],
        "critical_advantage": "Free throw shooting - Scarsdale shoots 77.4% from the line compared to Arlington's 59.2%, potentially decisive in a close game." if not team_analysis[0]["strengths"] else ";".join(team_analysis[0]["strengths"]),
        # "keys_to_victory": ["Control the Defensive Glass", "Protect the Ball", "Win the Perimeter Battle", "Capitalize at the Line", "Start Fast, Finish Strong"]
        "situational_adjustments": [
            "Increase three-point attempts and pace",
            "Focus on high-percentage shots and clock management",
            "Run actions for Sussberg (50% 3PT) or Hoey (50% 3PT)"
        ] if not team_analysis[0]['situational_adjustments'] else team_analysis[0]['situational_adjustments'],
        "offensive_player_keys": ["Utilize Jake Sussberg's three-point shooting", "Feature Daniel Hoey", "Get Brandon Gibbons involved early", "Create mismatches with Finn Miller", "Capitalize on excellent FT shooting" ]
        if not team_analysis[0]["key_players"] else team_analysis[0]["key_players"],
        "defensive_player_keys": [
            "Limit Gavin Flynn's three-point opportunities",
            "Contain Jacob Jerome's scoring",
            "Pressure Jensy Adames into turnovers",
            "Box out against Jerome Richards",
            "Force contested shots against Jayden Tuttle"
        ] if not opponent_analysis[0]["key_players"] else opponent_analysis[0]["key_players"],

        "key_matchup": "Jake Sussberg (PG) vs Gavin Flynn (PG) will be the deciding matchup. Both are their team's top three-point shooters with Sussberg shooting 37.2% on 43 attempts and Flynn shooting 52.9% on 17 attempts. Sussberg averages 24.4 PPG compared to Flynn's 8.8 PPG, but Flynn has a better overall FG% (52.9% vs 34.9%)." if not report["sim_key_matchups"] else report["sim_key_matchups"],
        "defensive_priorities": "Hold Arlington under 55 total points and limit their lead facilitator, Jacob Jerome, to fewer than 8 assists to disrupt their offensive rhythm." if not "; ".join(team_analysis[0]['defensive_keys']) else "; ".join(team_analysis[0]['defensive_keys']),
        # "offensive_plays": [
        #     {"name": "Horns Flare", "purpose": "Create three-point opportunity for Jake Sussberg (37.2% 3PT)", "execution": "Start in horns formation. Hoey initiates from top, big sets flare screen for Sussberg to create separation for perimeter shot", "counter_options": "If defender goes under screen, Sussberg can attack inside-out. If overplayed, backdoor cut available"},
        #     {"name": "High Pick and Roll", "purpose": "Utilize Daniel Hoey's playmaking (17 AST) and decision-making", "execution": "High screen from forward. Hoey attacks downhill with options to score or distribute to shooters", "counter_options": "If defense traps, slip the screen and roll to basket. If help rotates, kick to open shooter"},
        #     {"name": "Box Set Isolation", "purpose": "Create scoring opportunity for Brandon Gibbons (44.1% FG)", "execution": "Box formation with Gibbons at elbow, clear side for isolation against defender", "counter_options": "If help defense collapses, kick to Sussberg or Hoey for three-point attempt"}
        # ],
        # "defensive_plays": [
        #     {"name": "Deny Flynn", "purpose": "Limit Gavin Flynn's three-point opportunities (52.9% 3PT)", "execution": "Face-guard Flynn on perimeter, go over all screens, no help off him", "counter_options": "If Flynn drives, late help from weak side while maintaining perimeter coverage"},
        #     {"name": "Ice Side Pick and Roll", "purpose": "Force Jacob Jerome (35.8% FG) into inefficient shots", "execution": "Force side pick and rolls toward baseline, big contains until guard recovers", "counter_options": "If Jerome rejects screen, switch coverage to standard pick and roll defense"},
        #     {"name": "Box Out Richards", "purpose": "Neutralize Jerome Richards offensive rebounding (7 OREB)", "execution": "Assign Miller and Hoey to specifically box out Richards on every shot attempt", "counter_options": "If Richards moves to perimeter, switch box out assignments to nearest defender"}
        # ],
        # "special_plays": [
        #     {"name": "Hammer Action", "purpose": "Create open corner three for Sussberg in late-game situations", "execution": "Start in horns formation. Hoey initiates from top, big sets flare screen for Sussberg to create separation for perimeter shot", "counter_options": "Drive and kick with weak side hammer screen to free Sussberg in corner"},
        #     {"name": "1-4 High Clear", "purpose": "Isolate Hoey (48.5% FG) against weaker defender", "execution": "1-4 high set with clear out for Hoey to attack from wing", "counter_options": "If help comes, kick to open shooter. If denied entry, flow into secondary motion offense"}
        # ],
        # "inbound_plays": [
        #     {"name": "Box Screen", "purpose": "Create scoring opportunity from baseline out of bounds", "execution": "Box formation with cross screens to free Sussberg for catch and shoot", "counter_options": "If Sussberg is denied, secondary option to Hoey cutting to basket"}
        # ],
        # "timeout_plays": [
        #     {"name": "Elevator Doors", "purpose": "Free shooter after timeout for critical three-point attempt", "execution": "Double screen with screeners closing gap after shooter passes through", "counter_options": "If defense anticipates, screeners slip to basket for interior pass"}
        # ],
        # "sim_offensive_keys": [
        #     "Jake Sussberg's three-point shooting battle between Scarsdale's volume shooter (37.2% on 43 attempts) and Arlington's efficient shooter (52.9% on 17 attempts)",
        #     "Daniel Hoey vs. Jacob Jerome: Playmaking duel between Hoey (17 AST, 15 PPG) and Jerome (19 AST, 10.8 PPG)",
        #     "Brandon Gibbons vs. Jensy Adames: Secondary scoring matchup between Gibbons (7.4 PPG, 44.1% FG) and Adames (9.2 PPG, 41.9% FG)"
        # ],
        # "sim_defensive_keys": [
        #     "Games decided by 5 points or fewer occurred in 42% of simulations, highlighting the razor-thin margin between teams",
        #     "Scarsdale wins contests strongly with games where they attempt 20+ free throws (72.4% FT% vs Arlington's 59.2%)",
        #     "Arlington wins typically feature strong first quarter starts (+3.5 points) that Scarsdale couldn't overcome"
        # ],
        # "home_team_sim_players": [
        #     {"name": "J. Sussberg (PG)", "ppg": "22.8", "rpg": "3.2", "apg": "3.7", "fg_pct": "40%", "fg3_pct": "38%"},
        #     {"name": "D. Hoey (SG)", "ppg": "15.6", "rpg": "5.2", "apg": "4.1", "fg_pct": "46%", "fg3_pct": "35%"},
        #     {"name": "B. Gibbons (SF)", "ppg": "8.4", "rpg": "4.2", "apg": "2.1", "fg_pct": "43%", "fg3_pct": "32%"},
        #     {"name": "F. Miller (PF)", "ppg": "6.2", "rpg": "6.8", "apg": "1.2", "fg_pct": "38%", "fg3_pct": "30%"},
        #     {"name": "L. Mancusi (C)", "ppg": "5.8", "rpg": "7.1", "apg": "0.8", "fg_pct": "52%", "fg3_pct": "0%"}
        # ],
        # "away_team_sim_players": [
        #     {"name": "J. Jerome (PG)", "ppg": "11.2", "rpg": "3.8", "apg": "4.2", "fg_pct": "38%", "fg3_pct": "33%"},
        #     {"name": "G. Flynn (SG)", "ppg": "9.4", "rpg": "2.6", "apg": "2.8", "fg_pct": "50%", "fg3_pct": "48%"},
        #     {"name": "J. Adames (SF)", "ppg": "9.8", "rpg": "4.1", "apg": "1.6", "fg_pct": "42%", "fg3_pct": "35%"},
        #     {"name": "J. Tuttle (PF)", "ppg": "7.2", "rpg": "5.8", "apg": "1.1", "fg_pct": "45%", "fg3_pct": "28%"},
        #     {"name": "J. Richards (C)", "ppg": "6.4", "rpg": "6.2", "apg": "0.6", "fg_pct": "48%", "fg3_pct": "0%"}
        # ],
        # "sim_scenarios": [
        #     {"name": "Jake Sussberg Limited by Injury", "outcome": "Scarsdale's offense stalls without their primary scorer, averaging only 48 points while shooting 33% from the field", "adjustment": "Increase usage for Daniel Hoey as primary ball-handler, run more pick-and-roll actions with Gibbons, and utilize Lev Stahl's efficient shooting (58.3% eFG%)"},
        #     {"name": "Three-Point Shooting Drought", "outcome": "Scarsdale struggles to space the floor, allowing Arlington to pack the paint and limit inside scoring opportunities, leading to 39% win probability", "adjustment": "Emphasize drives to the basket to draw fouls (77.4% FT%), increase post touches for Hoey to collapse defense, and prioritize transition opportunities before Arlington's defense sets"},
        #     {"name": "Daniel Hoey in Foul Trouble", "outcome": "Scarsdale's assist rate drops by 35% and defensive pressure decreases, allowing Arlington's Jerome (10.8 PPG) and Flynn (8.8 PPG) to attack more freely", "adjustment": "Switch to zone defense to protect Hoey, increase Gibbons' playmaking responsibilities, and utilize Stahl's defensive presence while preserving Hoey for fourth quarter minutes"},
        #     {"name": "Bench Production Surge", "outcome": "Scarsdale's win probability jumps to 72% with increased floor spacing and reduced fatigue for starters in fourth quarter/overtime", "adjustment": "Extend rotation to 9 players, run specific actions for Stahl (58.3% eFG%) and Grossberg, and maintain aggressive defensive pressure throughout the game with fresher players"}
        # ]
    }
    
    return templates.TemplateResponse("report_view.html", context)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
