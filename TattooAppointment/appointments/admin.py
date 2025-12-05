from django.contrib import admin
from .models import Artist, TattooRequest, Appointment, Design


@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ['user', 'specialization']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'specialization']


@admin.register(TattooRequest)
class TattooRequestAdmin(admin.ModelAdmin):
    list_display = ['title', 'client', 'artist', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['title', 'client__username', 'artist__user__username']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['client', 'artist', 'scheduled_date', 'duration_hours', 'status']
    list_filter = ['status', 'scheduled_date']
    search_fields = ['client__username', 'artist__user__username']
    date_hierarchy = 'scheduled_date'
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Design)
class DesignAdmin(admin.ModelAdmin):
    list_display = ['tattoo_request', 'artist', 'created_at']
    list_filter = ['created_at']
    search_fields = ['tattoo_request__title', 'artist__user__username']
    date_hierarchy = 'created_at'
