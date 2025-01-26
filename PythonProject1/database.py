import sqlite3
import re


def get_db_connection():
   
    conn = sqlite3.connect('requests.db')
    conn.row_factory = sqlite3.Row  
    return conn


def is_valid_email(email):
   
    return email.endswith('@gmail.com') or email.endswith('@ceat.com')


def insert_request(name, email, description):
   
    if not is_valid_email(email):
        print("Invalid email address. It must end with '@gmail.com' or '@ceat.com'.")
        return  
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO requests (name, email, description, status) VALUES (?, ?, ?, ?)',
                       (name, email, description, 'Pending'))  
        conn.commit()
        print("Request inserted successfully")  
    except sqlite3.Error as e:
        print(f"Error inserting request: {e}")
    finally:
        conn.close()


def get_all_requests():
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT * FROM requests')
        requests = cursor.fetchall()
        return [dict(req) for req in requests] 
    except sqlite3.Error as e:
        print(f"Error fetching requests: {e}")
        return []
    finally:
        conn.close()


def update_request_status(request_id, status):
   
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('UPDATE requests SET status = ? WHERE id = ?', (status, request_id))
        conn.commit()
        print(f"Request {request_id} status updated to {status}.")  
    except sqlite3.Error as e:
        print(f"Error updating request status: {e}")
    finally:
        conn.close()


def reset_request_ids():
   
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        
        cursor.execute('CREATE TEMPORARY TABLE temp_requests AS SELECT * FROM requests')
        
        cursor.execute('DELETE FROM requests')
       
        cursor.execute('DELETE FROM sqlite_sequence WHERE name="requests"')
        
        cursor.execute(
            'INSERT INTO requests (name, email, description, status) SELECT name, email, description, status FROM temp_requests')
        
        cursor.execute('DROP TABLE temp_requests')
        conn.commit()
        print("Request IDs reset successfully.")  
    except sqlite3.Error as e:
        print(f"Error resetting request IDs: {e}")
    finally:
        conn.close()


def delete_request(request_id):
  
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('DELETE FROM requests WHERE id = ?', (request_id,))
        conn.commit()
        reset_request_ids()  
        print(f"Request {request_id} deleted successfully.")  
    except sqlite3.Error as e:
        print(f"Error deleting request: {e}")
    finally:
        conn.close()
