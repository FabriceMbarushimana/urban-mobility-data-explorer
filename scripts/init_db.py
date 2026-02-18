import mysql.connector
from mysql.connector import errorcode
import os
from dotenv import load_dotenv

load_dotenv()

def init_db():
    host = os.getenv("DB_HOST", "localhost")
    user = os.getenv("DB_USER", "root")
    password = os.getenv("DB_PASSWORD", "")
    port = int(os.getenv("DB_PORT", 3306))
    ssl_ca = os.getenv("DB_SSL_CA")

    config = {
        "host": host,
        "user": user,
        "password": password,
        "port": port
    }

    if ssl_ca:
        config["ssl_ca"] = ssl_ca
        config["ssl_verify_cert"] = True

    try:
        # Connect without specifying database to create it
        print(f"[INFO] Connecting to MySQL server at {host}...")
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()

        # Determine schema file path
        script_dir = os.path.dirname(os.path.abspath(__file__))
        schema_path = os.path.join(os.path.dirname(script_dir), "schema.sql")

        print(f"[INFO] Reading schema from: {schema_path}")
        with open(schema_path, 'r') as f:
            schema_sql = f.read()

        # Split and execute individual commands
        # Note: mysql-connector python doesn't support reading multiple statements in a single execute calls well without 'multi=True'
        # The schema.sql has simple statements separated by ;
        # We will iterate through them

        print("[INFO] Executing schema statements...")

        # Manual splitting is safer and more portable for simple schemas
        statements = schema_sql.split(';')

        for statement in statements:
            statement = statement.strip()
            if statement:
                try:
                    cursor.execute(statement)
                    print(f"[INFO] Executed successfully: {statement[:60]}...")
                except mysql.connector.Error as err:
                    print(f"[ERROR] Failed executing statement: {statement[:60]}...")
                    print(f"[ERROR] {err}")
                    # Continue or break? For schema init, breaking is usually safer if something fails.
                    raise err

        conn.commit()
        print("[INFO] Database and schema initialized successfully.")

        cursor.close()
        conn.close()

    except mysql.connector.Error as err:
        print(f"[ERROR] Failed initializing database: {err}")
        exit(1)
    except Exception as e:
        print(f"[ERROR] An unexpected error occurred: {e}")
        exit(1)

if __name__ == "__main__":
    init_db()

