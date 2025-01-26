import sqlite3
import re


def get_db_connection():
    """
    Establishes and returns a database connection to the 'requests.db' file.
    """
    conn = sqlite3.connect('requests.db')
    conn.row_factory = sqlite3.Row  # This allows access to columns by name
    return conn


def is_valid_email(email):
    """
    Validate if the email ends with either @gmail.com or @ceat.com
    """
    return email.endswith('@gmail.com') or email.endswith('@ceat.com')


def insert_request(name, email, description):
    """
    Inserts a new request into the requests table with default status as 'Pending'.
    Ensures the email is valid before inserting.
    """
    if not is_valid_email(email):
        print("Invalid email address. It must end with '@gmail.com' or '@ceat.com'.")
        return  # Early return if email is invalid

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO requests (name, email, description, status) VALUES (?, ?, ?, ?)',
                       (name, email, description, 'Pending'))  # Default status as 'Pending'
        conn.commit()
        print("Request inserted successfully")  # Debugging line
    except sqlite3.Error as e:
        print(f"Error inserting request: {e}")
    finally:
        conn.close()


def get_all_requests():
    """
    Fetches all requests from the requests table and returns them as a list of dictionaries.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT * FROM requests')
        requests = cursor.fetchall()
        return [dict(req) for req in requests]  # Convert rows to dictionaries
    except sqlite3.Error as e:
        print(f"Error fetching requests: {e}")
        return []
    finally:
        conn.close()


def update_request_status(request_id, status):
    """
    Updates the status of a request based on the request ID.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('UPDATE requests SET status = ? WHERE id = ?', (status, request_id))
        conn.commit()
        print(f"Request {request_id} status updated to {status}.")  # Debugging line
    except sqlite3.Error as e:
        print(f"Error updating request status: {e}")
    finally:
        conn.close()


def reset_request_ids():
    """
    Resets the IDs in the `requests` table to ensure they remain sequential after a deletion.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Create a temporary table to hold data
        cursor.execute('CREATE TEMPORARY TABLE temp_requests AS SELECT * FROM requests')
        # Clear the original table
        cursor.execute('DELETE FROM requests')
        # Reset the auto-increment counter
        cursor.execute('DELETE FROM sqlite_sequence WHERE name="requests"')
        # Insert data back into the original table with new IDs
        cursor.execute(
            'INSERT INTO requests (name, email, description, status) SELECT name, email, description, status FROM temp_requests')
        # Drop the temporary table
        cursor.execute('DROP TABLE temp_requests')
        conn.commit()
        print("Request IDs reset successfully.")  # Debugging line
    except sqlite3.Error as e:
        print(f"Error resetting request IDs: {e}")
    finally:
        conn.close()


def delete_request(request_id):
    """
    Deletes a request from the database based on the request ID and resets the request IDs afterward.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('DELETE FROM requests WHERE id = ?', (request_id,))
        conn.commit()
        reset_request_ids()  # Reset IDs to maintain sequence after deletion
        print(f"Request {request_id} deleted successfully.")  # Debugging line
    except sqlite3.Error as e:
        print(f"Error deleting request: {e}")
    finally:
        conn.close()
