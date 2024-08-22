# users/management/commands/load_users.py
import csv
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from users.models import UserProfile

class Command(BaseCommand):
    help = 'Load data from users CSV file into the database'

    def handle(self, *args, **kwargs):
        with open('recommendations/data/Coursera_users_sampled.csv', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                User.objects.create_user(
                    username=row['username'],
                    email=row['username'] + '@gmail.com',
                    password=row['password'],
                    first_name=row['first_name'],
                )
                UserProfile.objects.create(
                    user=User.objects.get(username=row['username']),
                    location='Ha Noi',
                    phone_number='0123456789',
                    birth_date='2004-01-01',
                    gender='O'
                )
        self.stdout.write(self.style.SUCCESS('Successfully loaded users data from CSV'))