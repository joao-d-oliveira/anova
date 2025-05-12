-- Update team_stats table column names
ALTER TABLE team_stats 
RENAME COLUMN fg_pct TO fg_percentage;

ALTER TABLE team_stats 
RENAME COLUMN fg3_pct TO three_pt_percentage;

ALTER TABLE team_stats 
RENAME COLUMN ft_pct TO ft_percentage;

-- Add columns for made and attempted shots if they don't exist
ALTER TABLE team_stats 
ADD COLUMN IF NOT EXISTS fg_made INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS fg_attempted INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS three_pt_made INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS three_pt_attempted INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS ft_made INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS ft_attempted INTEGER DEFAULT 0;

-- Update players table column name
ALTER TABLE players 
RENAME COLUMN number TO jersey_number;
