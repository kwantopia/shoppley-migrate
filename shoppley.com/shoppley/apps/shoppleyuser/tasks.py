from celery.decorators import task, periodic_task
from celery.task.schedules import crontab
from datetime import timedelta

#@periodic_task(run_every=timedelta(seconds=3))
#def run_every_three():
                #from offer.management.commands.check_sms import Command
#                print("Running 3-second task...\n")
                #cmd = Command()
                #cmd.handle_noargs()

@periodic_task(run_every=timedelta(minutes=1))
def process_sms():
		from offer.management.commands.check_sms import Command
		print("Running 1-minute task...\n")
		cmd = Command()
		cmd.handle_noargs()

@periodic_task(run_every=crontab(hour=7, minute=0))
def reset_offer_count():
		from offer.management.commands.reset_offer_counts import Command
		cmd = Command()
		cmd.handle_noargs()

@periodic_task(run_every=crontab())
def send_mail():
		from mailer.management.commands.send_mail import Command
		cmd = Command()
		cmd.handle_noargs()
		

@periodic_task(run_every=crontab())
def emit_notices():
		from notification.management.commands.emit_notices import Command
		cmd = Command()
		cmd.handle_noargs()

@periodic_task(run_every=crontab(minute="*/20"))
def retry_deferred():
		from mailer.management.commands.retry_deferred import Command
		cmd = Command()
		cmd.handle_noargs()
