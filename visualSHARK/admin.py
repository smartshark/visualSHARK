from django.contrib import admin

from .models import CommitGraph, CommitLabelField, ProjectStats, VSJob, VSJobType, UserProfile


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


admin.site.register(CommitGraph, CommitGraphAdmin)
admin.site.register(CommitLabelField, CommitLabelFieldAdmin)
admin.site.register(ProjectStats, ProjectStatsAdmin)
admin.site.register(VSJob, VSJobAdmin)
admin.site.register(VSJobType, VSJobTypeAdmin)
admin.site.register(UserProfile)
