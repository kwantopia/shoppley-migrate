from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from api import BuxferInterface 
from datetime import date, datetime, timedelta
from common.helpers import JSONHttpResponse

@login_required
def load_trans(request):
    """
        Loads Buxfer data given email and password
        
        :param POST['email']:
        :param POST['password']:
    
        :rtype: JSON

        ::

            # successful loading
            {'result':'1'}
            # not a valid form
            {'result':'0'}
            # need to be POST
            {'result':'-1'}
        
    """
        
    if request.method == 'POST':
        u = request.user
        
        form = BuxferLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['email']
            password = form.cleaned_data['password']

            b = BuxferInterface()

            # pass username and password
            if b.buxfer_login(username, password):
            
                accts = b.get_accounts()
                for a in accts:
                    acct, created = Account.objects.get_or_create(user=u.otnuser, account_id=a['id'], name=a['name'], balance=a['balance'])
                    acct.save()
                    
                    final = 1 
                    p = 1   # page number
                    while final != 0:  
                        txns, final, total = b.get_transactions(a['id'], page=p)
                        # TODO: iterate through txns and insert into model
                        for t in txns:
                            m, created = Memo.objects.get_or_create(txt=t['description'])
                            m.save()
                            
                            trans, created = Transaction.objects.get_or_create(account=acct, amount="%.2f"%t['amount'], purchase_date=datetime.strptime(t['date']+" "+str(date.today().year), '%d %b %Y'), memo=m, transaction_id=t['id'])
                            trans.save()

                            r, created = Receipt.objects.get_or_create(txn=trans)
                            r.save()
                            
                        p += 1    # if no transactions are on page, then filter = len(response["transactions"]) = 0

                return JSONHttpResponse({'result':'1'})
        else:
            return JSONHttpResponse({'result':'0', 'error': form.errors})
    return JSONHttpResponse({'result':'-1', 'error':'Incorrect username or password.'})


