import streamlit as st
import mysql.connector
from datetime import datetime

# Establish MySQL database connection
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="abhinav",
        database="sports_team_db"
    )

# Initialize session state for login
if 'is_logged_in' not in st.session_state:
    st.session_state.is_logged_in = False
if 'user_type' not in st.session_state:
    st.session_state.user_type = None

# Function to display login page
def login_page():
    st.title("Sports Team Management System")
    if not st.session_state.is_logged_in:
        user_type = st.selectbox("Login as:", ["Coach", "Player"])
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        login_button = st.button("Login")

        if login_button:
            conn = get_connection()
            cursor = conn.cursor()
            if user_type == "Coach":
                cursor.execute("SELECT * FROM coaches WHERE username = %s AND password = %s", (username, password))
            else:
                cursor.execute("SELECT * FROM players WHERE username = %s AND password = %s", (username, password))

            user = cursor.fetchone()
            conn.close()

            if user:
                st.session_state.is_logged_in = True
                st.session_state.user_type = user_type
                st.session_state.username = username
                st.success(f"Welcome, {username}!")
                if user_type == "Coach":
                    coach_dashboard()
                else:
                    player_dashboard()
            else:
                st.error("Invalid username or password.")
    else:
        if st.session_state.user_type == "Coach":
            coach_dashboard()
        else:
            player_dashboard()

def coach_dashboard():
    st.header("Coach Dashboard")
    
    menu = ["Schedule Match/Training", "View Matches/Training", "Add/Remove Player", "View Full Roster", "Update Injury Status", "View Injuries", "Logout"]
    choice = st.selectbox("Select an option:", menu)

    conn = get_connection()
    cursor = conn.cursor()

    if choice == "Schedule Match/Training":
        st.subheader("Schedule a Match or Training Session")
        event_type = st.selectbox("Type", ["Match", "Training"])
        event_date = st.date_input("Date")
        event_time = st.time_input("Time")
        opponents = None

        if event_type == "Match":
            opponents = st.text_input("Opponents")
            if not opponents:
                st.error("Please enter the name of the opponents for the match.")
        
        if st.button("Schedule"):
            if event_type == "Match" and not opponents:
                st.error("Opponents field is required for matches.")
            else:
                cursor.execute("""
                    INSERT INTO matches (event_type, event_date, event_time, opponents) 
                    VALUES (%s, %s, %s, %s)
                """, (event_type, event_date, event_time, opponents))
                conn.commit()
                st.success("Event scheduled successfully!")
    elif choice == "View Matches/Training":
        st.subheader("View or Remove Scheduled Events")
        cursor.execute("SELECT id, event_type, event_date, event_time, opponents FROM matches")
        events = cursor.fetchall()
        if events:
            for event in events:
                event_id, event_type, event_date, event_time, opponents = event
                opponents_info = f", Opponents: {opponents}" if opponents else ""
                st.write(f"Type: {event_type}, Date: {event_date}, Time: {event_time}{opponents_info}")
                
                if st.button(f"Delete", key=event_id):
                    cursor.execute("DELETE FROM matches WHERE id = %s", (event_id,))
                    conn.commit()
                    st.success(f"Event ID {event_id} removed successfully!")
                    st.experimental_rerun()  # Refresh the list of events after deletion
        else:
            st.write("No scheduled events found.")

    elif choice == "Add/Remove Player":
        st.subheader("Add or Remove Players")
        action = st.selectbox("Action", ["Add", "Remove"])
        player_username = st.text_input("Player Username")
        position = st.selectbox("Position", ["Forward", "Midfielder", "Defender", "Goalkeeper"])
        player_password = st.text_input("Player Password")  # Add password input

        if action == "Add" and st.button("Add Player"):
            cursor.execute("INSERT INTO players (username, password, position) VALUES (%s, %s, %s)", 
                           (player_username, player_password, position))
            conn.commit()
            st.success("Player added successfully!")
        elif action == "Remove" and st.button("Remove Player"):
            cursor.execute("DELETE FROM players WHERE username = %s", (player_username,))
            conn.commit()
            st.success("Player removed successfully!")

    elif choice == "View Full Roster":
        st.subheader("Full Roster")
        cursor.execute("""
            SELECT p.username, p.position, i.injury_name 
            FROM players p 
            LEFT JOIN injuries i ON p.id = i.player_id
        """)
        rows = cursor.fetchall()
        for row in rows:
            username, position, injury_name = row
            status = "Injured" if injury_name else "Healthy"
            st.write(f"Name: {username.upper()},\tPosition: {position},\tStatus: {status}")
            
    elif choice == "Update Injury Status":
        st.subheader("Update Player Injury Status")
        action = st.selectbox("Action", ["Add/Update Injury", "Remove Injury"])
        player_username = st.text_input("Player Username")

        if action == "Add/Update Injury":
            injury_name = st.text_input("Injury Name")
            recovery_time = st.number_input("Estimated Time for Recovery (in weeks)", min_value=1, step=1)
            if st.button("Add/Update Injury"):
                try:
                    cursor.execute("SELECT id FROM players WHERE username = %s", (player_username,))
                    player = cursor.fetchone()
                    if player:
                        player_id = player[0]
                        cursor.execute("""
                            INSERT INTO injuries (player_id, player_username, injury_name, recovery_time) 
                            VALUES (%s, %s, %s, %s)
                            ON DUPLICATE KEY UPDATE 
                            injury_name = VALUES(injury_name), recovery_time = VALUES(recovery_time)
                        """, (player_id, player_username, injury_name, recovery_time))
                        conn.commit()
                        st.success("Injury status updated successfully!")
                    else:
                        st.error("Player not found!")
                except mysql.connector.Error as err:
                    st.error(f"Error: {err}")

        elif action == "Remove Injury":
            if st.button("Remove Injury"):
                cursor.execute("SELECT id FROM players WHERE username = %s", (player_username,))
                player = cursor.fetchone()
                if player:
                    cursor.execute("DELETE FROM injuries WHERE player_username = %s", (player_username,))
                    conn.commit()
                    st.success("Injury removed successfully!")
                else:
                    st.error("Player not found or no injury associated with the player.")


    elif choice == "View Injuries":
        st.subheader("View Injuries")
        cursor.execute("SELECT player_username, injury_name, recovery_time FROM injuries")
        injuries = cursor.fetchall()
        if injuries:
            for injury in injuries:
                st.write(f"Player: {injury[0].upper()}, Injury: {injury[1]}, Estimated Recovery Time: {injury[2]} weeks")
        else:
            st.write("No injuries reported.")
    elif choice == "Logout":
        st.session_state.is_logged_in = False
        st.session_state.user_type = None
        st.session_state.username = None
        st.success("You have been logged out. Please refresh the page to log in again.")
        st.stop()  # Stops the execution of the script here

    
    conn.close()


# Player's dashboard
def player_dashboard():
    st.header("Player Dashboard")
    
    menu = ["View Scheduled Matches", "View Training Sessions", "View Full Roster", "Logout"]
    choice = st.selectbox("Select an option:", menu)

    conn = get_connection()
    cursor = conn.cursor()

    if choice == "View Scheduled Matches":
        st.subheader("Scheduled Matches")
        cursor.execute("SELECT event_date, event_time, opponents FROM matches WHERE event_type = 'Match'")
        matches = cursor.fetchall()
        if matches:
            for match in matches:
                st.write(f"Date: {match[0]}, Time: {match[1]}, Opponents: {match[2]}")
        else:
            st.write("No scheduled matches.")

    elif choice == "View Training Sessions":
        st.subheader("Training Sessions")
        cursor.execute("SELECT event_date, event_time FROM matches WHERE event_type = 'Training'")
        trainings = cursor.fetchall()
        if trainings:
            for training in trainings:
                st.write(f"Date: {training[0]}, Time: {training[1]}")
        else:
            st.write("No scheduled training sessions.")

    elif choice == "View Full Roster":
        st.subheader("Full Team Roster")
        cursor.execute("""
            SELECT p.username, p.position, i.injury_name 
            FROM players p 
            LEFT JOIN injuries i ON p.id = i.player_id
        """)
        rows = cursor.fetchall()
        for row in rows:
            username, position, injury_name = row
            status = "Injured" if injury_name else "Healthy"
            st.write(f"Name: {username.upper()},\tPosition: {position},\tStatus: {status}")

    elif choice == "Logout":
        st.session_state.is_logged_in = False
        st.session_state.user_type = None
        st.session_state.username = None
        st.success("You have been logged out.")
        st.stop()

    conn.close()


# Main entry point
login_page()
