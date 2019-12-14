import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


def send_message(email, name, time, password):

    message = Mail(
        from_email="from_email@example.com",
        to_emails=email,
        subject="Baxter College Room Allocation",
        html_content=f"<strong>BABY IT IS ROOM SELECTION TIME!!! YEET!</strong><br><p>Your time is: {str(time)}</p><p>Your password is: {password}</p><p>Do not share that.</p><p>You can log onto the room selection portal here: http://room-allocation.herokuapp.com</p>",
    )

    try:
        # HACK: Need to pu this in an environment variable but cbf.
        sg = SendGridAPIClient("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")
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(str(e))

# send_message('z55@mailinator.com', "z55", "TIME", "password")