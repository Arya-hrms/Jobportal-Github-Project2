from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.contrib import messages
from .models import CandidateProfile, Skill, Job, RecruiterProfile, Application
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from .utils import normalize_skill
from django.views.decorators.http import require_http_methods



def register(request):
    if request.method == 'POST':

        firstname = request.POST.get('firstname', '').strip()
        lastname = request.POST.get('lastname', '').strip()
        email = request.POST.get('email', '').strip().lower()
        phone = request.POST.get('phone', '').strip()
        location = request.POST.get('location', '').strip()
        education = request.POST.get('education', '').strip()
        experience = request.POST.get('experience', '').strip()
        skills_input = request.POST.get('skills', '').strip()
        resume = request.FILES.get('resume')
        password = request.POST.get('password', '')

        # Basic validation
        if not firstname or not lastname:
            messages.error(request, "Please enter your full name.")
            return render(request, "register.html")

        if not email:
            messages.error(request, "Please enter your email.")
            return render(request, "register.html")

        if not password:
            messages.error(request, "Please enter a password.")
            return render(request, "register.html")

        # Check email
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return render(request, "register.html")

        # Check phone
        if not phone or len(phone) < 10:
            messages.error(request, "Phone number is invalid.")
            return render(request, "register.html")

        # Convert experience to integer
        try:
            experience = int(experience)
        except (ValueError, TypeError):
            messages.error(request, "Please enter a valid number of years of experience.")
            return render(request, "register.html")

        # Create User
        user = User.objects.create_user(
            username=email,
            first_name=firstname,
            last_name=lastname,
            email=email,
            password=password
        )

        # Create Candidate Profile
        profile = CandidateProfile.objects.create(
            user=user,
            phone=phone,
            location=location,
            education=education,
            experience=experience,
            resume=resume,
        )

        # Save skills
        if skills_input:
            skills_list = [
                skill.strip()
                for skill in skills_input.split(',')
                if skill.strip()
            ]

            for skill_name in skills_list:
                skill, created = Skill.objects.get_or_create(
                    name=skill_name
                )
                profile.skills.add(skill)

        messages.success(request, "Registration successful! Please login.")
        return redirect('login')

    return render(request, 'register.html')



def login_view(request):
    if request.method == 'POST':

        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')

        user = authenticate(
            request,
            username=email,
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect('candidate_dashboard')

        messages.error(
            request,
            "Invalid username or password"
        )

    return render(request, 'login.html')

def home(request):
    return render(request, 'home.html')



@login_required
def candidate_dashboard(request):
    profile = CandidateProfile.objects.get(user=request.user)

    return render(
        request,
        'candidate/dashboard.html',
        {
            'profile': profile
        }
    )


@login_required
def candidate_editprofile(request):
    user = request.user
    profile = user.candidateprofile

    if request.method == "POST":

        # User fields
        user.email = request.POST.get("email", "").strip()
        user.first_name = request.POST.get("first_name", "").strip()
        user.last_name = request.POST.get("last_name", "").strip()
        user.save()

        # Candidate profile fields
        profile.phone = request.POST.get("phone", "").strip()
        profile.location = request.POST.get("location", "").strip()
        profile.education = request.POST.get("education", "").strip()

        experience = request.POST.get("experience", "").strip()
        profile.experience = int(experience) if experience else 0

        # Skills
        skills_text = request.POST.get("skills", "").strip()

        profile.skills.clear()

        if skills_text:
            skill_names = [
                skill.strip()
                for skill in skills_text.split(",")
                if skill.strip()
            ]

            for skill_name in skill_names:
                skill = Skill.objects.filter(
                name__iexact=skill_name
                ).first()

                if not skill:
                    skill = Skill.objects.create(
                    name=skill_name
                    )



                profile.skills.add(skill)

        # Resume
        resume = request.FILES.get("resume")

        if resume:
            profile.resume = resume

        profile.save()

        return redirect("candidate_dashboard")

    return render(
        request,
        "candidate/editprofile.html",
        {
            "profile": profile
        }
    )



def register_recruiter(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        company = request.POST.get('company', '').strip()
        email = request.POST.get('email', '').strip().lower()
        phone = request.POST.get('phone', '').strip()
        location = request.POST.get('location', '').strip()
        password = request.POST.get('password', '')
        

        # Basic validation
        # Check phone
        if not phone or len(phone) < 10:
            messages.error(request, "Phone number is invalid.")
            return render(request, "register_recruiter.html")

        if not email:
            messages.error(request, "Please enter your email.")
            return render(request, "register_recruiter.html")

        if not password:
            messages.error(request, "Please enter a password.")
            return render(request, "register_recruiter.html")

        # Check email
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return render(request, "register_recruiter.html")

        

        

        # Create User
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        # Create Candidate Profile
        RecruiterProfile.objects.create(
            user=user,
            company=company,
            phone=phone,
            location=location,
            
        )

        messages.success(request, "Registration successful! Please login.")
        return redirect('login_recruiter')

    return render(request, 'register_recruiter.html')

def login_recruiter(request):
    if request.method == 'POST':

        email_recruiter = request.POST.get('email', '').strip().lower()
        password_recruiter = request.POST.get('password', '')

        try:
            user_obj = User.objects.get(email=email_recruiter)
        except User.DoesNotExist:
            messages.error(request, "Invalid email or password")
            return render(request, 'login_recruiter.html')

        user = authenticate(
            request,
            username=user_obj.username,
            password=password_recruiter
        )

        if user is not None:
            login(request, user)

           

            return redirect('recruiter_dashboard')

        messages.error(request, "Invalid email or password")

    return render(request, 'login_recruiter.html')



@login_required
def recruiter_dashboard(request):
    profilerecruiter= RecruiterProfile.objects.get(user=request.user)

    # Active jobs
    total_jobs = Job.objects.filter(
        recruiter=profilerecruiter,
        is_active=True
    ).count()

    # Recruiter-ude jobs-il vanna applications
    applications = Application.objects.filter(
        job__recruiter=profilerecruiter
    )

    # Total applications
    total_applications = applications.count()

    

    # Shortlisted applications
    shortlisted_count = applications.filter(
        status='Shortlisted'
    ).count()
    # Selected applications
    selected_count = applications.filter(
        status='Selected'
    ).count()

    context = {
        'profilerecruiter': profilerecruiter,
        'total_jobs': total_jobs,
        'total_applications': total_applications,
        'shortlisted_count': shortlisted_count,
        'selected_count': selected_count,
    }

    return render(
        request,
        'recruiter/recruiter_dashboard.html',
        context
    )
@login_required
def job_post(request):
    if request.method == 'POST':
    
            title = request.POST.get('title')
            company = request.POST.get('company')
            jobtype = request.POST.get('jobtype')
            lastdate = request.POST.get('lastdate')
            location = request.POST.get('location')
            required_skills = request.POST.get('required_skills')
            experience = request.POST.get('experience')
            education = request.POST.get('education')
            salary = request.POST.get('salary')
            description = request.POST.get('description')
            recruiter_profile = RecruiterProfile.objects.get(
            user=request.user)
            job = Job.objects.create(
                recruiter=recruiter_profile,
                title=title,
                company=company,
                jobtype=jobtype,
                lastdate=lastdate,
                location=location,
                
                experience=experience,
                education=education,
                salary=salary,
                description=description



            )
            skills = [
            skill.strip()
            for skill in required_skills.split(',')
            if skill.strip()
        ]

            for skill_name in skills:
                skill, created = Skill.objects.get_or_create(
                name=skill_name
                )
                job.required_skills.add(skill)
            return redirect('job_management')
    return render(
            request,
            'recruiter/job_post.html'
            
        )
@login_required
def job_management(request):
    recruiter_profile = RecruiterProfile.objects.get(
        user=request.user
    )

    jobs = Job.objects.filter(
    recruiter=recruiter_profile,
    is_active=True
    ).prefetch_related('required_skills')


    return render(
        request,
        'recruiter/job_management.html',
        {'jobs': jobs}
    )
@login_required
def delete_job(request, job_id):

    recruiter_profile = get_object_or_404(
        RecruiterProfile,
        user=request.user
    )

    job = get_object_or_404(
        Job,
        id=job_id,
        recruiter=recruiter_profile
    )

    if request.method == 'POST':

        job.is_active = False
        job.save(update_fields=['is_active'])

        # Check database value
        print(
            "JOB DELETED:",
            job.id,
            job.title,
            job.is_active
        )

        messages.success(
            request,
            'Job deleted successfully.'
        )

        return redirect('job_management')

    return redirect('job_management')

def edit_job(request, job_id):

    # Get the job
    job = get_object_or_404(Job, id=job_id)

    # Get logged-in recruiter's profile
    recruiter_profile = get_object_or_404(
        RecruiterProfile,
        user=request.user
    )

    # Security: only allow the owner/recruiter to edit this job
    if job.recruiter != recruiter_profile:
        return redirect('job_management')

    if request.method == 'POST':

        title = request.POST.get('title')
        company = request.POST.get('company')
        jobtype = request.POST.get('jobtype')
        lastdate = request.POST.get('lastdate')
        location = request.POST.get('location')
        required_skills = request.POST.get('required_skills')
        experience = request.POST.get('experience')
        education = request.POST.get('education')
        salary = request.POST.get('salary')
        description = request.POST.get('description')


        # Update Job details

        job.title = title
        job.company = company
        job.jobtype = jobtype
        job.lastdate = lastdate
        job.location = location
        job.experience = experience
        job.education = education
        job.salary = salary
        job.description = description

        job.save()


        # Update Skills

        skills = [
            skill.strip()
            for skill in required_skills.split(',')
            if skill.strip()
        ]


        # Remove old skills and add new skills

        job.required_skills.clear()


        for skill_name in skills:

            skill, created = Skill.objects.get_or_create(
                name=skill_name
            )

            job.required_skills.add(skill)


        return redirect('job_management')


    return render(
        request,
        'recruiter/edit_job.html',
        {
            'job': job
        }
    )


@login_required
def job_search(request):

    query = request.GET.get('q', '').strip()

    # All jobs
    jobs = Job.objects.filter(
    is_active=True
    ).prefetch_related(
    'required_skills'
    )


    # Search
    if query:
        jobs = jobs.filter(
            Q(title__icontains=query) |
            Q(company__icontains=query) |
            Q(location__icontains=query) |
            Q(jobtype__icontains=query) |
            Q(experience__icontains=query) |
            Q(education__icontains=query) |
            Q(required_skills__name__icontains=query)
        ).distinct()

    # Get logged-in candidate
    profile = get_object_or_404(
        CandidateProfile,
        user=request.user
    )

    # Jobs already applied by this candidate
    applied_job_ids = set(
        Application.objects.filter(
            candidate=profile
        ).values_list('job_id', flat=True)
    )

    return render(
        request,
        'candidate/job_search.html',
        {
            'jobs': jobs,
            'query': query,
            'applied_job_ids': applied_job_ids,
        }
    )


@login_required
def apply_job(request, job_id):

    # Get selected job
    job = get_object_or_404(
        Job,
        id=job_id,
        is_active=True
    )

    # Get logged-in candidate
    profile = get_object_or_404(
        CandidateProfile,
        user=request.user
    )

    # Check whether candidate already applied
    already_applied = Application.objects.filter(
        candidate=profile,
        job=job
    ).exists()

    if already_applied:
        messages.warning(
            request,
            "You have already applied for this job."
        )

        return redirect('jobsearch')

    # Submit application
    if request.method == 'POST':

        candidate_skills = {
        normalize_skill(skill.name)
        for skill in profile.skills.all()
        }

        job_skills = {
        normalize_skill(skill.name)
        for skill in job.required_skills.all()
        }


        if job_skills:
            matched_skills = candidate_skills.intersection(job_skills)

            match_percentage = round(
            (len(matched_skills) / len(job_skills)) * 100
            )
        else:
            match_percentage = 0
        Application.objects.create(
            candidate=profile,
            job=job,
            match_percentage=match_percentage,
            status='Applied'
            )


        messages.success(
            request,
            "Application submitted successfully!"
        )

        return redirect('candidate_dashboard')

    return render(
        request,
        'candidate/apply_job.html',
        {
            'job': job,
            'profile': profile,
        }
    )
@login_required
def my_applications(request):

    profile = get_object_or_404(
        CandidateProfile,
        user=request.user
    )

    candidate_skills = {
        normalize_skill(skill.name)
        for skill in profile.skills.all()
    }

    applications = (
        Application.objects
        .filter(
            candidate=profile,
            job__is_active=True
        )
        .select_related('job')
        .prefetch_related('job__required_skills')
        .order_by('-applied_at')
    )

    application_data = []

    for application in applications:

        job = application.job

        job_skills = {
            normalize_skill(skill.name)
            for skill in job.required_skills.all()
        }

        missing_skills = job_skills - candidate_skills

        application_data.append({
            'application': application,
            'missing_skills': missing_skills,
        })

    return render(
        request,
        'candidate/my_applications.html',
        {
            'application_data': application_data,
        }
    )

@login_required
def application_management(request):

    # Get logged-in recruiter
    recruiter_profile = get_object_or_404(
        RecruiterProfile,
        user=request.user
    )

    # ------------------------------------------------
    # 1. UPDATE APPLICATION STATUS
    # ------------------------------------------------

    if request.method == 'POST':

        app_id = request.POST.get('application_id')
        new_status = request.POST.get('status')

        # Valid statuses
        valid_statuses = {
            'Applied',
            'Shortlisted',
            'Selected',
            'Rejected'
        }

        # Check valid status
        if new_status not in valid_statuses:

            messages.error(
                request,
                "Invalid application status."
            )

            return redirect('application_management')

        # Get only applications belonging
        # to this recruiter
        application = get_object_or_404(
            Application,
            id=app_id,
            job__recruiter=recruiter_profile
        )

        # Update status
        application.status = new_status
        application.save()

        messages.success(
            request,
            f"{application.candidate.user.get_full_name()}'s "
            f"status updated to {new_status}!"
        )

        return redirect(
            'application_management'
        )

    # ------------------------------------------------
    # 2. GET CURRENT FILTER
    # ------------------------------------------------

    current_filter = request.GET.get(
        'status',
        'all'
    ).lower()

    # ------------------------------------------------
    # 3. GET ALL APPLICATIONS OF THIS RECRUITER
    # ------------------------------------------------

    all_applications = (
        Application.objects
        .filter(
            job__recruiter=recruiter_profile
        )
        .select_related(
            'candidate__user',
            'job'
        )
        .order_by('-applied_at')
    )

    # ------------------------------------------------
    # 4. COUNT APPLICATIONS
    # ------------------------------------------------

    counts = {
        'all': all_applications.count(),

        'shortlisted': all_applications.filter(
            status='Shortlisted'
        ).count(),

        'selected': all_applications.filter(
            status='Selected'
        ).count(),

        'rejected': all_applications.filter(
            status='Rejected'
        ).count(),
    }

    # ------------------------------------------------
    # 5. FILTER APPLICATIONS
    # ------------------------------------------------

    if current_filter == 'shortlisted':

        applications = all_applications.filter(
            status='Shortlisted'
        )

    elif current_filter == 'selected':

        applications = all_applications.filter(
            status='Selected'
        )

    elif current_filter == 'rejected':

        applications = all_applications.filter(
            status='Rejected'
        )

    else:

        # Default = all applications
        current_filter = 'all'

        applications = all_applications

    # ------------------------------------------------
    # 6. SEND DATA TO TEMPLATE
    # ------------------------------------------------

    return render(
        request,
        'recruiter/application_management.html',
        {
            'applications': applications,
            'counts': counts,
            'current_filter': current_filter,
        }
    )

@login_required
def candidate_management(request):
    recruiter_profile = get_object_or_404(
        RecruiterProfile,
        user=request.user
    )

    # Only candidates who applied to this recruiter's jobs
    candidates = CandidateProfile.objects.filter(
        application__job__recruiter=recruiter_profile
    ).distinct()

    # Search
    query = request.GET.get('q', '').strip()

    if query:
        candidates = candidates.filter(
            Q(user__first_name__icontains=query)
            | Q(user__last_name__icontains=query)
            | Q(user__email__icontains=query)
            | Q(skills__name__icontains=query)
        ).distinct()

    # Add match percentage for each candidate
    candidate_data = []

    for candidate in candidates:

        applications = Application.objects.filter(
            candidate=candidate,
            job__recruiter=recruiter_profile
        ).select_related('job')

        candidate_data.append({
            'candidate': candidate,
            'applications': applications
        })

    return render(
        request,
        'recruiter/candidate_management.html',
        {
            'candidate_data': candidate_data,
            'query': query,
        },
    )
@login_required
def recommended_jobs(request):

    # Logged-in candidate
    profile = get_object_or_404(
        CandidateProfile,
        user=request.user
    )

    # Only jobs applied by this candidate
    applications = (
        Application.objects
        .filter(
            candidate=profile, job__is_active=True,
            match_percentage__gt=50
        )
        .select_related('job')
        .prefetch_related('job__required_skills')
        .order_by('-match_percentage')
    )

    recommended_jobs = []

    # Candidate skills
    candidate_skills = set(
        skill.name.strip().lower()
        for skill in profile.skills.all()
    )

    for application in applications:

        job = application.job

        # Required skills of the job
        job_skills = set(
            skill.name.strip().lower()
            for skill in job.required_skills.all()
        )

        # Skills candidate doesn't have
        missing_skills = job_skills - candidate_skills

        recommended_jobs.append({
            'job': job,
            'match_percentage': application.match_percentage,
            'missing_skills': missing_skills,
            'status': application.status,
        })

    return render(
        request,
        'candidate/recommended_jobs.html',
        {
            'recommended_jobs': recommended_jobs,
        }
    )

def adminlogin(request):

    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None and user.is_staff:
            login(request, user)
            return redirect('admin_dashboard')

        else:
            messages.error(
                request,
                "Invalid credentials or not authorized as admin"
            )

    return render(request, 'adminlogin.html')
@login_required
def admin_dashboard(request):

    if not request.user.is_staff:
        messages.error(
            request,
            "You are not authorized to access this page."
        )
        return redirect('login')

    # ALL registered candidates
    candidates = (
        CandidateProfile.objects
        .select_related('user')
        .prefetch_related('skills')
        .all()
    )

    # ALL recruiters
    recruiters = (
        RecruiterProfile.objects
        .select_related('user')
        .all()
    )

    # ALL jobs
    jobs = (
        Job.objects
        .select_related('recruiter')
        .prefetch_related('required_skills')
        .all()
        .order_by('-id')
    )

    # Counts
    user_count = candidates.count()
    recruiter_count = recruiters.count()
    job_count = jobs.count()

    return render(
        request,
        'admin_dashboard.html',
        {
            'candidates': candidates,
            'recruiters': recruiters,
            'jobs': jobs,
            'user_count': user_count,
            'recruiter_count': recruiter_count,
            'job_count': job_count,
        }
    )
@login_required
@user_passes_test(lambda user: user.is_staff, login_url='adminlogin')
def admin_manage_users(request):

    # Search query
    query = request.GET.get('q', '').strip()

    # Get all candidate profiles
    candidates = (
        CandidateProfile.objects
        .select_related('user')
        .prefetch_related('skills')
        .all()
        .order_by('-id')
    )

    # Search candidates
    if query:
        candidates = candidates.filter(
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query) |
            Q(user__username__icontains=query) |
            Q(user__email__icontains=query) |
            Q(phone__icontains=query) |
            Q(location__icontains=query) |
            Q(education__icontains=query) |
            Q(skills__name__icontains=query)
        ).distinct()

    # Count matching active candidates
    active_count = candidates.filter(
        user__is_active=True
    ).count()

    # Count matching blocked candidates
    blocked_count = candidates.filter(
        user__is_active=False
    ).count()

    # Block / unblock candidate
    if request.method == 'POST':

        candidate_id = request.POST.get('candidate_id')
        action = request.POST.get('action')

        candidate = get_object_or_404(
            CandidateProfile.objects.select_related('user'),
            id=candidate_id
        )

        user = candidate.user

        # Prevent blocking admin accounts
        if user.is_staff or user.is_superuser:
            messages.error(
                request,
                'Admin accounts cannot be blocked here.'
            )
            return redirect('manage_users')

        if action == 'block':

            user.is_active = False
            user.save(update_fields=['is_active'])

            messages.success(
                request,
                f'{user.get_full_name() or user.username} blocked successfully.'
            )

        elif action == 'unblock':

            user.is_active = True
            user.save(update_fields=['is_active'])

            messages.success(
                request,
                f'{user.get_full_name() or user.username} unblocked successfully.'
            )

        else:
            messages.error(request, 'Invalid action.')

        return redirect('admin_manage_users')

    # Render template
    return render(
        request,
        'admin_manage_users.html',
        {
            'candidates': candidates,
            'query': query,
            'active_count': active_count,
            'blocked_count': blocked_count,
        }
    )

@staff_member_required
@require_http_methods(["GET", "POST"])
def admin_manage_recruiters(request):
    if request.method == "POST":
        recruiter_id = request.POST.get("recruiter_id")
        action = request.POST.get("action")

        recruiter = get_object_or_404(
            RecruiterProfile.objects.select_related("user"),
            id=recruiter_id,
        )

        # Never allow this view to block or unblock admin accounts.
        if recruiter.user.is_staff or recruiter.user.is_superuser:
            messages.error(request, "Admin accounts cannot be modified here.")
            return redirect("admin_manage_recruiters")

        if action == "block":
            recruiter.user.is_active = False
            recruiter.user.save(update_fields=["is_active"])
            messages.success(request, "Recruiter account blocked successfully.")

        elif action == "unblock":
            recruiter.user.is_active = True
            recruiter.user.save(update_fields=["is_active"])
            messages.success(request, "Recruiter account unblocked successfully.")

        else:
            messages.error(request, "Invalid action.")

        return redirect("admin_manage_recruiters")

    query = request.GET.get("q", "").strip()

    recruiters = RecruiterProfile.objects.select_related("user").all()

    if query:
        recruiters = recruiters.filter(
            Q(user__username__icontains=query)
            | Q(user__first_name__icontains=query)
            | Q(user__last_name__icontains=query)
            | Q(user__email__icontains=query)
            | Q(company_name__icontains=query)
            | Q(phone__icontains=query)
            | Q(designation__icontains=query)
            | Q(location__icontains=query)
        )

    recruiters = recruiters.order_by("id")

    # Count accounts in the complete recruiter list, not just search results.
    all_recruiters = RecruiterProfile.objects.filter(
        user__is_staff=False,
        user__is_superuser=False,
    )

    active_count = all_recruiters.filter(user__is_active=True).count()
    blocked_count = all_recruiters.filter(user__is_active=False).count()

    context = {
        "recruiters": recruiters,
        "active_count": active_count,
        "blocked_count": blocked_count,
        "query": query,
    }

    return render(request, "admin_manage_recruiters.html", context)

@staff_member_required
@require_http_methods(["GET", "POST"])
def admin_manage_jobs(request):

    # Delete job
    if request.method == "POST":
        job_id = request.POST.get("job_id")

        job = get_object_or_404(Job, id=job_id)
        job_title = job.title

        job.delete()

        messages.success(
            request,
            f'"{job_title}" deleted successfully.'
        )

        return redirect('admin_manage_jobs')

    # Search jobs
    query = request.GET.get("q", "").strip()

    jobs = Job.objects.select_related(
        "recruiter",
        "recruiter__user"
    ).all()

    if query:
        jobs = jobs.filter(
            Q(title__icontains=query)
            | Q(company__icontains=query)
            | Q(location__icontains=query)
            | Q(recruiter__user__username__icontains=query)
            | Q(recruiter__user__email__icontains=query)
        )

    jobs = jobs.order_by("-id")

    # Statistics
    total_jobs = Job.objects.count()

    active_jobs = Job.objects.filter(
        is_active=True
    ).count()

    recruiter_count = Job.objects.values(
        "recruiter_id"
    ).distinct().count()

    context = {
        "jobs": jobs,
        "query": query,
        "total_jobs": total_jobs,
        "active_jobs": active_jobs,
        "recruiter_count": recruiter_count,
    }

    return render(request, "admin_manage_jobs.html", context)

def logoutcandidate(request):
    logout(request)
    return redirect('login')
def logoutrecruiter(request):
    logout(request)
    return redirect('login_recruiter')
def logoutadmin(request):
    logout(request)
    return redirect('adminlogin')
