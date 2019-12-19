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
    collegeName = "Baxter"
    app.config.update(mail_settings)
    mail = Mail(app)
    with app.app_context():

        msg = Message(subject="This is a test",
                      sender=app.config.get("MAIL_USERNAME"),
                      recipients=[email],
                      body=f"Hello {collegeName} Resident!\n\nIt is time for you to select your room for next year! Instructions are included on the following link, but there are a few important things to keep in mind:\n\t1. The room you select is not 100% gaurenteed. There may be some changes made to the room allocations.\n\t2. You will only be able to submit your preferences AFTER your start time (see below). You will have about 1 week to complete this form. You can hold off submitting if you want to wait for a friend.\n\t3. If you have the same room points as someone else, they will have the same start time as you.\n\t4. You can send your password (which you need to submit your preferences) to a friend if you will be unvaliable for your time slot.\n\nYour start time is:\n\t{time}\n\nYour password is:\n\t{password}\n\nWhen your start time comes arround, wou will be able to select your room at:\n\thttp://room-allocation.herokuapp.com\n\nIf you have any issues at all, please message Tom Wright straight away! This is a trial run, Tom Hill, Rohan and I have all our fingers crossed that this works!\n\nGood luck!"
                    )
        
        mail.send(msg)