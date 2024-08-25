#!/bin/sh

# Check if the database is already initialized
if [ ! -f ./db_initialized ]; then
  echo "Initializing the database..."
  python manage.py makemigrations
  python manage.py migrate
  python manage.py load_courses
  python manage.py load_users
  python manage.py load_reviews
  python manage.py load_enrolled_courses
  touch ./db_initialized
else
  echo "Database already initialized."
fi

# Start the Django development server
exec "$@"