from django.contrib import admin
from django.contrib import admin
from .models import Application, CandidateProfile, Job, RecruiterProfile, Skill


@admin.register(RecruiterProfile)
class RecruiterAdmin(admin.ModelAdmin):
    list_display = ('user', 'company', 'phone')
    search_fields = ('user__username', 'user__email', 'company_name')


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(CandidateProfile)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone')
    search_fields = ('user__username', 'user__email')
    filter_horizontal = ('skills',)


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'recruiter', 'location', 'created_at', 'is_active')
    list_filter = ('is_active', 'created_at', 'location')
    search_fields = ('title', 'description', 'recruiter__company_name')
    filter_horizontal = ('required_skills',)


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('job', 'candidate', 'status', 'applied_at')
    list_filter = ('status', 'applied_at')
    search_fields = (
        'job__title',
        'candidate__user__username',
        'candidate__user__email',
    )


