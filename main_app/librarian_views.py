import json
import requests
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, JsonResponse
from django.shortcuts import (HttpResponse, HttpResponseRedirect,
                              get_object_or_404, redirect, render)
from django.templatetags.static import static
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import UpdateView

from .forms import *
from .models import *

from django.shortcuts import render,redirect
from .models import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.utils import timezone
import datetime
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib import auth

from django.conf import settings


# student information

def student_page(request):
    student=Student.objects.all()
    context = {
        'page_title': "Manage Student",
        'student': student,

    }
    return render(request,'library/student_page.html',context)


def home_page(request):
    student=Student.objects.all()
    context = {
        'page_title': "Manage Student",
        'student': student,

    }
    return render(request,'library/home_content.html',context)


#  ISSUES


#  FINES

@login_required(login_url='login_page')
# @user_passes_test(lambda u: not u.is_superuser ,login_url='/student/login/')
def myfines(request):
    if Student.objects.filter(student_id=request.user):
        student=Student.objects.filter(student_id=request.user)[0]
        fines=Fine.objects.filter(student=student)
        return render(request,'library/myfines.html',{'fines':fines})
    messages.error(request,'You are Not a Student !')
    return redirect('library/home')


@login_required(login_url='login_page')
# @user_passes_test(lambda u:  u.is_superuser ,login_url='/admin/')
def all_fines(request):
    issues=Fine.objects.all()
    context={
        "issues":issues,
        'page_title': 'All Fines'

    }
    return render(request,"library/student_fine.html",context)

def allfines(request):
    issues=Issue.objects.all()
    for issue in issues:
        calcFine(issue)
    return redirect('library/fine/')


import razorpay
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

@login_required(login_url='login_page')
@user_passes_test(lambda u: not u.is_superuser ,login_url='login_page')
def payfine(request,fineID):
    fine=Fine.objects.get(id=fineID)
    order_amount = int(fine.amount)*100
    order_currency = 'INR'
    order_receipt = fine.order_id
    
    
    razorpay_order=razorpay_client.order.create(dict(amount=order_amount, currency=order_currency, receipt=order_receipt, ))
    print(razorpay_order)
    
    
    return render(request,'library/payfine.html',
    {'amount':order_amount,'razor_id':settings.RAZORPAY_KEY_ID,
    'reciept':razorpay_order['id'],
    'amount_displayed':order_amount / 100,
    'address':'a custom address',
    'fine':fine, 
    })


@login_required(login_url='login_page')
@user_passes_test(lambda u: not u.is_superuser ,login_url='login_page')
def pay_status(request,fineID):
    if request.method == 'POST':
        params_dict={
            'razorpay_payment_id':request.POST['razorpay_payment_id'],
            'razorpay_order_id':request.POST['razorpay_order_id'],
            'razorpay_signature':request.POST['razorpay_signature'],
        }
        try:
            status=razorpay_client.utility.verify_payment_signature(params_dict)
            if status is None:
                fine=Fine.objects.get(id=fineID)
                fine.paid=True
                fine.datetime_of_payment=timezone.now()
                fine.razorpay_payment_id=request.POST['razorpay_payment_id']
                fine.razorpay_signature=request.POST['razorpay_signature']
                fine.razorpay_order_id = request.POST['razorpay_order_id']
                fine.save()
                
            messages.success(request,'Payment Succesfull')
        except:
            messages.error(request,'Payment Failure')
    return redirect('my-fines')