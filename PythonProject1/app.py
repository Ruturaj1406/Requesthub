import streamlit as st
import re
from database import get_all_requests, update_request_status, insert_request, delete_request
from mail import send_email

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

DEPARTMENTS = ["Digital", "IT", "HR", "Finance", "Operations"]

ITEMS_LIST = [
    {"particular": "A3 ENVELOPE GREEN"},
    {"particular": "A3 PAPER"},
    {"particular": "A3 TRANSPARENT FOLDER"},
    {"particular": "A4 ENVELOPE GREEN"},
    {"particular": "A4 LOGO ENVOLOP"},
    {"particular": "A4 PAPER"},
    {"particular": "A4 TRANSPARENT FOLDER"},
    {"particular": "BINDER CLIP 19MM"},
    {"particular": "BINDER CLIP 25MM"},
    {"particular": "BINDER CLIP 41MM"},
    {"particular": "BOX FILE"},
    {"particular": "C D MARKER"},
    {"particular": "CALCULATOR"},
    {"particular": "CARBON PAPERS"},
    {"particular": "CELLO TAPE"},
    {"particular": "CUTTER"},
    {"particular": "DUSTER"},
    {"particular": "ERASER"},
    {"particular": "FEVI STICK"},
    {"particular": "GEL PEN BLACK"},
    {"particular": "HIGH LIGHTER"},
    {"particular": "L FOLDER"},
    {"particular": "LETTER HEAD"},
    {"particular": "LOGO ENVOLOP SMALL"},
    {"particular": "NOTE PAD"},
    {"particular": "PEN"},
    {"particular": "PENCIL"},
    {"particular": "PERMANENT MARKER"},
    {"particular": "PUNCHING MACHINE"},
    {"particular": "PUSH PIN"},
    {"particular": "REGISTER"},
    {"particular": "ROOM SPRAY"},
    {"particular": "RUBBER BAND BAG"},
    {"particular": "SCALE"},
    {"particular": "SCISSOR"},
    {"particular": "FILE SEPARATOR"},
    {"particular": "SHARPENER"},
    {"particular": "SKETCH PEN"},
    {"particular": "SILVER PEN"},
    {"particular": "SPRING FILE"},
    {"particular": "STAMP PAD"},
    {"particular": "STAMP PAD INK"},
    {"particular": "STAPLER"},
    {"particular": "STAPLER PIN BIG"},
    {"particular": "STAPLER PIN SMALL"},
    {"particular": "STICKY NOTE"},
    {"particular": "TRANSPARENT FILE"},
    {"particular": "U PIN"},
    {"particular": "VISTING CARD HOLDER"},
    {"particular": "WHITE BOARD MARKER"},
    {"particular": "WHITE INK"},
]

if 'is_user_logged_in' not in st.session_state:
    st.session_state.is_user_logged_in = False
    st.session_state.user_details = {}

if 'is_admin' not in st.session_state:
    st.session_state.is_admin = False


def validate_email(email):
    email_regex = r'^[a-zA-Z0-9_.+-]+@(gmail\.com|ceat\.com)$'
    return re.match(email_regex, email) is not None


def user_login():
    st.title("User Login")
    emp_id = st.text_input("Employee ID", key="emp_id")
    email = st.text_input("Email", key="email")

    department = st.selectbox("Department", [""] + DEPARTMENTS, key="department")

    if st.button("Login"):
        if not validate_email(email):
            st.error("Please enter a valid email id")
        elif emp_id.strip() and email.strip() and department.strip():
            st.session_state.is_user_logged_in = True
            st.session_state.user_details = {
                "emp_id": emp_id,
                "email": email,
                "department": department
            }
            st.success("Login successful!")
        else:
            st.error("Please fill out all fields to log in.")





def user_request_form():
    """User request form"""
    st.title("Request Form")
    user_name = st.text_input("Enter your Name")

    user_email = st.session_state.user_details.get("email", "")

    # Initialize selected_items in session state if it doesn't exist
    if "selected_items" not in st.session_state:
        st.session_state.selected_items = {}

    # Search functionality for items
    search_query = st.text_input("Search Items")
    filtered_items = [item for item in ITEMS_LIST if search_query.lower() in item["particular"].lower()]

    # Display filtered items in a list
    st.subheader("Add Items")
    for idx, item in enumerate(filtered_items):
        item_name = item["particular"]

        # Initialize session state for the item if not already present
        if item_name not in st.session_state.selected_items:
            st.session_state.selected_items[item_name] = {"selected": False, "quantity": 1}

        # Use columns for better layout
        col1, col2 = st.columns([4, 1])

        with col1:
            # Checkbox for selecting the item
            if st.checkbox(item_name, value=st.session_state.selected_items[item_name]["selected"], key=f"checkbox_{idx}"):
                st.session_state.selected_items[item_name]["selected"] = True
            else:
                st.session_state.selected_items[item_name]["selected"] = False
                # Reset quantity if unchecked
                st.session_state.selected_items[item_name]["quantity"] = 1

        # Only show quantity input if the item is selected
        if st.session_state.selected_items[item_name]["selected"]:
            with col2:
                # Manual quantity input
                quantity = st.number_input(
                    f"Enter quantity for {item_name}",
                    min_value=1,
                    value=st.session_state.selected_items[item_name]["quantity"],
                    key=f"quantity_{idx}",
                )
                # Update the session state with the quantity entered by the user
                st.session_state.selected_items[item_name]["quantity"] = quantity

    # Show selected items and their quantities before submitting
    selected_items = {item: details for item, details in st.session_state.selected_items.items() if details["selected"]}
    if selected_items:
        st.subheader("Selected Items")
        for item_name, details in selected_items.items():
            # Display the same quantity in the selected items section
            st.write(f"Item: {item_name}, Quantity: {details['quantity']}")

    # Submit Request
    if st.button("Submit Request"):
        if not user_name.strip():
            st.error("Please enter your name.")
        elif not selected_items:
            st.error("Please select at least one item before submitting the request.")
        else:
            # Format selected items into a single string
            formatted_description = ", ".join(
                [f"{item_name} (Quantity: {details['quantity']})" for item_name, details in selected_items.items()]
            )

            # Insert into the database
            insert_request(user_name, user_email, formatted_description)

            # Send email notification
            request_details = {
                "name": user_name,
                "email": user_email,
                "description": formatted_description,
            }
            subject = "Request Submission"
            body = (
                f"Request details:\nName: {user_name}\nItems: {formatted_description}"
            )
            send_email(user_email, "System", request_details, subject, body)

            st.success("Your requests have been submitted successfully!")

            # Clear selected items after submission
            st.session_state.selected_items = {}

    # Back Button
    if st.button("Back"):
        st.session_state.is_user_logged_in = False
        st.session_state.request_submitted = False
        st.session_state.page = "User Login"



def admin_login():
    st.sidebar.title("Admin Login")
    username = st.sidebar.text_input("Username", key="admin_username")
    password = st.sidebar.text_input("Password", type="password", key="admin_password")
    admin_email = st.sidebar.text_input("Admin Email", key="admin_email")

    if st.sidebar.button("Login"):
        if not validate_email(admin_email):
            st.sidebar.error("Please enter a valid email ending with @gmail.com or @ceat.com")
        elif username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            st.session_state.is_admin = True
            st.sidebar.success("Admin login successful!")
        else:
            st.sidebar.error("Invalid credentials!")


def admin_dashboard():
    """Admin Dashboard for managing requests and communicating with users."""
    st.title("Admin Dashboard")

    # Fetch all requests from the database
    requests = get_all_requests()

    if requests:
        for req in requests:
            # Extract request details
            req_id = req.get("id", "N/A")
            emp_id = req.get("emp_id", "N/A")
            email = req.get("email", "N/A")
            status = req.get("status", "Pending")

            # Description parsing for multiple items
            description = req.get("description", "N/A")
            if isinstance(description, list):
                description = "\n".join(description)  # Combine all selected items into a single string

            # Display request details
            st.write(f"### Request ID: {req_id}")
            st.write(f"- **Emp ID**: {emp_id}")
            st.write(f"- **Email**: {email}")
            st.write(f"- **Description**:\n{description}")
            st.write(f"- **Status**: {status}")

            # Columns for status update and actions
            col1, col2, col3 = st.columns([3, 2, 2])

            with col1:
                # Status update options
                status_update = st.radio(
                    f"Update Status for Request {req_id}",
                    ["Pending", "Approved", "Rejected"],
                    index=["Pending", "Approved", "Rejected"].index(status),
                    key=f"status_{req_id}",
                )

            with col2:
                # Button to update the status
                if st.button(f"Update Status {req_id}", key=f"update_{req_id}"):
                    update_request_status(req_id, status_update)
                    subject = f"Request {status_update.capitalize()}"
                    body = (
                        f"Your request has been {status_update.lower()}.\n\n"
                        f"Request Details:\n{description}"
                    )
                    send_email(email, "Admin", req, subject, body)
                    st.success(f"Status for Request {req_id} updated and email sent!")

            with col3:
                # Button to delete the request
                if st.button(f"Delete Request {req_id}", key=f"delete_{req_id}"):
                    delete_request(req_id)
                    st.success(f"Request ID {req_id} deleted!")

            st.write("---")  # Divider between requests

    else:
        st.info("No requests available.")

    # Send message functionality
    st.subheader("Send Message to User")
    user_emails = [req["email"] for req in requests if req.get("email")]
    selected_email = st.selectbox("Select User Email", [""] + list(set(user_emails)))

    message_content = st.text_area("Enter your message", height=150)

    if st.button("Send Message"):
        if selected_email and message_content.strip():
            subject = "Message from Admin"
            body = f"{message_content}"
            request_details = {
                "name": "User",
                "email": selected_email,
                "description": "Admin Message",
            }
            send_email(selected_email, "Admin", request_details, subject, body)
            st.success(f"Message sent to {selected_email} successfully!")
        else:
            st.error("Please select an email and enter a message before sending.")



def main():
    if not st.session_state.is_user_logged_in:
        page = st.sidebar.selectbox("Select Page", ["User Login", "Admin Login"])
    else:
        page = st.session_state.page if 'page' in st.session_state else "User Login"

    if page == "User Login":
        if not st.session_state.is_user_logged_in:
            user_login()
        else:
            user_request_form()
    elif page == "Admin Login":
        if not st.session_state.is_admin:
            admin_login()
        else:
            admin_dashboard()


if __name__ == "__main__":
    main()
