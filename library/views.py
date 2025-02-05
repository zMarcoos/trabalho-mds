import os
import logging
from django.shortcuts import redirect, render
from django.http import HttpResponseRedirect
from . import forms,models
from django.http import HttpResponseRedirect
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required,user_passes_test
from datetime import date
from django.core.mail import send_mail
from librarymanagement.settings import EMAIL_HOST_USER

logger = logging.getLogger(__name__)

#VER ISSO AQUI AQQ
def is_authenticated(request) -> object:
    if request.user.is_authenticated: return HttpResponseRedirect('afterlogin')

def home_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')

    return render(request,'library/index.html')

def studentclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')

    return render(request,'library/studentclick.html')

def adminclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'library/adminclick.html')

def studentsignup_view(request):
    form1=forms.StudentUserForm()
    form2=forms.StudentExtraForm()
    mydict={'form1':form1,'form2':form2}
    if request.method=='POST':
        form1=forms.StudentUserForm(request.POST)
        form2=forms.StudentExtraForm(request.POST)
        if form1.is_valid() and form2.is_valid():
            user=form1.save()
            user.set_password(user.password)
            user.save()
            f2=form2.save(commit=False)
            f2.user=user
            f2.save()

            my_student_group = Group.objects.get_or_create(name='STUDENT')
            my_student_group[0].user_set.add(user)

        return HttpResponseRedirect('studentlogin')
    return render(request,'library/studentsignup.html',context=mydict)




def is_admin(user):
    if user.is_superuser or user.is_staff:
        return True
    else:
        return False

def is_student(user):
    return user.groups.filter(name='STUDENT').exists()
def afterlogin_view(request):
    if is_admin(request.user):
        return render(request,'library/adminafterlogin.html')

    elif(is_student(request.user)):
        return render(request,'library/studentafterlogin.html')


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def addbook_view(request):
    #now it is empty book form for sending to html
    form=forms.BookForm()
    if request.method=='POST':
        #now this form have data from html
        form=forms.BookForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request,'library/bookadded.html')
    return render(request,'library/addbook.html',{'form':form})

@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def viewbook_view(request):
    books=models.Book.objects.all()
    return render(request,'library/viewbook.html',{'books':books})




@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def issuebook_view(request):
    form=forms.IssuedBookForm()
    if request.method=='POST':
        #now this form have data from html
        form=forms.IssuedBookForm(request.POST)
        if form.is_valid():
            obj=models.IssuedBook()
            obj.enrollment=request.POST.get('enrollment2')
            obj.isbn=request.POST.get('isbn2')
            obj.save()
            return render(request,'library/bookissued.html')
    return render(request,'library/issuebook.html',{'form':form})


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def viewissuedbook_view(request):
    issuedbooks=models.IssuedBook.objects.all()
    li=[]
    for ib in issuedbooks:
        issdate=str(ib.issuedate.day)+'-'+str(ib.issuedate.month)+'-'+str(ib.issuedate.year)
        expdate=str(ib.expirydate.day)+'-'+str(ib.expirydate.month)+'-'+str(ib.expirydate.year)
        #fine calculation
        days=(date.today()-ib.issuedate)
        print(date.today())
        d=days.days
        fine=0
        if d>15:
            day=d-15
            fine=day*10


        books=list(models.Book.objects.filter(isbn=ib.isbn))
        students=list(models.StudentExtra.objects.filter(enrollment=ib.enrollment))
        i=0
        for _ in books:
            t=(students[i].get_name,students[i].enrollment,books[i].name,books[i].author,issdate,expdate,fine,ib.status)
            i=i+1
            li.append(t)

    return render(request,'library/viewissuedbook.html',{'li':li})

@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def viewstudent_view(request):
    students=models.StudentExtra.objects.all()
    return render(request,'library/viewstudent.html',{'students':students})


@login_required(login_url='studentlogin')
def viewissuedbookbystudent(request):
    student = models.StudentExtra.objects.filter(user=request.user).first()

    if not student:
        return render(request, 'library/viewissuedbookbystudent.html', {'combined_data': []})

    issued_books = models.IssuedBook.objects.filter(enrollment=student.enrollment)
    combined_data = []

    for issued_book in issued_books:
        book = models.Book.objects.filter(isbn=issued_book.isbn).first()

        if book:
            issdate = issued_book.issuedate.strftime('%d-%m-%Y')
            expdate = issued_book.expirydate.strftime('%d-%m-%Y')

            days = (date.today() - issued_book.issuedate).days
            fine = max((days - 15) * 10, 0) if days > 15 else 0

            combined_data.append((
                student.get_name, student.enrollment, student.branch,
                book.name, book.author, issdate, expdate, fine, issued_book.status, issued_book.id
            ))

    return render(request, 'library/viewissuedbookbystudent.html', {'combined_data': combined_data})

def returnbook(_, id):
    issued_book = models.IssuedBook.objects.get(pk=id)
    issued_book.status = "Returned"
    issued_book.save()
    return redirect('viewissuedbookbystudent')

def aboutus_view(request):
    return render(request,'library/aboutus.html')

def contactus_view(request):
    submit = forms.ContactusForm()

    if request.method == 'POST':
        submit = forms.ContactusForm(request.POST)

        if submit.is_valid():
            email = submit.cleaned_data['Email']
            name = submit.cleaned_data['Name']
            message = submit.cleaned_data['Message']

            subject = f"{name} || {email}"
            recipient_list = [os.getenv('RECIPIENT_EMAIL', 'zmarcoos12@gmail.com')]

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