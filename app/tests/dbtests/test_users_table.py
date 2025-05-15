#!/usr/bin/env python3
from app.tests.dbtests.db_tester_base import DatabaseTesterBase

class UsersTester(DatabaseTesterBase):
    """Test class for users table operations"""
    
    def test_creation_deletion_table_users(self):
        """Test creating and deleting the users table"""
        print("\n=== Testing Table: users ===")
        
        if not self.connect():
            return False
            
        try:
            # Drop table if exists
            self.cur.execute("DROP TABLE IF EXISTS users CASCADE;")
            
            # Create table
            self.cur.execute("""
                CREATE TABLE users (
                    id SERIAL PRIMARY KEY,
                    cognito_id VARCHAR(255) NOT NULL,
                    email VARCHAR(255) NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # Insert test data
            self.cur.execute("""
                INSERT INTO users (cognito_id, email, name)
                VALUES (%s, %s, %s);
            """, ('test-cognito-id', 'test@example.com', 'Test User'))
            
            # Query data
            self.cur.execute("SELECT * FROM users;")
            rows = self.cur.fetchall()
            print(f"Inserted {len(rows)} row(s) into users table")
            
            # Check table structure
            self.check_table_structure("users")
            
            # Clean up
            self.cur.execute("DROP TABLE IF EXISTS users CASCADE;")
            self.conn.commit()
            
            print("Users table test successful!")
            return True
            
        except Exception as e:
            self.conn.rollback()
            print(f"Error testing users table: {e}")
            return False
        finally:
            self.disconnect()

def run_test():
    """Run the users table test"""
    tester = UsersTester()
    return tester.test_creation_deletion_table_users()

if __name__ == "__main__":
    success = run_test()
    import sys
    sys.exit(0 if success else 1)
