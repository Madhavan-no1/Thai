from flask import Flask, render_template, request, redirect, url_for, flash
import json
import schedule
import time
import winsound
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Set a secret key for session management

SCOPES = ['https://www.googleapis.com/auth/calendar']

def create_event(summary, description, start_time, end_time, location):
    creds = None
    try:
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    except Exception as e:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('calendar', 'v3', credentials=creds)

    event = {
        'summary': summary,
        'location': location,
        'description': description,
        'start': {
            'dateTime': start_time,
            'timeZone': 'Asia/Kolkata',
        },
        'end': {
            'dateTime': end_time,
            'timeZone': 'Asia/Kolkata',
        },
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'email', 'minutes': 10},
                {'method': 'popup', 'minutes': 10},
            ],
        },
    }

    event_result = service.events().insert(calendarId='primary', body=event).execute()
    print(f"Event created: {event_result.get('htmlLink')}")
    return event_result.get('htmlLink')  # Return the event link

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/set_reminder', methods=['POST'])
def set_reminder():
    summary = "Pill Reminder"
    description = request.form['description']
    date_input = request.form['date']
    time_input = request.form['time']

    # Combine date and time for medication time
    medication_time = datetime.strptime(f"{date_input} {time_input}", "%Y-%m-%d %I:%M %p")
    medication_end_time = medication_time + timedelta(hours=1)

    start_time_iso = medication_time.isoformat()
    end_time_iso = medication_end_time.isoformat()

    # Create the event
    create_event(summary, description, start_time_iso, end_time_iso, "Home")
    
    # Flash a confirmation message
    flash('Event created successfully!', 'success')

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
