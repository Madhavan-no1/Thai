import json
import schedule
import time
import winsound  # For Windows; use other libraries for different OS
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import speech_recognition as sr  # For voice input

SCOPES = ['https://www.googleapis.com/auth/calendar']

def create_event(summary, description, start_time, end_time, location):
    # Load credentials from token.json or create new credentials
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
            'timeZone': 'Asia/Kolkata',  # IST timezone
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

def format_time_12_hour(dt):
    return dt.strftime("%I:%M %p"), dt.strftime("%H:%M")  # Return both formats

def alarm():
    print("Time to take your medication!")
    winsound.Beep(440, 1000)  # Beep for 1 second

def schedule_alarm(alarm_time_24hr):
    schedule.every().day.at(alarm_time_24hr).do(alarm)

def voice_input(prompt):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print(prompt)
        audio = recognizer.listen(source)

    try:
        return recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        print("Sorry, I did not understand that.")
        return ""
    except sr.RequestError:
        print("Could not request results from Google Speech Recognition service.")
        return ""

# Predefined event details
summary = "Pill Reminder"
description = "Take your medication."
location = "Home"

# Get user input for medication time
input_method = input("Do you want to enter details via voice or text? (voice/text): ").strip().lower()

if input_method == 'voice':
    time_input = voice_input("Please say the medication time in format 'YYYY-MM-DD HH:MM AM/PM':")
else:
    time_input = input("Enter the medication time (YYYY-MM-DD HH:MM AM/PM): ")

# Parse the medication time
medication_time = datetime.strptime(time_input, "%Y-%m-%d %I:%M %p")  # Example: "2024-10-05 05:35 PM"
medication_end_time = medication_time + timedelta(hours=1)  # 1 hour duration

# Format the start and end time in ISO format for Google Calendar
start_time_iso = medication_time.isoformat()
end_time_iso = medication_end_time.isoformat()

# Create the event
create_event(summary, description, start_time_iso, end_time_iso, location)

# Schedule the alarm in both formats
formatted_alarm_time_12hr, formatted_alarm_time_24hr = format_time_12_hour(medication_time)
schedule_alarm(formatted_alarm_time_24hr)

# Run the scheduling loop
while True:
    schedule.run_pending()
    time.sleep(1)
