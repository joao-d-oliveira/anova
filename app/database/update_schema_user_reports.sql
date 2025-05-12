-- Add user_id to games table to associate games with users
ALTER TABLE games ADD COLUMN IF NOT EXISTS user_id INTEGER REFERENCES users(id);

-- Create index on user_id for faster lookups
CREATE INDEX IF NOT EXISTS idx_games_user_id ON games(user_id);
