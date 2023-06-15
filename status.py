import sys
import asyncio

from src.tools.database import db
from src.tools.pulsar import Portal

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
    
elif sys.argv[1] == "check_pulsar":
    try:
        class Template(Portal):
            async def on_join(self):
                print("\n-> Pulsar connection successful!")
                exit(0)
        
        action = Template()
        asyncio.run(action.run())
        
    except Exception as e:
        print("\n-> Pulsar connection failed! Trace:\n")
        print(e)
        exit(1)
        
elif sys.argv[1] == "check_rcon":
    pass