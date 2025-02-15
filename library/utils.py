from datetime import timedelta
from django.utils import timezone


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


def get_expiry():
  return timezone.now().date() + timedelta(days=15)
