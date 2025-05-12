-- Add users table for authentication
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    cognito_id VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    phone_number VARCHAR(20),
    school VARCHAR(100),
    role VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Add user_id to coaches table for linking coaches to users
ALTER TABLE coaches ADD COLUMN IF NOT EXISTS user_id INTEGER REFERENCES users(id);

-- Create index on cognito_id for faster lookups
CREATE INDEX IF NOT EXISTS idx_users_cognito_id ON users(cognito_id);

-- Create index on email for faster lookups
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);