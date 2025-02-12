from django.db import models
from django.contrib.auth.models import User
from datetime import datetime, timedelta

class StudentExtra(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    enrollment = models.CharField(max_length=40)
    branch = models.CharField(max_length=40)

    def __str__(self):
        return self.user.first_name + '[' + str(self.enrollment) + ']'

    @property
    def get_name(self):
        return self.user.first_name

    @property
    def getuserid(self):
        return self.user.id


class Book(models.Model):
    categories = [
        ('programming', 'Programação'),
        ('data_structure', 'Estrutura de Dados'),
        ('software_engineering', 'Engenharia de Software'),
        ('data_science', 'Ciência de Dados'),
        ('artificial_intelligence', 'Inteligência Artificial'),
        ('cybersecurity', 'Cibersegurança'),
        ('cloud_computing', 'Computação em Nuvem'),
        ('web_development', 'Desenvolvimento Web'),
        ('mobile_development', 'Desenvolvimento Mobile'),
        ('computer_networks', 'Redes de Computadores'),
        ('hardware', 'Hardware e Eletrônica'),
        ('robotics', 'Robótica'),
        ('automation', 'Automação Industrial'),
        ('mechanical_engineering', 'Engenharia Mecânica'),
        ('electrical_engineering', 'Engenharia Elétrica'),
        ('civil_engineering', 'Engenharia Civil'),
        ('biomedical_engineering', 'Engenharia Biomédica'),
        ('materials_engineering', 'Engenharia de Materiais'),
        ('control_systems', 'Sistemas de Controle'),
        ('physics', 'Física Aplicada'),
        ('mathematics', 'Matemática Aplicada'),
        ('project_management', 'Gestão de Projetos'),
        ('entrepreneurship', 'Empreendedorismo Tecnológico'),
        ('biography', 'Biografia'),
        ('history', 'História da Tecnologia'),
    ]

    name = models.CharField(max_length=100, blank=True)
    isbn = models.PositiveIntegerField()
    author = models.CharField(max_length=100, blank=True)
    category = models.CharField(max_length=30, choices=categories, default=categories[0][0])
    image_url = models.URLField(max_length=500, blank=True, null=True)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.name} [{self.isbn}]"

    def is_available(self):
        return self.quantity > 0


def get_expiry():
    return datetime.today() + timedelta(days=15)


class IssuedBook(models.Model):
    enrollment = models.CharField(max_length=30)
    isbn = models.CharField(max_length=30)
    issuedate = models.DateField(auto_now=True)
    expirydate = models.DateField(default=get_expiry)
    statuschoice = [
        ('Issued', 'Issued'),
        ('Returned', 'Returned'),
    ]
    status = models.CharField(max_length=20, choices=statuschoice, default="Issued")

    def __str__(self):
        return self.enrollment
