from django.db import models


class TS(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class StudyProgram(TS):
    code = models.CharField(max_length=50, unique=True)          # например: "BI"
    name = models.CharField(max_length=255, unique=True)         # "Бизнес-информатика"
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Skill(TS):
    code = models.CharField(max_length=64, unique=True)          # "python", "sql"
    name = models.CharField(max_length=255)                      # "Python", "SQL"
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["code"]

    def __str__(self):
        return self.code


class Language(TS):
    code = models.CharField(max_length=8, unique=True)           # "ru", "en"
    name = models.CharField(max_length=64)                       # "Русский", "English"
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["code"]

    def __str__(self):
        return self.code

