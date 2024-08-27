# reviews/management/commands/load_reviews.py
import csv
from django.core.management.base import BaseCommand
from courses.models import Review, Course
from django.contrib.auth.models import User
import pandas as pd

class Command(BaseCommand):
    help = 'Load data from reviews CSV file into the database'

    def handle(self, *args, **kwargs):
        with open('data/Coursera_reviews_sampled.csv', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                try:
                    course = Course.objects.get(name=row['course_name'])
                    user = User.objects.get(first_name=row['reviewers'])
                    review_date = pd.to_datetime(row['date_reviews'], format="%Y-%m-%d").date()
                    review_text = row['reviews'].encode('utf-8').decode('utf-8')
                    Review.objects.create(
                        course=course,
                        user=user,
                        rating=row['rating'],
                        review_text=review_text,
                        review_date=review_date
                    )
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error processing row: {row}"))
                    self.stdout.write(self.style.ERROR(str(e)))


        self.stdout.write(self.style.SUCCESS('Successfully loaded reviews data from CSV'))