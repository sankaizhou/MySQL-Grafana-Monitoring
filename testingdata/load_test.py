import mysql.connector
from mysql.connector import Error
from faker import Faker
import time

# Database connection parameters
DB_CONFIG = {
    'host': '127.0.0.1',        # Master server host
    'port': 3306,               # Master server port
    'user': 'root',             # Replace with your MySQL username
    'password': '',             # Replace with your MySQL password
    'database': 'replicated_db' # Database name
}

# Initialize Faker
fake = Faker()

def insert_user(cursor):
    # Generate fake data
    first_name = fake.first_name()
    last_name = fake.last_name()
    email = fake.email()
    address = fake.address().replace('\n', ', ')

    # Prepare SQL Insert statement
    sql_insert_query = """INSERT INTO users (first_name, last_name, email, address) 
                          VALUES (%s, %s, %s, %s)"""
    record = (first_name, last_name, email, address)

    # Execute the insert statement
    cursor.execute(sql_insert_query, record)

def insert_users(num_inserts):
    try:
        # Establish a connection
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()

        for _ in range(num_inserts):
            insert_user(cursor)

        connection.commit()
        print(f"Inserted {num_inserts} records")

    except Error as e:
        print(f"Error: {e}")

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection closed")

def main():
    try:
        print("Starting continuous load testing for 5 minutes...")

        start_time = time.time()
        duration = 5 * 60  # 5 minutes in seconds

        while True:
            current_time = time.time()
            if current_time - start_time >= duration:
                print("5 minutes have passed. Stopping data generation.")
                break

            insert_users(100)  # Insert 100 records
            time.sleep(5)      # Wait for 5 seconds

    except KeyboardInterrupt:
        print("Load testing stopped by user.")

if __name__ == "__main__":
    main()
