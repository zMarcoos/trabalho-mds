"""librarymanagement URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf.urls import include
from django.urls import path
from library import views
from django.contrib.auth.views import LoginView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', views.home_view),

    path('adminclick', views.admin_click_view),
    path('studentclick', views.student_click_view),

    path('studentsignup', views.student_signup_view),
    path('adminlogin', LoginView.as_view(
        template_name='library/adminlogin.html')),
    path('studentlogin', LoginView.as_view(
        template_name='library/studentlogin.html')),
    path('returnbook/<int:id>/', views.return_book, name='returnbook'),

    path('logout', views.custom_logout_view, name='logout'),
    path('afterlogin', views.after_login_view),

    path('addbook', views.add_book_view),
    path('viewbook', views.view_book_view),
    path('issuebook', views.issue_book_view),
    path('viewissuedbook', views.view_issued_book_view),
    path('viewstudent', views.view_student_view),
    path('viewissuedbookbystudent', views.view_issued_book_by_student,
         name='viewissuedbookbystudent'),

    path('aboutus', views.aboutus_view),
    path('contactus', views.contactus_view),

]
