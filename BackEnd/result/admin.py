from django.contrib import admin

from .models import ResultBatch, StudentResult,StudentCharacterSkill

# Register your models here.
@admin.register(ResultBatch)
class ResultBatchAdmin(admin.ModelAdmin):
    list_display = ("id", "class_room", "subject", "teacher", "session", "term", "status", "is_uploaded", "is_locked")
    list_filter = ("status", "is_uploaded", "is_locked")
    search_fields = ("class_room__name", "subject__name", "teacher__name", "session__name", "term__name")

@admin.register(StudentResult)
class StudentResultAdmin(admin.ModelAdmin):
    list_display = ("id", "batch", "student", "ca1", "ca2", "exam", "total")
    search_fields = ("batch__class_room__name", "batch__subject__name", "student__name")
    list_filter = ("batch", "grade")
@admin.register(StudentCharacterSkill) 
class StudentCharacterSkill(admin.ModelAdmin) :
    list_display = ("student", "punctuality", "honesty", "creativity", "handwriting","verbal_fluency")
    