import os
import logging
from django.shortcuts import redirect, render
from django.http import HttpResponseRedirect
from . import forms, models
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required, user_passes_test
from datetime import date
from django.core.mail import send_mail
from librarymanagement.settings import EMAIL_HOST_USER
from django.contrib.auth import logout
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from django.contrib.auth.views import LoginView
from django.contrib.auth import authenticate, login
from django.urls import reverse

COMMON_NAV_ITEMS = [
    {"name": "Sobre nós", "url": "/aboutus"},
    {"name": "Contate-nos", "url": "/contactus"},
]

AUTH_NAV_ITEMS = [
    {"name": "Administrador", "url": "/adminclick"},
    {"name": "Estudante", "url": "/studentclick"},
    *COMMON_NAV_ITEMS,
]

ADMINISTRATOR_NAV_ITEMS = [
    {"name": "Livros", "submenu": [
        {"name": "Adicionar livro", "url": "/addbook"},
        {"name": "Visualizar livros", "url": "/viewbook"}
    ]},
    {"name": "Empréstimos", "submenu": [
        {"name": "Emitir livro", "url": "/issuebook"},
        {"name": "Livros emprestados", "url": "/viewissuedbook"}
    ]},
    {"name": "Estudantes", "submenu": [
        {"name": "Visualizar estudantes", "url": "/viewstudent"}
    ]},
    *COMMON_NAV_ITEMS,
    {"name": "Sair", "url": "/logout"},
]

STUDENT_NAV_ITEMS = [
    {"name": "Livros", "submenu": [
        {"name": "Livros emprestados", "url": "/viewissuedbookbystudent"},
    ]},
    *COMMON_NAV_ITEMS,
    {"name": "Sair", "url": "/logout"},
]


logger = logging.getLogger(__name__)


class CustomLoginView(LoginView):
    template_name = 'library/registration/login.html'

    def form_valid(self, form):
        user = form.get_user()
        login(self.request, user)

        if user.is_superuser or user.is_staff or user.groups.filter(name='STUDENT').exists():
            return redirect('afterlogin')
        else:
            return redirect('/')


    def form_invalid(self, form):
        username = self.request.POST.get('username')
        password = self.request.POST.get('password')

        user = authenticate(username=username, password=password)
        if user is None:
            error_message = "Usuário não encontrado ou senha incorreta."
        else:
            error_message = "Erro ao tentar logar. Verifique seus dados."

        return self.render_to_response(self.get_context_data(form=form, error_message=error_message))


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user_type = self.request.GET.get('type', 'student')
        if user_type == "admin":
            context.update({
                "title": "Login do administrador",
                "heading": "Acesso do administrador",
                "show_signup_link": False,
                "nav_items": AUTH_NAV_ITEMS,
            })
        else:
            context.update({
                "title": "Login do estudante",
                "heading": "Acesso do estudante",
                "show_signup_link": True,
                "nav_items": AUTH_NAV_ITEMS,
            })

        context["error_message"] = kwargs.get('error_message', None)
        return context


@require_http_methods(["GET"])
def custom_logout_view(request):
    logout(request)
    return redirect('/')


@require_http_methods(["GET"])
def home_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')

    return render(request, 'library/index.html', {"nav_items": AUTH_NAV_ITEMS})


@require_http_methods(["GET"])
def student_click_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')

    return render(request, 'library/student/student_click.html', {"nav_items": AUTH_NAV_ITEMS})


@require_http_methods(["GET"])
def admin_click_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')

    return render(request, 'library/admin/admin_click.html', {"nav_items": AUTH_NAV_ITEMS})


@csrf_protect
@require_http_methods(["GET"])
def student_signup_page(request):
    return render(request, 'library/student/student_signup.html', {
        'form1': forms.StudentUserForm(),
        'form2': forms.StudentExtraForm(),
        "nav_items": AUTH_NAV_ITEMS
    })


@csrf_protect
@require_http_methods(["POST"])
def student_signup_action(request):
    first_form = forms.StudentUserForm(request.POST)
    second_form = forms.StudentExtraForm(request.POST)

    if first_form.is_valid() and second_form.is_valid():
        student_account = first_form.save(commit=False)
        student_account.set_password(student_account.password)
        student_account.save()

        student_extra_data = second_form.save(commit=False)
        student_extra_data.user = student_account
        student_extra_data.save()

        Group.objects.get_or_create(name='STUDENT')[
            0].user_set.add(student_account)

        login_url = reverse('custom_login') + "?type=student"
        return HttpResponseRedirect(login_url)

    return render(request, 'library/student/student_signup.html', {
        "form1": first_form,
        "form2": second_form,
        "nav_items": AUTH_NAV_ITEMS,
    })


def is_admin(user):
    return user.is_superuser or user.is_staff


def is_student(user):
    return user.groups.filter(name='STUDENT').exists()


@require_http_methods(["GET"])
@login_required
def after_login_page(request):
    if is_admin(request.user):
        return render(request, 'library/admin/admin_after_login.html', {"nav_items": ADMINISTRATOR_NAV_ITEMS})
    elif is_student(request.user):
        return render(request, 'library/student/student_after_login.html', {"nav_items": STUDENT_NAV_ITEMS})

    return redirect('/')


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
@require_http_methods(["GET"])
def add_book_page(request):
    form = forms.BookForm()
    return render(request, 'library/book/add_book.html', {'form': form, "nav_items": ADMINISTRATOR_NAV_ITEMS})


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
@csrf_protect
@require_http_methods(["POST"])
def add_book_action(request):
    form = forms.BookForm(request.POST)

    if form.is_valid():
        isbn = form.cleaned_data['isbn']
        quantity = form.cleaned_data['quantity']

        book, created = models.Book.objects.get_or_create(isbn=isbn, defaults=form.cleaned_data)
        if not created:
            book.quantity += quantity
            book.save()

        return render(request, 'library/book/book_added.html', {"nav_items": ADMINISTRATOR_NAV_ITEMS})

    return render(request, 'library/book/add_book.html', {
        'form': form,
        'error_message': 'Formulário inválido.',
        "nav_items": ADMINISTRATOR_NAV_ITEMS
    })


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
@require_http_methods(["GET"])
def view_book_view(request):
    books = models.Book.objects.all()
    return render(request, 'library/book/view_book.html', {'books': books, "nav_items": ADMINISTRATOR_NAV_ITEMS})


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
@require_http_methods(["GET"])
def issue_book_page(request):
    return render_form_page(request, 'library/book/issue_book.html', forms.IssuedBookForm(), ADMINISTRATOR_NAV_ITEMS)


@csrf_protect
@require_http_methods(["POST"])
@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def issue_book_action(request):
    form = forms.IssuedBookForm(request.POST)
    page = 'library/book/issue_book.html'

    if form.is_valid():
        book = form.cleaned_data.get('book')
        enrollment = form.cleaned_data.get('enrollment')

        if not book or book.quantity <= 0:
            return render_form_page(request, page, form, ADMINISTRATOR_NAV_ITEMS, 'Livro indisponível para empréstimo.')

        models.IssuedBook.objects.create(enrollment=enrollment.enrollment, isbn=book.isbn)
        book.quantity -= 1
        book.save()

        return render(request, 'library/book/book_issued.html', {"nav_items": ADMINISTRATOR_NAV_ITEMS})

    return render_form_page(request, page, form, ADMINISTRATOR_NAV_ITEMS)


def render_form_page(request, template, form, nav_items, error_message=None):
    context = {"form": form, "nav_items": nav_items}

    if error_message:
        context["error_message"] = error_message

    return render(request, template, context)


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
@require_http_methods(["GET"])
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

    return render(request, 'library/book/view_issued_book.html', {'li': issued_books_list, "nav_items": ADMINISTRATOR_NAV_ITEMS})


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
@require_http_methods(["GET"])
def view_student_view(request):
    students = models.StudentExtra.objects.all()
    return render(request, 'library/student/view_student.html', {'students': students, "nav_items": ADMINISTRATOR_NAV_ITEMS})


@login_required(login_url='studentlogin')
@require_http_methods(["GET"])
def view_issued_book_by_student(request):
    student = models.StudentExtra.objects.filter(user=request.user).first()

    if not student:
        return render(request, 'library/book/view_issued_book_by_student.html', {'combined_data': [], "nav_items": STUDENT_NAV_ITEMS})

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

    return render(request, 'library/book/view_issued_book_by_student.html', {'combined_data': combined_data, "nav_items": STUDENT_NAV_ITEMS})


@login_required(login_url='studentlogin')
@csrf_protect
@require_http_methods(["POST"])
def return_book(request, id):
    try:
        issued_book = models.IssuedBook.objects.get(pk=id)

        if issued_book.status == "Returned":
            return redirect('viewissuedbookbystudent')

        issued_book.status = "Returned"
        issued_book.save()

        book = models.Book.objects.filter(isbn=issued_book.isbn).first()
        if book:
            book.quantity += 1
            book.save()

        return redirect('viewissuedbookbystudent')
    except models.IssuedBook.DoesNotExist:
        return redirect('viewissuedbookbystudent')


@require_http_methods(["GET"])
def about_us_view(request):
    return render(request, 'library/about_us/index.html', {"nav_items": AUTH_NAV_ITEMS})


@csrf_protect
@require_http_methods(["GET"])
def contactus_page(request):
    return render_form_page(request, 'library/contact/index.html', forms.ContactusForm(), AUTH_NAV_ITEMS)


@csrf_protect
@require_http_methods(["POST"])
def contactus_action(request):
    submit = forms.ContactusForm(request.POST)
    page = 'library/contact/index.html'

    if submit.is_valid():
        email = submit.cleaned_data['Email']
        name = submit.cleaned_data['Nome']
        message = submit.cleaned_data['Mensagem']

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
            return render(request, 'library/contact/success.html', {'nav_items': AUTH_NAV_ITEMS})

        except Exception as exception:
            logger.error(f"Erro ao enviar e-mail: {exception}")
            return render_form_page(request, page, submit, AUTH_NAV_ITEMS, 'Erro ao enviar e-mail. Tente novamente mais tarde.')

    return render_form_page(request, page, submit, AUTH_NAV_ITEMS)
