# Email-sender

This is an python script to send emails with attachments automatically.

## Run script

You will need to set a `password.txt` and a `email-body.txt` in root project folder to run this script.

Notice that `email-body.txt` should have a text like `total_hours_worked` to be replaced with csv total hours worked value.

```bash
python email-sender.py \
    --from example@example.com \
    --to example2@example.com \
    --attachments attachments \
    --password_toggl example123
```
