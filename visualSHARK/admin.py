from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from .models import CommitGraph, CommitLabelField, ProjectStats, VSJob, VSJobType, UserProfile, IssueValidation, \
    IssueValidationUser, ProjectAttributes, LeaderboardSnapshot, CorrectionIssue, PMDIssue


def activate_user(modeladmin, news, queryset):
    queryset.update(is_active=True)
activate_user.short_description = u"Activate selected Users"


def deactivate_user(modeladmin, news, queryset):
    queryset.update(is_active=False)
deactivate_user.short_description = u"Deactivate selected Users"


class CustomUserAdmin(UserAdmin):
    actions = [activate_user, deactivate_user]


class CorrectionIssueAdmin(admin.ModelAdmin):
    list_display = ('user', 'external_id', 'is_corrected', 'is_skipped')
    list_filter = ('user', 'is_corrected', 'is_skipped')
    search_fields = ('user',)


class CommitGraphAdmin(admin.ModelAdmin):
    list_display = ('title', 'vcs_system_id', 'directed_pickle', 'last_updated')


class CommitLabelFieldAdmin(admin.ModelAdmin):
    list_display = ('approach', 'name')


class ProjectStatsAdmin(admin.ModelAdmin):
    list_display = ('project_name', 'stats_date')


class VSJobTypeAdmin(admin.ModelAdmin):
    list_display = ('ident', 'name')


class VSJobAdmin(admin.ModelAdmin):
    list_display = ('job_type', 'requested_by', 'created_at', 'executed_at')


class IssueValidationAdmin(admin.ModelAdmin):
    list_display = ('project_id', 'issue_system_id', 'issue_id', 'issue_type', 'issue_type_unified', 'linked', 'resolution')
    list_filter = ('linked', 'resolution', 'issue_type_unified')
    search_fields = ('issue_id',)


class IssueValidationUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'issue_validation', 'label')
    list_filter = ('user',)


class LeaderboardSnapshotAdmin(admin.ModelAdmin):
    list_display = ('created_at',)


class PMDIssueAdmin(admin.ModelAdmin):
    list_display = ('user', 'external_id', 'is_validated', 'is_skipped')
    list_filter = ('user', 'is_validated', 'is_skipped')
    search_fields = ('user',)


# custom user admin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

admin.site.register(CommitGraph, CommitGraphAdmin)
admin.site.register(CommitLabelField, CommitLabelFieldAdmin)
admin.site.register(ProjectStats, ProjectStatsAdmin)
admin.site.register(VSJob, VSJobAdmin)
admin.site.register(VSJobType, VSJobTypeAdmin)
admin.site.register(UserProfile)
admin.site.register(IssueValidation, IssueValidationAdmin)
admin.site.register(IssueValidationUser, IssueValidationUserAdmin)
admin.site.register(ProjectAttributes)
admin.site.register(LeaderboardSnapshot, LeaderboardSnapshotAdmin)
admin.site.register(CorrectionIssue, CorrectionIssueAdmin)
admin.site.register(PMDIssue, PMDIssueAdmin)
