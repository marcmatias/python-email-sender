# For guessing MIME type based on file name extension
import argparse
from email.message import EmailMessage
import mimetypes
import os
import smtplib

from signal import signal, SIGINT
from sys import exit

from csv_reader import return_total_hours
from download_reports import download_reports

def parser_args(arguments):
    parser = argparse.ArgumentParser()
    for arg in arguments:
        parser.add_argument(
                arg['name'],
                dest=arg['dest'],
                type=arg['type'],
                help=arg['help']
                )
    return parser.parse_args()

def handler(signal_received, frame):
    # Handle any cleanup here
    print(' Exiting gracefully')
    exit(0)

def send_mail(password, args, email_body):
    msg = EmailMessage()
    msg['Subject'] = args.email_subject
    msg['From'] = args.email_from
    msg['To'] = args.email_to
    msg.add_header('Content-Type', 'text/html')
    msg.set_payload(email_body)

    if args.attachments_directory:
        for filename in os.listdir(args.attachments_directory):
            path = os.path.join(args.attachments_directory, filename)
            if not os.path.isfile(path):
                continue
            # Guess the content type based on the file's extension.  Encoding
            # will be ignored, although we should check for simple things like
            # gzip'd or compressed files.
            ctype, encoding = mimetypes.guess_type(path)
            if ctype is None or encoding is not None:
                # No guess could be made, or the file is encoded (compressed), so
                # use a generic bag-of-bits type.
                ctype = 'application/octet-stream'
            maintype, subtype = ctype.split('/', 1)
            with open(path, 'rb') as fp:
                msg.add_attachment(fp.read(),
                                   maintype=maintype,
                                   subtype=subtype,
                                   filename=filename)

    s = smtplib.SMTP('smtp.gmail.com: 587')
    s.starttls()
    try:
        # Login Credetials for sending the mail
        s.login(msg['From'], password)
    except Exception as e:
        print(e)

    print('Sending email')
    s.sendmail(msg['From'], [msg['To']], msg.as_string().encode('utf-8'))
    print('Email successfully sent!')

def main(args):
    # Erasing old reports and downloading new versions
    download_reports(args.email_from, args.password_toggl)

    total_hours_worked = return_total_hours()

    # Capture SIGINT or CTRL-C
    signal(SIGINT, handler)
    with open('password.txt', 'r') as file:
        password = file.read().rstrip()
    with open('email-body.txt', 'r') as file:
        mail_body = file.read().replace('\n', '<br>').replace('total_hours_worked', total_hours_worked)

    send_mail(password, args, mail_body)

if __name__ == "__main__":
    args = parser_args([
        {
            'name': '--subject',
            'dest': 'email_subject',
            'type': str,
            'help': 'email subject'
            },
        {
            'name': '--to',
            'dest': 'email_to',
            'type': str,
            'help': 'email to send'
            },
        {
            'name': '--from',
            'dest': 'email_from',
            'type': str,
            'help': 'email from'
            },
        {
            'name': '--attachments',
            'dest': 'attachments_directory',
            'type': str,
            'help': 'attachments directory'
            },
        {
            'name': '--password_toggl',
            'dest': 'password_toggl',
            'type': str,
            'help': 'password Toggl to download reports'
            },
        ]
    )
    main(args)
