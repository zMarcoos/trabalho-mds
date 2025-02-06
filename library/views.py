import os
import logging
from django.shortcuts import redirect, render
from django.http import HttpResponseRedirect
from . import forms, models
from django.http import HttpResponseRedirect
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required, user_passes_test
from datetime import date
from django.core.mail import send_mail
from librarymanagement.settings import EMAIL_HOST_USER
from django.contrib.auth import logout
from django.shortcuts import redirect

logger = logging.getLogger(__name__)


def custom_logout_view(request):
    logout(request)
    return redirect('/')


def home_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')

    return render(request, 'library/index.html')


def student_click_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')

    return render(request, 'library/studentclick.html')


def admin_click_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request, 'library/adminclick.html')


def student_signup_view(request):
    first_form = forms.StudentUserForm(request.POST or None)
    second_form = forms.StudentExtraForm(request.POST or None)
    if request.method == 'POST' and first_form.is_valid() and second_form.is_valid():
        student_account = first_form.save()
        student_account.set_password(student_account.password)
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


def after_login_view(request):
    if is_admin(request.user):
        return render(request, 'library/adminafterlogin.html')
    elif is_student(request.user):
        return render(request, 'library/studentafterlogin.html')


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def add_book_view(request):
    form = forms.BookForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
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
def issue_book_view(request):
    form = forms.IssuedBookForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        models.IssuedBook.objects.create(
            enrollment=request.POST.get('enrollment2'),
            isbn=request.POST.get('isbn2')
        )
        return render(request, 'library/bookissued.html')

    return render(request, 'library/issuebook.html', {'form': form})


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def view_issued_book_view(request):
    issued_books = models.IssuedBook.objects.all()
    issued_books_list = []

    for issued_book in issued_books:
        issued_book_date = issued_book.issuedate.strftime("%d/%m/%Y")
        expiry_date = issued_book.expirydate.strftime("%d/%m/%Y")

        days = (date.today() - issued_book.issuedate).days
        fine = max(0, (days - 15) * 10) if days > 15 else 0

        books = models.Book.objects.filter(isbn=issued_book.isbn)
        students = models.StudentExtra.objects.filter(
            enrollment=issued_book.enrollment)

        for book, student in zip(books, students):
            issued_books_list.append((
                student.get_name,
                student.enrollment,
                book.name,
                book.author,
                issued_book_date,
                expiry_date,
                fine,
                issued_book.status
            ))

    return render(request, 'library/viewissuedbook.html', {'li': issued_books_list})


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def view_student_view(request):
    students = models.StudentExtra.objects.all()
    return render(request, 'library/viewstudent.html', {'students': students})


@login_required(login_url='studentlogin')
def view_issued_book_by_student(request):
    student = models.StudentExtra.objects.filter(user=request.user).first()

    if not student:
        return render(request, 'library/viewissuedbookbystudent.html', {'combined_data': []})

    issued_books = models.IssuedBook.objects.filter(
        enrollment=student.enrollment)
    combined_data = []

    for issued_book in issued_books:
        book = models.Book.objects.filter(isbn=issued_book.isbn).first()

        if book:
            issue_date = issued_book.issuedate.strftime('%d/%m/%Y')
            expiration_date = issued_book.expirydate.strftime('%d/%m/%Y')

            days = (date.today() - issued_book.issuedate).days
            fine = max(0, (days - 15) * 10) if days > 15 else 0

            combined_data.append((
                student.get_name,
                student.enrollment,
                student.branch,
                book.name,
                book.author,
                issue_date,
                expiration_date,
                fine,
                issued_book.status,
                issued_book.id
            ))

    return render(request, 'library/viewissuedbookbystudent.html', {'combined_data': combined_data})


def return_book(_, id):
    issued_book = models.IssuedBook.objects.get(pk=id)
    issued_book.status = "Returned"
    issued_book.save()
    return redirect('viewissuedbookbystudent')


def aboutus_view(request):
    return render(request, 'library/aboutus.html')


def contactus_view(request):
    submit = forms.ContactusForm()

    if request.method == 'POST':
        submit = forms.ContactusForm(request.POST)

        if submit.is_valid():
            email = submit.cleaned_data['Email']
            name = submit.cleaned_data['Name']
            message = submit.cleaned_data['Message']

            subject = f"{name} || {email}"
            recipient_list = [
                os.getenv('RECIPIENT_EMAIL', 'zmarcoos12@gmail.com')]

            try:
                send_mail(
                    subject,
                    message,
                    EMAIL_HOST_USER,
                    recipient_list,
                    fail_silently=False,
                )

                return render(request, 'library/contactussuccess.html')

            except Exception as exception:
                logger.error(f"Erro ao enviar e-mail: {exception}")

                return render(request, 'library/contactus.html', {
                    'form': submit,
                    'error_message': 'Erro ao enviar e-mail. Tente novamente mais tarde.'
                })

    return render(request, 'library/contactus.html', {'form': submit})
