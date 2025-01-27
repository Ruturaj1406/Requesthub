import sqlite3
import json


def get_db_connection():
    """
    Establishes a connection to the SQLite database and sets the row factory.
    """
    conn = sqlite3.connect('requests.db')
    conn.row_factory = sqlite3.Row
    return conn


def is_valid_email(email):
    """
    Validates email addresses to ensure they end with '@gmail.com' or '@ceat.com'.
    """
    return email.endswith('@gmail.com') or email.endswith('@ceat.com')


def insert_request(name, email, selected_items):
    """
    Inserts a new request into the database with multiple selected items.

    Args:
        name (str): Name of the requester.
        email (str): Email address of the requester.
        selected_items (list): List of selected items.
    """
    if not is_valid_email(email):
        print("Invalid email address. It must end with '@gmail.com' or '@ceat.com'.")
        return

    # Convert the list of selected items to a JSON string
    description = json.dumps(selected_items)

    try:
        with get_db_connection() as conn:
            conn.execute(
                '''
                INSERT INTO requests (name, email, description, status)
                VALUES (?, ?, ?, ?)
                ''',
                (name, email, description, 'Pending')
            )
        print("Request inserted successfully.")
    except sqlite3.Error as e:
        print(f"Error inserting request: {e}")


def get_all_requests():
    """
    Retrieves all requests from the database.

    Returns:
        list: A list of dictionaries containing request details.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM requests')
            requests = cursor.fetchall()

            # Parse the JSON description or leave it as-is
            all_requests = []
            for req in requests:
                description = req["description"]
                try:
                    # If stored as JSON
                    items = json.loads(description)
                except json.JSONDecodeError:
                    # Fallback if stored as a plain string
                    items = description.split(", ")

                all_requests.append({
                    "id": req["id"],
                    "name": req["name"],
                    "email": req["email"],
                    "items": items,
                    "status": req["status"]
                })
            return all_requests
    except sqlite3.Error as e:
        print(f"Error fetching requests: {e}")
        return []


def update_request_status(request_id, status):
    """
    Updates the status of a request by its ID.

    Args:
        request_id (int): ID of the request to update.
        status (str): New status to set.
    """
    try:
        with get_db_connection() as conn:
            conn.execute(
                'UPDATE requests SET status = ? WHERE id = ?',
                (status, request_id)
            )
        print(f"Request {request_id} status updated to '{status}'.")
    except sqlite3.Error as e:
        print(f"Error updating request status: {e}")


def reset_request_ids():
    """
    Resets the auto-increment IDs of the requests table.
    """
    try:
        with get_db_connection() as conn:
            # Temporarily store data
            conn.execute('CREATE TEMPORARY TABLE temp_requests AS SELECT * FROM requests')

            # Clear the requests table
            conn.execute('DELETE FROM requests')

            # Reset auto-increment sequence
            conn.execute('DELETE FROM sqlite_sequence WHERE name="requests"')

            # Reinsert data from the temporary table
            conn.execute(
                '''
                INSERT INTO requests (name, email, description, status)
                SELECT name, email, description, status FROM temp_requests
                '''
            )

            # Drop the temporary table
            conn.execute('DROP TABLE temp_requests')

        print("Request IDs reset successfully.")
    except sqlite3.Error as e:
        print(f"Error resetting request IDs: {e}")


def delete_request(request_id):
    """
    Deletes a request by its ID and resets IDs.

    Args:
        request_id (int): ID of the request to delete.
    """
    try:
        with get_db_connection() as conn:
            conn.execute('DELETE FROM requests WHERE id = ?', (request_id,))
        print(f"Request {request_id} deleted successfully.")
        reset_request_ids()
    except sqlite3.Error as e:
        print(f"Error deleting request: {e}")


# Example function usage
if __name__ == "__main__":
    # Example: Insert a request with multiple selected items
    selected_items = ["Item1", "Item2", "Item3"]  # List of items
    insert_request("John Doe", "john.doe@gmail.com", selected_items)

    # Example: Fetch and display all requests
    all_requests = get_all_requests()
    for request in all_requests:
        print(f"Request ID: {request['id']}")
        print(f"Name: {request['name']}")
        print(f"Email: {request['email']}")
        print(f"Selected Items: {', '.join(request['items'])}")
        print(f"Status: {request['status']}\n")

    # Example: Update a request's status
    update_request_status(1, "Completed")

    # Example: Delete a request
    delete_request(1)

    # Example: Reset request IDs
    reset_request_ids()
