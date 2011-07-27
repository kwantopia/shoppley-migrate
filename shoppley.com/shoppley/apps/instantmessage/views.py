from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from tropo import Tropo, Result

@csrf_exempt
def index(request):
	t = Tropo()
	t.call(to = "yod@shoppley.com", _from = "shoppley@tropo.im", channel = "TEXT", network = "JABBER")
	t.ask(choices = "yes(yes,y,1), no(no,n,2)", timeout=60, name="reminder", say = "Hey, did you remember to take your pills?")	
	t.on(event = "continue", next ="verify_yes")
	t.on(event = "incomplete", next ="verify_no")
	json = t.RenderJson()
	print json
	return HttpResponse(json)

@csrf_exempt
def verify_yes(request):
	r = Result(request.body)
	t = Tropo()

	answer = r.getValue()

	t.say("You said " + str(answer))

	if answer == "yes" :
		t.say("Ok, just checkin.")
	else :
		t.say("What are you waiting for?")

	json = t.RenderJson()
	print json
	return HttpResponse(json)

@csrf_exempt
def verify_no(request):
	t = Tropo()
	t.say("Sorry, that wasn't on of the options.")
	json = t.RenderJson()
	print json
	return HttpResponse(json)
	