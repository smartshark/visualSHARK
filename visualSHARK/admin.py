from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from .models import CommitGraph, CommitLabelField, ProjectStats, VSJob, VSJobType, UserProfile, IssueValidation, \
    IssueValidationUser, ProjectAttributes, LeaderboardSnapshot, CorrectionIssue, ChangeTypeLabel, TechnologyLabelCommit, TechnologyLabel


def activate_user(modeladmin, news, queryset):
    queryset.update(is_active=True)
activate_user.short_description = u"Activate selected Users"


def deactivate_user(modeladmin, news, queryset):
    queryset.update(is_active=False)
deactivate_user.short_description = u"Deactivate selected Users"


def remove_label(modeladmin, news, queryset):
    queryset.update(has_label=False)
remove_label.short_description = u"Remove label"


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


class ChangeTypeLabelAdmin(admin.ModelAdmin):
    actions = [remove_label]
    list_display = ('user', 'project_name', 'revision_hash', 'has_label', 'is_perfective', 'is_corrective', 'changed_at')
    list_filter = ('user', 'has_label', 'is_perfective', 'is_corrective')
    search_fields = ('user',)


class TechnologyLabelCommitAdmin(admin.ModelAdmin):
    list_display = ('user', 'project_name', 'revision_hash', 'is_labeled', 'changed_at')
    list_filter = ('user', 'project_name', 'is_labeled')
    search_fields = ('user',)


class TechnologyLabelAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'created_by')


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
admin.site.register(ChangeTypeLabel, ChangeTypeLabelAdmin)
admin.site.register(TechnologyLabelCommit, TechnologyLabelCommitAdmin)
admin.site.register(TechnologyLabel, TechnologyLabelAdmin)
