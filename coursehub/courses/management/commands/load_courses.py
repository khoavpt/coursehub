# courses/management/commands/load_courses.py
import csv
from django.core.management.base import BaseCommand
from courses.models import Course  # Replace with your actual model

class Command(BaseCommand):
    help = 'Load data from courses CSV file into the database'

    def handle(self, *args, **kwargs):
        with open('recommendations/data/Coursera_courses_sampled.csv', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                Course.objects.create(
                    name=row['name'],
                    institution=row['institution'],
                    course_url=row['course_url'],
                    price=row['price']
                )
        self.stdout.write(self.style.SUCCESS('Successfully loaded courses data from CSV'))