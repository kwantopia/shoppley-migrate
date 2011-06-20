from celery.decorators import task, periodic_task
from shoppleyuser.models import *
from offer.management.commands.check_sms import Command
@task
def add(x, y):
		print x+y
		return x + y


@periodic_task(run_every=timedelta(seconds=3))
def every_3_seconds():
		print("Running periodic task!")

@periodic_task(run_every=timedelta(minutes=1))
def process_sms():
		print("Running 1-minute task...\n")
		cmd = Command()
		cmd.handle_noargs()
