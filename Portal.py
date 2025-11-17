# Imports
import streamlit as st
import pandas as pd
import mysql.connector
import hashlib
from datetime import datetime

# ---------------------------
# MySQL Connection
# ---------------------------
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Aqibo612@",
        database="aqi_query"
    )

# ---------------------------
# Password Hashing
# ---------------------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ---------------------------
# Sample Users
# ---------------------------
users = {
    "client@user": {
        "hashed_password": hash_password("client_123"),
        "role": "Client"
    },
    "support@user": {
        "hashed_password": hash_password("support_123"),
        "role": "Support"
    }
}

# ---------------------------
# Session State Initialization
# ---------------------------
if "role" not in st.session_state:
    st.session_state["role"] = None

# ---------------------------
# Page Config & Styling
# ---------------------------
st.set_page_config(page_title="Client Query Management System", layout="wide")

st.markdown("""
    <style>
        body {
            background-color: #f0f4f8;
            font-family: 'Segoe UI', sans-serif;
        }
        h1, h2, h3 {
            color: #1F4E79;
        }
        .stButton>button {
            background-color: #1F4E79;
            color: white;
            border-radius: 5px;
        }
        .stTextInput>div>input, .stTextArea>div>textarea {
            background-color: #f9fbfc;
        }
    </style>
""", unsafe_allow_html=True)

# ---------------------------
# Login Page
# ---------------------------
if st.session_state["role"] is None:
    st.markdown("<h1 style='text-align: center;'>Client Query Management System</h1>", unsafe_allow_html=True)
    st.subheader("🔐 Login Page")

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        role = st.selectbox("Role", ["Client", "Support"])
        login_btn = st.form_submit_button("Login")

    if login_btn:
        if username in users:
            hashed_pw = hash_password(password)
            if hashed_pw == users[username]["hashed_password"] and role == users[username]["role"]:
                st.session_state["role"] = role
                st.success(f"Welcome {username}! You are logged in as {role}.")
                st.rerun()
            else:
                st.error("Invalid password or role.")
        else:
            st.error("User not found.")

# ---------------------------
# Client Submission Page
# ---------------------------
elif st.session_state["role"] == "Client":
    st.sidebar.title("📋 Navigation")
    page = st.sidebar.radio("Choose Page", ["📩 Client Submission Page", "🚪 Logout"])

    if page == "📩 Client Submission Page":
        st.markdown("<h2>Submit a Query</h2>", unsafe_allow_html=True)
        with st.form("client_form"):
            email = st.text_input("Email ID")
            mobile = st.text_input("Mobile Number")
            heading = st.text_input("Query Heading")
            description = st.text_area("Query Description")
            submit_btn = st.form_submit_button("Submit Query")

        if submit_btn:
            try:
                conn = get_connection()
                cursor = conn.cursor()

                # Generate query_id like Q001, Q002...
                cursor.execute("SELECT COUNT(*) FROM queries")
                count = cursor.fetchone()[0]
                query_id = f"Q{count + 1:03d}"

                insert_query = """
                    INSERT INTO queries (query_id, client_email, client_mobile, query_heading, query_description, status, date_issued)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                data = (query_id, email, mobile, heading, description, "Open", datetime.now().date())
                cursor.execute(insert_query, data)
                conn.commit()
                conn.close()

                st.success(f"✅ Query {query_id} submitted successfully!")
            except Exception as e:
                st.error(f"❌ Failed to submit query: {e}")

    elif page == "🚪 Logout":
        st.session_state["role"] = None
        st.rerun()

# ---------------------------
# Support Dashboard
# ---------------------------
elif st.session_state["role"] == "Support":
    st.sidebar.title("📋 Navigation")
    page = st.sidebar.radio("Choose Page", ["🛠️ Support Dashboard", "🚪 Logout"])

    if page == "🛠️ Support Dashboard":
        st.markdown("<h2>Support Dashboard</h2>", unsafe_allow_html=True)

        try:
            conn = get_connection()
            query = "SELECT * FROM queries"
            df = pd.read_sql(query, conn)
            conn.close()

            st.dataframe(df)

            status_filter = st.selectbox("Filter by Status", ["All", "Open", "Closed"])
            if status_filter != "All":
                st.dataframe(df[df["status"] == status_filter])

            query_id = st.text_input("Enter Query ID to close (e.g., Q001)")
            if st.button("Close Query"):
                try:
                    conn = get_connection()
                    cursor = conn.cursor()

                    update_query = """
                        UPDATE queries
                        SET status = 'Closed', date_closed = %s
                        WHERE query_id = %s AND status = 'Open'
                    """
                    cursor.execute(update_query, (datetime.now().date(), query_id))
                    conn.commit()
                    conn.close()

                    st.success(f"✅ Query {query_id} closed successfully!")
                except Exception as e:
                    st.error(f"❌ Failed to close query: {e}")
        except Exception as e:
            st.error(f"❌ Failed to load queries: {e}")

    elif page == "🚪 Logout":
        st.session_state["role"] = None
        st.rerun()






































