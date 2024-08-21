from django.shortcuts import render, HttpResponse, get_object_or_404
from courses.models import Course, Review
from users.models import UserProfile
from django.contrib.auth.models import User
from .forms import ReviewForm

def home_page(request):
    return render(request, 'courses/home_page.html')

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
    
    # Check if the user is enrolled in the course
    is_enrolled = False
    if request.user.is_authenticated:
        user_profile = request.user.userprofile
        is_enrolled = course in user_profile.enrolled_courses.all()

    context = {
        'course': course,
        'reviews': reviews,
        'review_form': review_form,
        'is_enrolled': is_enrolled
    }
    return render(request, 'courses/course_detail.html', context)


def enroll_course(request, course_id):
    if request.method == 'POST':
        course = get_object_or_404(Course, id=course_id)
        user = get_object_or_404(User, id=request.user.id)
        user_profile = UserProfile.objects.get(user=user)
        user_profile.enrolled_courses.add(course)
        user_profile.save()
        return render(request, 'courses/course_detail.html', {'course': course, 'reviews': Review.objects.filter(course=course), 'review_form': ReviewForm()})
    else:
        return HttpResponse('Method not allowed')


def review_course(request, course_id):
    if request.method == 'POST':
        course = get_object_or_404(Course, id=course_id)
        user = get_object_or_404(User, id=request.user.id)
        review = Review(course=course, user=user, rating=request.POST['rating'], review_text=request.POST['review_text'])

        review.save()
        return render(request, 'courses/course_detail.html', {'course': course, 'reviews': Review.objects.filter(course=course), 'review_form': ReviewForm()})
    else:
        return HttpResponse('Method not allowed')

