from flask_mail import Mail, Message
import os

mail_settings = {
    "MAIL_SERVER": 'smtp.gmail.com',
    "MAIL_PORT": 465,
    "MAIL_USE_TLS": False,
    "MAIL_USE_SSL": True,
    "MAIL_USERNAME": os.environ['EMAIL_USER'],
    "MAIL_PASSWORD": os.environ['EMAIL_PASSWORD']
}




def sendEmail(app, email, password, time):
    app.config.update(mail_settings)
    mail = Mail(app)
    with app.app_context():

        msg = Message(subject="This is a test",
                      sender=app.config.get("MAIL_USERNAME"),
                      recipients=[email], # replace with your email for testing
                      body=f"Hello!\n\nIT'S HECKIN' ROOM SELECTION TIME BABY!\n\nYour selection time is: {time}.\n\nYour password is: {password}\nDO NOT SHARE THIS.\n\nYou will be able to select your room at: http://room-allocation.herokuapp.com when your time comes around.\n\n Bye.")
        mail.send(msg)