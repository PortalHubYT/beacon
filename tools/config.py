import json
import psycopg2

with open("config.json", "r") as f:
    config = json.load(f)


class PostgresDB:
    def __init__(self, host, database, user, password):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.connect()

    def connect(self):
        """Establishes a connection to the database."""
        self.conn = psycopg2.connect(
            host=self.host,
            database=self.database,
            user=self.user,
            password=self.password,
        )
        self.cur = self.conn.cursor()

    def execute(self, query, params=None):
        """Executes a SQL query and returns the result."""
        self.cur.execute(query, params)
        return self.cur.fetchall()

    def execute_commit(self, query, params=None):
        """Executes a SQL query and commits the transaction."""
        self.cur.execute(query, params)
        self.conn.commit()

    def close(self):
        """Closes the cursor and connection."""
        self.cur.close()
        self.conn.close()

    def get_tables(self):
        """Returns a list of table names in the database."""
        query = "SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname = 'public'"
        self.cur.execute(query)
        tables = self.cur.fetchall()
        return [table[0] for table in tables]

    def create_table(self, table_name, columns):
        """
        Creates a new table with the given name and columns.

        Arguments:
        - table_name: the name of the new table to create
        - columns: a dictionary where the keys are column names and the values are SQL data types
        """
        columns_sql = ", ".join(
            [f"{col} {data_type}" for col, data_type in columns.items()]
        )
        query = f"CREATE TABLE {table_name} ({columns_sql})"
        self.cur.execute(query)
        self.conn.commit()


db = PostgresDB("localhost", "stream", config["server_ip"], config["rcon_password"])

db.create_table(
    "users",
    {"nickname": "text", "unique_id": "text", "user_id": "text", "role": "text"},
)

db.create_table(
    "comments",
    {
        "user_id": "text",
        "comment": "text",
        "parsed": "boolean",
    },
)

db.create_table(
    "gifts",
    {
        "user_id": "text",
        "gift": "text",
        "parsed": "boolean",
    },
)

# Create a new table for followers
db.create_table(
    "follows",
    {
        "user_id": "text",
        "parsed": "boolean",
    },
)

# Create a new table for joins
db.create_table("joins", {"user_id": "text", "parsed": "boolean"})

# Create a table for likes
db.create_table("likes", {"user_id": "text", "parsed": "boolean"})

# Create a table for shares
db.create_table("shares", {"user_id": "text", "parsed": "boolean"})
