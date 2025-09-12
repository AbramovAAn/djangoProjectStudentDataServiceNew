import csv
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from students.models import StudentsProjection

class Command(BaseCommand):
    help = "Импорт студентов из CSV в витрину StudentsProjection"

    def add_arguments(self, parser):
        parser.add_argument("csv_path", type=str, help="Путь к CSV-файлу")
        parser.add_argument("--delimiter", default=",")
        parser.add_argument("--encoding", default="utf-8")

    def handle(self, *args, **opts):
        path = Path(opts["csv_path"])
        if not path.exists():
            raise CommandError(f"Файл не найден: {path}")

        count = 0
        with path.open("r", encoding=opts["encoding"], newline="") as f:
            reader = csv.DictReader(f, delimiter=opts["delimiter"])
            for row in reader:
                # ожидаемые столбцы: fio, program, course, gpa, language, skills
                # skills как "python;sql;excel" или "python,sql,excel"
                raw_skills = row.get("skills") or ""
                skills = [s.strip() for s in raw_skills.replace(";", ",").split(",") if s.strip()]
                data = {
                    "fio": row.get("fio", ""),
                    "program": row.get("program", ""),
                    "course": int(row.get("course") or 0),
                    "gpa": float(row.get("gpa") or 0.0),
                    "language": row.get("language", "").strip(),
                    "skills": skills,
                }
                StudentsProjection.objects.create(data=data)
                count += 1

        self.stdout.write(self.style.SUCCESS(f"Импортировано записей: {count}"))