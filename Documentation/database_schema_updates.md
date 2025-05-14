# Database Schema Updates

This document describes the database schema updates needed to fix issues with column names in the database.

## Issues Identified

Based on the error logs, the following issues were identified:

1. In the `team_stats` table:
   - The code is trying to use `fg_percentage`, `three_pt_percentage`, and `ft_percentage` columns, but the actual schema uses `fg_pct`, `fg3_pct`, and `ft_pct`.
   - Some columns are missing: `fg_made`, `fg_attempted`, `three_pt_made`, `three_pt_attempted`, `ft_made`, `ft_attempted`.

2. In the `players` table:
   - The code is trying to use `jersey_number` column, but the actual schema uses `number`.

## Solution

Two approaches were implemented to fix these issues:

1. **Update the database schema** to match the column names used in the code.
2. **Update the code** to use the column names in the database schema.

For this implementation, we chose to update the database schema to match the code, as it's more maintainable to keep the code consistent.

## Files Created

1. `app/database/update_schema_fields.sql` - SQL script with the schema updates
2. `app/database/apply_schema_updates.py` - Python script to apply the SQL updates
3. `app/database/check_schema.py` - Python script to check the current database schema
4. `app/database/cleanup_database.py` - Comprehensive script that checks, updates, and verifies the database schema

## How to Apply the Updates

Run the following command to apply the database schema updates:

```bash
python app/database/cleanup_database.py
```

This script will:
1. Check the current database schema
2. Determine what updates are needed
3. Apply the necessary updates
4. Verify that the updates were applied correctly

## Schema Changes

The following changes are made to the database schema:

1. In the `team_stats` table:
   - Rename `fg_pct` to `fg_percentage`
   - Rename `fg3_pct` to `three_pt_percentage`
   - Rename `ft_pct` to `ft_percentage`
   - Add columns: `fg_made`, `fg_attempted`, `three_pt_made`, `three_pt_attempted`, `ft_made`, `ft_attempted`

2. In the `players` table:
   - Rename `number` to `jersey_number`

## Code Changes

The `app/database/connection.py` file was updated to use the correct column names in the `insert_team_stats` function.

## Verification

After applying the updates, you can verify that the schema changes were applied correctly by running:

```bash
python app/database/check_schema.py
```

This will display the current schema of all tables in the database, allowing you to confirm that the column names are correct.
