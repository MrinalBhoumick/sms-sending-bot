from datetime import datetime
import csv
import os
from dotenv import load_dotenv
from twilio.rest import Client
import time

# Load environment variables from .env file
load_dotenv()

# SMS configuration
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')
CSV_FILE = 'recipients.csv'
CUSTOM_MESSAGE_FILE = 'message.txt'
FLAG_FILE = 'script_executed.flag'

# Initialize Twilio client
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Function to read recipient phone numbers and names from CSV file
def read_recipients_from_csv(file_path):
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)
        recipients = [(row['phone_number'], row['name']) for row in reader]
    return recipients

# Function to read custom message from text file
def read_custom_message(file_path):
    with open(file_path, 'r') as file:
        message = file.read()
    return message

# Function to create SMS message with custom content
def create_sms_message(custom_message, recipient_name):
    today = datetime.today().strftime("%Y-%m-%d")
    message = f"Dear {recipient_name} Arrest Warrant has been generated,\n\n"
    message += custom_message
    return message

# Function to send SMS
def send_sms(recipient_phone, recipient_name, custom_message):
    message = create_sms_message(custom_message, recipient_name)

    try:
        # Send SMS using Twilio
        client.messages.create(
            body=message,
            from_=TWILIO_PHONE_NUMBER,
            to=recipient_phone
        )
        print(f"SMS sent successfully to {recipient_name} ({recipient_phone}).")
    except Exception as e:
        print(f"Failed to send SMS to {recipient_name} ({recipient_phone}): {e}")

# Function to send daily SMS report
def send_daily_report():
    start_time = datetime.now()
    recipients = read_recipients_from_csv(CSV_FILE)
    custom_message = read_custom_message(CUSTOM_MESSAGE_FILE)

    # Send SMS to each recipient
    for recipient_phone, recipient_name in recipients:
        send_sms(recipient_phone, recipient_name, custom_message)
        time.sleep(5)  # Wait for 5 seconds before sending the next SMS

    # Calculate duration
    duration = datetime.now() - start_time
    print(f"Script executed for {duration} seconds.")

# Main script logic
def main():
    # Check if the script has already been executed today
    if not os.path.exists(FLAG_FILE):
        # Run the daily report
        send_daily_report()

        # Create the flag file to indicate that the script has been executed
        with open(FLAG_FILE, 'w') as f:
            f.write(f"Script executed on {datetime.now()}")

        print("Script execution completed.")
    else:
        print("Script has already been executed today.")

if __name__ == "__main__":
    main()
