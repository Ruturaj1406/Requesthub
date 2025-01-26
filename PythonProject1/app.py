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

    items_with_empty = [""] + [item["particular"] for item in ITEMS_LIST]  

    item = st.selectbox("Select an Item", items_with_empty, index=0)  # Default to the empty box

    quantity = st.number_input("Enter Quantity", min_value=1)

    if st.button("Submit Request"):
       
        if not user_name.strip():
            st.error("Please enter your name.")
        elif not item:  
            st.error("Please select an item before submitting the request.")
        else:
           
            insert_request(user_name, user_email, f"Item: {item}, Quantity: {quantity}")

           
            request_details = {
                "name": user_name,
                "email": user_email,
                "description": f"Item: {item}, Quantity: {quantity}"  
            }
            subject = "Request Submission"
            body = f"Request details:\nName: {user_name}\nItem: {item}\nQuantity: {quantity}"
            send_email(user_email, "System", request_details, subject, body)

            
            st.success("Your request has been submitted successfully!")

            st.session_state.request_submitted = True

    
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
  
    st.title("Admin Dashboard")

   
    requests = get_all_requests()
    if requests:
        for req in requests:
            # Access fields from the database response
            req_id = req['id']
            emp_id = req['emp_id'] if 'emp_id' in req else 'N/A'
            email = req['email']
            description = req['description']
            status = req['status']

            
            st.write(f"Request ID: {req_id} | Emp ID: {emp_id} | Email: {email} | Description: {description} | Status: {status}")

            
            status_update = st.radio(
                f"Update Status for Request {req_id}",
                ["Pending", "Approved", "Rejected"],
                index=["Pending", "Approved", "Rejected"].index(status),
                key=f"status_{req_id}",
            )

            
            if st.button(f"Update Status {req_id}", key=f"update_{req_id}"):
                update_request_status(req_id, status_update)
                subject = f"Request {status_update.capitalize()}"
                body = f"Your request has been {status_update.lower()}.\n\nRequest Details:\nDescription: {description}"
                send_email(email, "Admin", req, subject, body)
                st.success(f"Status for Request {req_id} updated and email sent!")

            
            if st.button(f"Delete Request {req_id}", key=f"delete_{req_id}"):
                delete_request(req_id)
                st.success(f"Request ID {req_id} deleted!")

        st.write("---")
    else:
        st.info("No requests available.")

   
    st.subheader("Send Message to User")
    user_emails = [req['email'] for req in requests if req['email']]  
    selected_email = st.selectbox("Select User Email", [""] + list(set(user_emails)))

    message_content = st.text_area("Enter your message", height=150)

    if st.button("Send Message"):
        if selected_email and message_content.strip():
            subject = "Message from Admin"
            body = f"{message_content}"  
            request_details = {
                "name": "User",  
                "email": selected_email,
                "description": "Admin Message"
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
