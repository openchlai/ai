#!/usr/bin/env python3
"""
Test MySQL connection for AI Service
Usage: python scripts/test_mysql_connection.py
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    import pymysql
    from sqlalchemy import create_engine, text
    from dotenv import load_dotenv
except ImportError as e:
    print(f"❌ Missing dependency: {e}")
    print("Install with: pip install pymysql sqlalchemy python-dotenv")
    sys.exit(1)

# Load environment variables
load_dotenv()

def test_pymysql_connection():
    """Test direct PyMySQL connection"""
    print("\n" + "="*60)
    print("Testing PyMySQL Direct Connection")
    print("="*60)

    host = os.getenv('MYSQL_HOST', '192.168.8.13')
    port = int(os.getenv('MYSQL_PORT', '3306'))
    user = os.getenv('MYSQL_USER', 'ai_service_user')
    password = os.getenv('MYSQL_PASSWORD')
    database = os.getenv('MYSQL_DATABASE', 'ai_service')

    try:
        connection = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            charset='utf8mb4',
            connect_timeout=5
        )

        with connection.cursor() as cursor:
            cursor.execute("SELECT DATABASE(), USER(), VERSION()")
            result = cursor.fetchone()

            print(f"✅ Connected successfully!")
            print(f"   Database: {result[0]}")
            print(f"   User: {result[1]}")
            print(f"   MySQL Version: {result[2]}")

            # Test basic privileges
            cursor.execute("SHOW GRANTS FOR CURRENT_USER()")
            grants = cursor.fetchall()
            print(f"✅ User has {len(grants)} privilege grant(s)")
            for grant in grants:
                print(f"   {grant[0]}")

            # Test SHOW TABLES (read operation)
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            print(f"✅ Database has {len(tables)} table(s)")
            if tables:
                print(f"   Tables: {', '.join([t[0] for t in tables])}")

        connection.close()
        return True

    except Exception as e:
        print(f"❌ PyMySQL connection failed: {e}")
        return False

def test_sqlalchemy_connection():
    """Test SQLAlchemy connection (used by the application)"""
    print("\n" + "="*60)
    print("Testing SQLAlchemy Connection")
    print("="*60)

    database_url = os.getenv('DATABASE_URL')

    if not database_url:
        print("❌ DATABASE_URL not found in environment")
        return False

    try:
        engine = create_engine(database_url, echo=False)

        with engine.connect() as connection:
            result = connection.execute(text("SELECT DATABASE(), USER(), VERSION()"))
            row = result.fetchone()

            print(f"✅ SQLAlchemy connection successful!")
            print(f"   Database: {row[0]}")
            print(f"   User: {row[1]}")
            print(f"   MySQL Version: {row[2]}")

            # Test database operations
            result = connection.execute(text("SHOW TABLES"))
            tables = result.fetchall()
            print(f"✅ Found {len(tables)} tables in database")
            if tables:
                print(f"   Tables: {', '.join([t[0] for t in tables])}")

        return True

    except Exception as e:
        print(f"❌ SQLAlchemy connection failed: {e}")
        return False

def main():
    print("\n🔍 MySQL Connection Test for AI Service")
    print(f"Server: {os.getenv('MYSQL_HOST', '192.168.8.13')}:{os.getenv('MYSQL_PORT', '3306')}")
    print(f"Database: {os.getenv('MYSQL_DATABASE', 'ai_service')}")
    print(f"User: {os.getenv('MYSQL_USER', 'ai_service_user')}")

    # Test both connection methods
    pymysql_ok = test_pymysql_connection()
    sqlalchemy_ok = test_sqlalchemy_connection()

    print("\n" + "="*60)
    print("Summary")
    print("="*60)
    print(f"PyMySQL Connection: {'✅ PASSED' if pymysql_ok else '❌ FAILED'}")
    print(f"SQLAlchemy Connection: {'✅ PASSED' if sqlalchemy_ok else '❌ FAILED'}")

    if pymysql_ok and sqlalchemy_ok:
        print("\n✅ All tests passed! MySQL is ready for the AI Service.")
        return 0
    else:
        print("\n❌ Some tests failed. Please check the configuration.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
