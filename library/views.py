import os
import logging
from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required, user_passes_test
from datetime import date
from django.core.mail import send_mail
from django.contrib.auth import logout
from django.views.decorators.http import require_GET, require_POST
from django.middleware.csrf import get_token
from . import forms, models

logger = logging.getLogger(__name__)

@require_GET
def custom_logout_view(request):
    if not request.user.is_authenticated:
        return HttpResponseForbidden("Acesso negado")
    logout(request)
    return redirect('/')

@require_GET
def home_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request, 'library/index.html', {'csrf_token': get_token(request)})

@require_GET
def student_click_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request, 'library/studentclick.html')

@require_GET
def admin_click_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request, 'library/adminclick.html')

@require_POST
def student_signup_view(request):
    first_form = forms.StudentUserForm(request.POST)
    second_form = forms.StudentExtraForm(request.POST)
    if first_form.is_valid() and second_form.is_valid():
        student_account = first_form.save(commit=False)
        student_account.set_password(first_form.cleaned_data['password'])
        student_account.save()

        student_extra_data = second_form.save(commit=False)
        student_extra_data.user = student_account
        student_extra_data.save()

        my_student_group, _ = Group.objects.get_or_create(name='STUDENT')
        my_student_group.user_set.add(student_account)

        return HttpResponseRedirect('studentlogin')
    return render(request, 'library/studentsignup.html', {'form1': first_form, 'form2': second_form})

def is_admin(user):
    return user.is_superuser or user.is_staff

def is_student(user):
    return user.groups.filter(name='STUDENT').exists()

@login_required
def after_login_view(request):
    if is_admin(request.user):
        return render(request, 'library/adminafterlogin.html')
    elif is_student(request.user):
        return render(request, 'library/studentafterlogin.html')
    return HttpResponseForbidden("Acesso negado")

@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
@require_POST
def add_book_view(request):
    form = forms.BookForm(request.POST)
    if form.is_valid():
        form.save()
        return render(request, 'library/bookadded.html')
    return render(request, 'library/addbook.html', {'form': form})

@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def view_book_view(request):
    books = models.Book.objects.all()
    return render(request, 'library/viewbook.html', {'books': books})

@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
@require_POST
def issue_book_view(request):
    form = forms.IssuedBookForm(request.POST)
    if form.is_valid():
        models.IssuedBook.objects.create(
            enrollment=form.cleaned_data['enrollment2'],
            isbn=form.cleaned_data['isbn2']
        )
        return render(request, 'library/bookissued.html')
    return render(request, 'library/issuebook.html', {'form': form})

@login_required(login_url='studentlogin')
def return_book(request, id):
    issued_book = get_object_or_404(models.IssuedBook, pk=id, enrollment=request.user.studentextra.enrollment)
    issued_book.status = "Returned"
    issued_book.save()
    return redirect('viewissuedbookbystudent')

@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def view_student_view(request):
    students = models.StudentExtra.objects.all()
    return render(request, 'library/viewstudent.html', {'students': students})

@require_POST
def contactus_view(request):
    form = forms.ContactusForm(request.POST)
    if form.is_valid():
        email = form.cleaned_data['Email']
        name = form.cleaned_data['Name']
        message = form.cleaned_data['Message']
        subject = f"{name} || {email}"
        recipient_list = [os.getenv('RECIPIENT_EMAIL', 'admin@example.com')]

        try:
            send_mail(
                subject,
                message,
                os.getenv('EMAIL_HOST_USER'),
                recipient_list,
                fail_silently=False,
            )
            return render(request, 'library/contactussuccess.html')
        except Exception as exception:
            logger.error(f"Erro ao enviar e-mail: {exception}")
            return render(request, 'library/contactus.html', {
                'form': form,
                'error_message': 'Erro ao enviar e-mail. Tente novamente mais tarde.'
            })
    return render(request, 'library/contactus.html', {'form': form})
