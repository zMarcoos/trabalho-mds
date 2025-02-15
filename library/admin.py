from django.contrib import admin
from .models import Book, StudentExtra, IssuedBook


class BookAdmin(admin.ModelAdmin):
    pass


class StudentExtraAdmin(admin.ModelAdmin):
    pass


class IssuedBookAdmin(admin.ModelAdmin):
    pass


admin.site.register(Book, BookAdmin)
admin.site.register(StudentExtra, StudentExtraAdmin)
admin.site.register(IssuedBook, IssuedBookAdmin)
