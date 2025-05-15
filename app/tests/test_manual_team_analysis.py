from app.services.anthropic_api import analyze_team_pdf

filename = "/Users/joao/Desktop/Local-Current-Work/Anona/data/input_samples/SCARSDALE Last 5 games individual stats.pdf"
prompt_path = "/Users/joao/Desktop/Local-Current-Work/Anona/prompts/team_analysis_prompt.txt"
data =  analyze_team_pdf(file_path = filename, is_our_team = True, prompt_path = prompt_path)
k = 0
pass
