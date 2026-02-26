import os
import csv
import re
import datetime
import calendar
import base64
import google_auth_oauthlib.flow
from google.oauth2 import service_account
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# Gmail API setup
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
CREDENTIALS_FILE = 'credentials.json'
CSV_FILE = 'transactions_master.csv'
TOKEN_FILE = 'token.json'

def authenticate_gmail():
    credentials = None
    # Load credentials from the token file if it exists
    if os.path.exists(TOKEN_FILE):
        credentials = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    
    # If there are no valid credentials, authenticate and save the token
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            credentials = flow.run_local_server(port=0)
            
            # Save the credentials for future use
            with open(TOKEN_FILE, 'w') as token_file:
                token_file.write(credentials.to_json())
    
    service = build('gmail', 'v1', credentials=credentials)
    return service


# def authenticate_gmail():
#     flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
#     credentials = flow.run_local_server(port=0)
#     service = build('gmail', 'v1', credentials=credentials)
#     return service

def get_date_range():
    # Prompt the user for month and year in a single line
    input_date = input("Enter the month and year (MM YYYY): ")
    month, year = map(int, input_date.split())
    
    # Define the start date as the 22nd of the chosen month
    start_date = datetime.datetime(year, month, 22)
    
    # Calculate the end date as the 23rd of the following month
    if month == 12:
        end_date = datetime.datetime(year + 1, 1, 23)
    else:
        end_date = datetime.datetime(year, month + 1, 23)
    
    # Format start and end dates as strings in the required format
    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")
    
    return start_date_str, end_date_str, month, year

def fetch_emails(service, start_date, end_date):
    # Convert dates to the YYYY/MM/DD format for the Gmail API
    start_date = start_date.replace("-", "/")
    end_date = end_date.replace("-", "/")
    
    query = f"subject:'PacifiCard: Consumos' after:{start_date} before:{end_date}"
    print(query)
    results = service.users().messages().list(userId='me', q=query).execute()
    
    # Debug: Print the result of email fetching
    if 'messages' in results:
        print(f"Found {len(results['messages'])} emails matching the date and subject criteria.")
    else:
        print("No emails found matching the date and subject criteria.")
        
    return results.get('messages', [])

def save_messages_to_file(messages, service, filename="email_messages.txt"):
    with open(filename, 'w', encoding='utf-8') as file:
        for i, message in enumerate(messages):
            msg = service.users().messages().get(userId='me', id=message['id'], format='full').execute()
            
            # Get the email payload parts
            if 'payload' in msg and 'parts' in msg['payload']:
                email_body = ""
                for part in msg['payload']['parts']:
                    if part['mimeType'] == 'text/plain' and 'data' in part['body']:
                        # Decode the base64 URL-encoded content
                        email_body += base64.urlsafe_b64decode(part['body']['data']).decode("utf-8")
                
                # Write email content to the file with a divider for each message
                file.write(f"Email {i+1}:\n")
                file.write(email_body + "\n")
                file.write("="*50 + "\n")  # Divider between messages
            else:
                file.write(f"Email {i+1}:\n")
                file.write("No body content found.\n")
                file.write("="*50 + "\n")  # Divider between messages

    print(f"All messages have been saved to {filename}")

def load_saved_messages(filename="email_messages.txt"):
    messages = []
    with open(filename, 'r', encoding='utf-8') as file:
        email_content = ""
        for line in file:
            # Identify the divider and save the email content when reached
            if line.strip() == "="*50:
                if email_content:
                    messages.append(email_content.strip())
                    email_content = ""
            else:
                email_content += line
        # Append the last message if there's no trailing divider
        if email_content:
            messages.append(email_content.strip())

    print(f"Loaded {len(messages)} messages from {filename}")
    return messages

def parse_transaction(email_content):
    date_pattern = re.compile(r'\*?Fecha de la transacción\*?\s*(\d{4}-\d{2}-\d{2} a las \d{2}:\d{2})')
    amount_pattern = re.compile(r'\*?Monto\*?\s*\$\s*(\d+\.\d{2})')

    
    date_match = date_pattern.search(email_content)
    amount_match = amount_pattern.search(email_content)
    
    if date_match and amount_match:
        date_str = date_match.group(1)
        amount = float(amount_match.group(1))
        date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d a las %H:%M')
        return date_obj, amount
    return None, None

def load_existing_transactions():
    existing_transactions = []
    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, mode='r') as file:
            reader = csv.reader(file)
            existing_transactions = [(datetime.datetime.strptime(row[0], '%Y-%m-%d %H:%M'), float(row[1])) for row in reader]
    return existing_transactions

def save_transaction(date, amount, month, year):
    # Create a filename based on the month and year
    month_name = calendar.month_name[month]
    filename = f"transactions_{month_name}_{year}_master.csv"
    
    # Check if the file exists; if not, create it with headers
    file_exists = os.path.isfile(filename)
    
    with open(filename, mode='a', newline='') as file:
        writer = csv.writer(file)
        
        # Write a header row if the file does not already exist
        if not file_exists:
            writer.writerow(["Date", "Amount"])
        
        # Write the transaction to the file
        writer.writerow([date.strftime('%Y-%m-%d %H:%M'), f"{amount:.2f}"])

def main():
    # Authenticate Gmail API
    service = authenticate_gmail()

    # Get date range and month/year for file naming
    start_date, end_date, month, year = get_date_range()
    print(start_date, end_date)

    # Fetch emails in specified date range
    messages = fetch_emails(service, start_date, end_date)
    
    # Load existing transactions for this month and year
    existing_transactions = load_existing_transactions()
    transactions = []
    total_amount = sum(amount for _, amount in existing_transactions)

    for message in messages:
        msg = service.users().messages().get(userId='me', id=message['id'], format='full').execute()
        
        # Decode the email body
        email_body = ""
        if 'payload' in msg and 'parts' in msg['payload']:
            for part in msg['payload']['parts']:
                if part['mimeType'] == 'text/plain' and 'data' in part['body']:
                    # Decode the base64 URL-encoded content
                    email_body += base64.urlsafe_b64decode(part['body']['data']).decode("utf-8")

        # Parse the email content for transactions
        transaction_date, transaction_amount = parse_transaction(email_body)
        print(transaction_date, transaction_amount)
        
        # Check for duplicates within the transactions list
        if transaction_date and transaction_amount:
            transaction_key = (transaction_date, transaction_amount)
            if transaction_key not in transactions:
                if transaction_key not in existing_transactions:
                    save_transaction(transaction_date, transaction_amount, month, year)
                    transactions.append(transaction_key)
                    total_amount += transaction_amount
                    
    # Display summary output without saving total to CSV
    print(f"\nSummary for {start_date} to {end_date}")
    print(f"Total Expenses Recorded: ${total_amount:.2f}")


if __name__ == '__main__':
    main()
