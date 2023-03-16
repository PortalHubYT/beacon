import datetime
import psycopg2
import os

from dotenv import load_dotenv

from config import config

load_dotenv()

POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")

class PostgresDB:

    database_definition = {
        "users": {
            "nickname": "text",
            "unique_id": "text",
            "user_id": "varchar(20) PRIMARY KEY NOT NULL",
            "role": "text",
            "followers": "integer",
            "following": "integer",
            "avatar1": "text",
            "avatar2": "text",
            "avatar3": "text",
            "avatar4": "text",
            "total_gifted_value": "integer NOT NULL DEFAULT(0)",
            "gifted_value_since_last_reset": "integer NOT NULL DEFAULT(0)",
        },
        "comments": {
            "timestamp": "timestamp",
            "user_id": "text",
            "comment": "text",
            "parsed": "boolean",
        },
        "gifts": {
            "timestamp": "timestamp",
            "user_id": "text",
            "gift": "text",
            "parsed": "boolean",
        },
        "follows": {"timestamp": "timestamp", "user_id": "text", "parsed": "boolean",},
        "joins": {"timestamp": "timestamp", "user_id": "text", "parsed": "boolean",},
        "likes": {"timestamp": "timestamp", "user_id": "text", "parsed": "boolean",},
        "shares": {"timestamp": "timestamp", "user_id": "text", "parsed": "boolean",},
        "views": {"timestamp": "timestamp", "count": "integer",},
    }

    def __init__(self, host, database, user, password, port):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.port = port
        self.tables = self.database_definition
        self.connect()
        self.initialize_tables()

    def initialize_tables(self):
        for keys in self.tables:

            if keys in self.get_tables():
                continue

            if keys == "views":
                self.create_table(keys, self.tables[keys])
                continue

            elif keys == "users":
                self.create_table(keys, self.tables[keys])

            else:
                constraint = f"CONSTRAINT FK_{keys}_user_id FOREIGN KEY (user_id) REFERENCES users(user_id)"
                self.create_table(keys, self.tables[keys], constraint)

            self.execute_commit(
                f"CREATE INDEX IF NOT EXISTS {keys}_user_id_idx ON {keys} (user_id)"
            )

    def reset_database(self, confirm=False):
        print("YOU JUST RESETTED DATABASE? MAKE SURE THIS IS INTENTIONAL")
        print(
            "NO PRESSURE, YOU CAN ALWAYS REVERT WHAT YOU DID, idk how though good luck"
        )
        print("...")
        print("You have to pass 'confirm' as True to actually reset the database")
        print(
            "Sorry for the inconvenience, I'm just making sure this is absolutely intentional"
        )
        print("Please remove this line ASAP from the code")
        print("... and sorry if you are just doing testing")
        if not confirm:
            return
        if self.tables:
            for table in self.get_tables():
                self.execute_commit(f"DROP TABLE {table} CASCADE")
            self.initialize_tables()

    def connect(self):
        """Establishes a connection to the database."""
        self.conn = psycopg2.connect(
            host=self.host,
            database=self.database,
            user=self.user,
            password=self.password,
            port=self.port,
        )
        self.cur = self.conn.cursor()

    def execute(self, query, params=None):
        """Executes a SQL query and returns the result."""
        if config.stream_ready == False:
            return
        self.cur.execute(query, params)

    def get(self, query, params=None, one=False):
        """Executes a SQL query and returns the result."""
        if config.stream_ready == False:
            return
        self.cur.execute(query, params)
        if one:
            return self.cur.fetchone()
        else:
            return self.cur.fetchall()

    def execute_commit(self, query, params=None):
        """Executes a SQL query and commits the transaction."""
        if config.stream_ready == False:
            return
        self.cur.execute(query, params)
        self.conn.commit()

    def insert(self, table_name, columns, values):
        """Inserts a row into the given table."""
        columns_sql = ", ".join(columns)
        values_sql = ", ".join(["%s"] * len(values))
        query = f"INSERT INTO {table_name} ({columns_sql}) VALUES ({values_sql})"
        self.execute(query, values)

    def insert_commit(self, table_name, columns, values):
        """Inserts a row into the given table and commits."""
        self.insert(table_name, columns, values)
        self.commit()

    def commit(self):
        """Commits the transaction."""
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
        # Remove all the tables that are not defined in the database definition
        parsed = []
        for table in tables:
            if table[0] in self.tables:
                parsed.append(table)

        return [table[0] for table in parsed]

    def create_table(self, table_name, columns, constraints=None):
        """
        Creates a new table with the given name and columns.

        Arguments:
        - table_name: the name of the new table to create
        - columns: a dictionary where the keys are column names and the values are SQL data types
        """

        if self.table_exists(table_name):
            return

        columns_sql = ", ".join(
            [f"{col} {data_type}" for col, data_type in columns.items()]
        )
        query = f"CREATE TABLE {table_name} ({columns_sql}{(', ' + constraints) if constraints else ''})"
        self.cur.execute(query)
        self.conn.commit()

    def table_exists(self, table_name):
        return table_name in self.get_tables()


class StreamDB(PostgresDB):
    def check_user_exists(self, profile):
        """Checks if a user exists in the database, based on their user_id"""
        uid = profile["user_id"]
        query = f"SELECT * FROM users WHERE user_id = '{uid}'"
        return self.get(query, one=True) != None

    def add_new_user(self, profile):
        """Adds a new user to the database"""
        if not self.check_user_exists(profile):
            columns = [
                "nickname",
                "unique_id",
                "user_id",
                "role",
                "followers",
                "following",
                "avatar1",
                "avatar2",
                "avatar3",
                "avatar4",
            ]
            avatars = []
            for i in range(4):
                try:
                    avatars.append(profile["avatars"][i])
                except IndexError:
                    avatars.append("None")

            if profile["role"] == None:
                role = "None"
            else:
                role = profile["role"]

            values = [
                profile["nickname"],
                profile["unique_id"],
                profile["user_id"],
                role,
                profile["followers"],
                profile["following"],
                *avatars,
            ]
            self.insert("users", columns, values)
            return True
        else:
            return False

    def add_event(self, profile, event):
        """Adds an event to the database"""
        table_name = event + "s"
        if event == "gift":
            self.insert(
                table_name,
                ["timestamp", "user_id", "gift", "parsed"],
                [datetime.datetime.now(), profile["user_id"], profile["gift"], False],
            )
        elif event == "comment":
            self.insert(
                table_name,
                ["timestamp", "user_id", "comment", "parsed"],
                [
                    datetime.datetime.now(),
                    profile["user_id"],
                    profile["comment"],
                    False,
                ],
            )
        else:
            self.insert(
                table_name,
                ["timestamp", "user_id", "parsed"],
                [datetime.datetime.now(), profile["user_id"], False],
            )

    def store_views(self, count):
        """Stores the views in the database"""
        self.insert("views", ["timestamp", "count"], [datetime.datetime.now(), count])

    def update_value_for_id(self, table_name, column, value, user_id):
        sql = f"UPDATE {table_name} SET {column} = {value} WHERE user_id = '{user_id}'"
        self.execute_commit(sql)

    def increment_value_for_id(self, table_name, column, increment, user_id):
        sql = f"UPDATE {table_name} SET {column} = {column} + {increment} WHERE user_id = '{user_id}'"
        self.execute_commit(sql)

    def set_user_gifted(self, value, user_id):
        self.update_value_for_id("users", "gifted", value, user_id)

    def add_user_gifted(self, value, user_id):
        self.increment_value_for_id("users", "gifted", value, user_id)
        self.increment_value_for_id("users", "gifted_since_action", value, user_id)

    def reset_user_gifted_since_action(self, user_id):
        self.update_value_for_id("users", "gifted_since_action", 0, user_id)

    def get_user_gifted_since_action(self, user_id):
        sql = f"SELECT gifted_since_action, avatar3 FROM users WHERE user_id = '{user_id}'"
        ret = self.get(sql, (user_id,), one=True)
        return ret


db = StreamDB(
    POSTGRES_HOST, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_PORT
)

