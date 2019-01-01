from flask import render_template, current_app
from flask.ext.mail import Message
from threading import Thread
from . import mail

class Email:
	@staticmethod
	def sendAsyncEmail(app, msg):
		with app.app_context():
			mail.send(msg)
		print "message sent!"

	@staticmethod
	def sendEmail(to, subject, template, **kwargs):
		app = current_app._get_current_object()
		msg = Message(app.config['QUIZ_MAIL_SUBJECT_PREFIX'] + subject,
			sender=app.config['QUIZ_MAIL_SENDER'], recipients=to)
		msg.body = render_template(template + '.txt', **kwargs)
		msg.html = render_template(template + '.html', **kwargs)
		thr = Thread(target=Email.sendAsyncEmail, args=[app, msg])
		thr.start()
		return thr


