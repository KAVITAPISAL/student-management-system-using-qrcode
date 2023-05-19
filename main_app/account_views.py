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
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.utils import timezone
import datetime
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib import auth
from student_management_system import settings

def context_data():
    context = {
        'page_name' : '',
        'page_title' : 'Chat Room',
        'system_name' : 'Genba Sopanrao Moze College of Engineering, Balewadi',
        'topbar' : True,
        'footer' : True,
    }

    return context

@login_required
def student_list(request):
    context =context_data()
    context['page'] = 'student_list'
    context['page_title'] = 'student List'
    context['students'] = Student.objects.all()

    return render(request, 'student_list.html', context)




@login_required 
def manage_student(request):
    context =context_data()
    context['page'] = 'add_student'
    context['page_title'] = 'Add New student'
    context['students'] = Student.objects.all()
    return render(request, 'library/home_content.html', context)

@login_required
def save_student(request):
    resp = { 'status' : 'failed', 'msg' : '' }
    if not request.method == 'POST':
        resp['msg'] = "No data has been sent into the request."

    else:
        if request.POST['id'] == '':
            form = forms.SaveStudent(request.POST, request.FILES)
        else:
            student = Student.objects.get(id = request.POST['id'])
            form = forms.SaveStudent(request.POST, request.FILES, instance = student)
        if form.is_valid():
            form.save()
            if request.POST['id'] == '':
                messages.success(request, f"{request.POST['student_code']} has been added successfully.")
            else:
                messages.success(request, f"{request.POST['student_code']} has been updated successfully.")
            resp['status'] = 'success'
        else:
            for field in form:
                for error in field.errors:
                    if not resp['msg'] == '':
                        resp['msg'] += str("<br />")
                    resp['msg'] += str(f"[{field.label}] {error}")

    return HttpResponse(json.dumps(resp), content_type="application/json")

@login_required
def view_card(request, pk =None):
    if pk is None:
        return HttpResponse("Student ID is Invalid")
    else:
        context = context_data()
        context['student'] = Student.objects.get(id=pk)
        return render(request, 'library/view_id.html', context)

@login_required
def view_scanner(request):
    context = context_data()
    return render(request, 'library/scanner.html', context)


@login_required
def view_details(request, code = None):
    if code is None:
        return HttpResponse("Student code is Invalid")
    else:
        print(code)
        context = context_data()
        context['student'] = Student.objects.get(student_id=code)
        print(Student.objects.get(student_id=code).id)
        return render(request, 'library/view_details.html', context)
@login_required
def student_data(request,id):
    context =context_data()
    context['page'] = 'student Documents'
    context['page_title'] = 'student Documents'
    context['docs'] = StudentDocuments.objects.filter(student=id)
    return render(request, 'library/student_data.html', context)
@login_required
def delete_student(request, pk=None):
    resp = { 'status' : 'failed', 'msg' : '' }
    if pk is None:
        resp['msg'] = "No data has been sent into the request."
    else:
        try:
            models.Student.objects.get(id=pk).delete()
            resp['status'] = 'success'
            messages.success(request, 'Student has been deleted successfully.')
        except:
            resp['msg'] = "Student has failed to delete."

    return HttpResponse(json.dumps(resp), content_type="application/json")
