# reviews/management/commands/load_enrolled_courses.py
import csv
from django.core.management.base import BaseCommand
from courses.models import Course
from django.contrib.auth.models import User
from users.models import UserProfile

class Command(BaseCommand):
    help = 'Load enrolled courses data from CSV file into the database'

    def handle(self, *args, **kwargs):
        with open('data/Coursera_reviews_sampled.csv', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                try:
                    course = Course.objects.get(name=row['course_name'])
                    user = User.objects.get(first_name=row['reviewers'])
                    user_profile = UserProfile.objects.get(user=user)
                    
                    # Add the course to the user's enrolled courses
                    user_profile.enrolled_courses.add(course)
                    user_profile.save()

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error processing row: {row}"))
                    self.stdout.write(self.style.ERROR(str(e)))

        self.stdout.write(self.style.SUCCESS('Successfully loaded enrolled courses data from CSV'))