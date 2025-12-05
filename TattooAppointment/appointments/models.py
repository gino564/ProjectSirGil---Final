from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Artist(models.Model):
    """Tattoo artist model"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    specialization = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username


class TattooRequest(models.Model):
    """Client's tattoo design request"""
    STATUS_CHOICES = [
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]

    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tattoo_requests')
    artist = models.ForeignKey(Artist, on_delete=models.SET_NULL, null=True, blank=True, related_name='requests')
    title = models.CharField(max_length=200)
    description = models.TextField()
    reference_image = models.ImageField(upload_to='tattoo_requests/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='submitted')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.client.username}"


class Appointment(models.Model):
    """Tattoo session appointment"""
    STATUS_CHOICES = [
        ('pending', 'Awaiting Approval'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]

    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments')
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name='appointments')
    tattoo_request = models.ForeignKey(TattooRequest, on_delete=models.SET_NULL, null=True, blank=True, related_name='appointments')
    scheduled_date = models.DateTimeField()
    duration_hours = models.DecimalField(max_digits=3, decimal_places=1, default=2.0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['scheduled_date']

    def __str__(self):
        return f"{self.client.username} - {self.scheduled_date.strftime('%Y-%m-%d %H:%M')}"

    @property
    def is_upcoming(self):
        return self.scheduled_date > timezone.now() and self.status != 'cancelled'


class Design(models.Model):
    """Approved tattoo design"""
    tattoo_request = models.ForeignKey(TattooRequest, on_delete=models.CASCADE, related_name='designs')
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name='designs')
    image = models.ImageField(upload_to='designs/')
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Design for {self.tattoo_request.title}"
