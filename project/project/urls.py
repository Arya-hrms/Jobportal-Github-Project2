"""
URL configuration for project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from app import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('adminlogin/', views.adminlogin, name='adminlogin'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/', admin.site.urls),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('home/', views.home, name='home'),
    path('candidate/dashboard/', views.candidate_dashboard, name='candidate_dashboard'),
    path('candidate/editprofile/', views.candidate_editprofile, name='candidate_editprofile'),
    path('candidate/jobsearch/', views.job_search, name='jobsearch'),
    path('register_recruiter/', views.register_recruiter, name='register_recruiter'),
    path('login_recruiter/', views.login_recruiter, name='login_recruiter'),
    path('recruiter/recruiter_dashboard/', views.recruiter_dashboard, name='recruiter_dashboard'),
    path('recruiter/job_post/', views.job_post, name='job_post'),
    path('recruiter/job_management/', views.job_management, name='job_management'),
    path(
        'recruiter/<int:job_id>/edit_job/',
        views.edit_job,
        name='edit_job'
    ),

    path(
        'recruiter/job_management/<int:job_id>/delete_job/',
        views.delete_job,
        name='delete_job'
    ),
    path('recruiter/application_management/', views.application_management, name='application_management'),
    path('recruiter/candidate_management/', views.candidate_management, name='candidate_management'),
    path('candidate/apply_job/<int:job_id>/', views.apply_job, name='apply_job'),
    path('candidate/my_applications/', views.my_applications, name='my_applications'),
    path(
    'candidate/recommended_jobs/',
    views.recommended_jobs,
    name='recommended_jobs'
    ),
    path('admin_manage_users/', views.admin_manage_users, name='admin_manage_users'),
    path('admin_manage_recruiters/', views.admin_manage_recruiters, name='admin_manage_recruiters'),
    path('admin_manage_jobs/', views.admin_manage_jobs, name='admin_manage_jobs'),
    path('logoutcandidate/', views.logoutcandidate, name='logoutcandidate'),
path('logoutrecruiter/', views.logoutrecruiter, name='logoutrecruiter'),
        

]
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )