import sys

from src.tools.database import db

if sys.argv[1] == "check_database":
    print("\n-> Checking database connection...")
    try:
        tables = db.get_tables()
        print("\n-> Database connection successful!")
        exit(0)
    except Exception as e:
        print("\n-> Database connection failed! Trace:\n")
        print(e)
        exit(1)
        
elif sys.argv[1] == "check_tables_empty":
    print("\n-> Checking if tables are empty...")
    table_empty = db.check_tables_empty()
    
    if table_empty:
        print("\n-> Tables are empty!")
        exit(0)
    else:
        print("\n-> Tables are not empty!")
        exit(1)
        
elif sys.argv[1] == "reset_database":
    print("\n-> Emptying tables...")
    db.reset_database(confirm=True)