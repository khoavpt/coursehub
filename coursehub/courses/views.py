from django.shortcuts import render, HttpResponse

def home_page(request):
    return render(request, 'courses/home_page.html')

def course_search(request):
    pass

def course_detail(request, course_id):
    pass

def enroll_course(request, course_id):
    pass

def review_course(request, course_id):
    pass

