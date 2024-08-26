import csv
from django.shortcuts import render, HttpResponse, get_object_or_404
from courses.models import Course, Review
from users.models import UserProfile
from django.contrib.auth.models import User
from .forms import ReviewForm
from courses.recommendations.models.non_personalized_rs import NonPersonalizedRecommenderSystem
from courses.recommendations.models.item_regression_rs import ItemBasedRegressionRecommenderSystem1
from courses.recommendations.recommend import get_user_recommendations, retrain_item_regression_model, retrain_non_personalized_model

NEW_REVIEWS_COUNT = 0

def home_page(request):
    if request.user.is_authenticated:
        num_ratings = Review.objects.filter(user=request.user).count()
        if num_ratings < 5:
            recommended_courses_id = get_user_recommendations(model_type='non personalized', user_id=request.user.id)
        else:
            recommended_courses_id = get_user_recommendations(model_type='item regression', user_id=request.user.id)
    else:
        recommended_courses_id = get_user_recommendations(model_type='non personalized', user_id=request.user.id)

    recommended_courses = Course.objects.filter(id__in=recommended_courses_id)
    context = {
        'recommended_courses': recommended_courses
    }
    return render(request, 'courses/home_page.html', context)

def course_search(request):
    query = request.GET.get('query')
    if query:
        courses = Course.objects.filter(name__icontains=query)
    else:
        courses = Course.objects.all()
    return render(request, 'courses/course_search.html', {'courses': courses})

def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    reviews = Review.objects.filter(course=course)
    review_form = ReviewForm()
    
    
    is_enrolled = False
    has_reviewed = False
    if request.user.is_authenticated:
        # Check if the user is enrolled in the course
        user_profile = request.user.userprofile
        is_enrolled = course in user_profile.enrolled_courses.all()
    
        # Check if the user has already reviewed the course
        user_review = Review.objects.filter(course=course, user=request.user)
        if user_review:
            has_reviewed = True


    context = {
        'course': course,
        'reviews': reviews,
        'review_form': review_form,
        'is_enrolled': is_enrolled,
        'has_reviewed': has_reviewed
    }
    return render(request, 'courses/course_detail.html', context)


def enroll_course(request, course_id):
    if request.method == 'POST':
        course = get_object_or_404(Course, id=course_id)
        user = get_object_or_404(User, id=request.user.id)
        user_profile = UserProfile.objects.get(user=user)
        user_profile.enrolled_courses.add(course)
        user_profile.save()
        return render(request, 'courses/course_detail.html', {'course': course, 'reviews': Review.objects.filter(course=course), 'review_form': ReviewForm(), 'is_enrolled': True})
    else:
        return HttpResponse('Method not allowed')


def review_course(request, course_id):
    global NEW_REVIEWS_COUNT  # Declare NEW_REVIEWS_COUNT as global
    if request.method == 'POST':
        course = get_object_or_404(Course, id=course_id)
        user = get_object_or_404(User, id=request.user.id)
        
        # Save the review to the database
        review = Review(course=course, user=user, rating=request.POST['rating'], review_text=request.POST['review_text'])
        review.save()

        # Append the new review to the CSV file
        with open('courses/recommendations/rating_data.csv', 'a', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow([course.id, user.id, request.POST['rating']])
        
        # Retrain the models after every 5 new reviews
        is_retrain = False
        NEW_REVIEWS_COUNT += 1
        print(NEW_REVIEWS_COUNT)
        if NEW_REVIEWS_COUNT >= 5:
            is_retrain = True
            retrain_item_regression_model(save=False)
            retrain_non_personalized_model(save=False)
            NEW_REVIEWS_COUNT = 0     

        return render(request, 'courses/course_detail.html', {
            'course': course, 
            'reviews': Review.objects.filter(course=course), 
            'review_form': ReviewForm(),
            'is_retrain': is_retrain,
            'is_enrolled': True,
            'has_reviewed': True
        })
    else:
        return HttpResponse('Method not allowed')

