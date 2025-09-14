from django.contrib import admin
from .models import StudyProgram, Skill, Language

@admin.register(StudyProgram)
class StudyProgramAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "is_active", "updated_at")
    list_filter  = ("is_active",)
    search_fields = ("code", "name")

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "is_active", "updated_at")
    list_filter  = ("is_active",)
    search_fields = ("code", "name")

@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "is_active", "updated_at")
    list_filter  = ("is_active",)
    search_fields = ("code", "name")
