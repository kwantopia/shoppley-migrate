from celery.decorators import task
from shoppleyuser.models import *

@task
def add(x, y):
    return x + y

