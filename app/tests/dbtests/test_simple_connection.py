#!/usr/bin/env python3
from app.tests.dbtests.db_tester_base import DatabaseTesterBase

class SimpleConnectionTester(DatabaseTesterBase):
    """Test class for basic database connection"""
    
    def simple_test_connection(self):
        """Test basic connection to the database"""
        print("\n=== Testing Basic Database Connection ===")
        
        if not self.connect():
            return False
            
        try:
            # Execute a simple query
            self.cur.execute("SELECT version();")
            
            # Get the result
            version = self.cur.fetchone()
            print(f"PostgreSQL version: {version[0]}")
            
            # Test if we can query the tables
            self.cur.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """)
            
            tables = self.cur.fetchall()
            print("\nDatabase tables:")
            for table in tables:
                print(f"- {table[0]}")
                
            print("\nBasic connection test successful!")
            return True
            
        except Exception as e:
            print(f"Error in simple connection test: {e}")
            return False
        finally:
            self.disconnect()

def run_test():
    """Run the simple connection test"""
    tester = SimpleConnectionTester()
    return tester.simple_test_connection()

if __name__ == "__main__":
    success = run_test()
    import sys
    sys.exit(0 if success else 1)
