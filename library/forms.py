from django import forms
from django.contrib.auth.models import User
from . import models
from library.models import Book

class ContactusForm(forms.Form):
    Nome = forms.CharField(max_length=30)
    Email = forms.EmailField()
    Mensagem = forms.CharField(max_length=500, widget=forms.Textarea(attrs={'rows': 3, 'cols': 30}))


class StudentUserForm(forms.ModelForm):
    class Meta:
        model=User
        fields=['first_name','last_name','username','password']
        widgets = {
            'password': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Digite sua senha'}),
        }


class StudentExtraForm(forms.ModelForm):
    class Meta:
        model=models.StudentExtra
        fields=['enrollment','branch']


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['name', 'isbn', 'author', 'category', 'image_url', 'quantity']


    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if quantity is not None and quantity <= 0:
            raise forms.ValidationError("A quantidade deve ser maior que 0.")

        return quantity


    def clean_isbn(self):
        isbn = str(self.cleaned_data.get('isbn')).replace('-', '').replace(' ', '')

        if not isbn.isdigit():
            raise forms.ValidationError("O ISBN deve conter apenas números.")

        if Book.objects.filter(isbn=isbn).exists():
            raise forms.ValidationError("Este ISBN já está cadastrado.")

        if len(isbn) == 10:
            if not self.is_valid_isbn10(isbn):
                raise forms.ValidationError("ISBN-10 inválido.")
        elif len(isbn) == 13:
            if not self.is_valid_isbn13(isbn):
                raise forms.ValidationError("ISBN-13 inválido.")
        else:
            raise forms.ValidationError("O ISBN deve ter 10 ou 13 dígitos.")

        return isbn


    def clean_image_url(self):
        image_url = self.cleaned_data.get('image_url')
        if image_url:
            if not image_url.startswith(('http://', 'https://')):
                raise forms.ValidationError("A URL da imagem deve começar com http:// ou https://")

        return image_url


    def is_valid_isbn10(self, isbn):
        if len(isbn) != 10: return False

        total = sum((10 - index) * int(digit) for index, digit in enumerate(isbn[:9]))
        check_digit = isbn[9]

        if check_digit == 'X':
            total += 10
        else:
            total += int(check_digit)

        return total % 11 == 0


    def is_valid_isbn13(self, isbn):
        if len(isbn) != 13: return False

        total = sum((1 if index % 2 == 0 else 3) * int(digit) for index, digit in enumerate(isbn[:12]))
        check_digit = (10 - (total % 10)) % 10

        return check_digit == int(isbn[12])


class IssuedBookForm(forms.Form):
    isbn2 = forms.ModelChoiceField(
        queryset=models.Book.objects.all(),
        empty_label="Selecione alguma opção",
        to_field_name="isbn",label='Nome & ISBN'
    )
    enrollment2=forms.ModelChoiceField(
        queryset=models.StudentExtra.objects.all(),
        empty_label="Selecione alguma opção",to_field_name='enrollment',
        label='Nome e matrícula'
    )
