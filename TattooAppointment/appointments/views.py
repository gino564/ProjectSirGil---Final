from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.db.models import Count, Q
from django.utils import timezone
from django.contrib import messages
from .models import Appointment, TattooRequest, Design, Artist


@login_required
def dashboard(request):
    """Client dashboard landing page"""
    user = request.user

    # Get statistics
    completed_sessions = Appointment.objects.filter(
        client=user,
        status='completed'
    ).count()

    upcoming_appointments = Appointment.objects.filter(
        client=user,
        scheduled_date__gte=timezone.now(),
        status__in=['pending', 'confirmed']
    ).count()

    total_requests = TattooRequest.objects.filter(client=user).count()

    approved_designs = Design.objects.filter(
        tattoo_request__client=user
    ).count()

    # Get upcoming appointments (next 5)
    upcoming_appointments_list = Appointment.objects.filter(
        client=user,
        scheduled_date__gte=timezone.now(),
        status__in=['pending', 'confirmed']
    ).select_related('artist', 'tattoo_request')[:5]

    # Get recent tattoo requests (last 6)
    tattoo_requests = TattooRequest.objects.filter(
        client=user
    ).select_related('artist')[:6]

    context = {
        'stats': {
            'completed_sessions': completed_sessions,
            'upcoming_appointments': upcoming_appointments,
            'total_requests': total_requests,
            'approved_designs': approved_designs,
        },
        'upcoming_appointments': upcoming_appointments_list,
        'tattoo_requests': tattoo_requests,
    }

    return render(request, 'appointments/landing.html', context)


class AppointmentListView(LoginRequiredMixin, ListView):
    """List all appointments for the client"""
    model = Appointment
    template_name = 'appointments/appointment_list.html'
    context_object_name = 'appointments'
    paginate_by = 10

    def get_queryset(self):
        queryset = Appointment.objects.filter(
            client=self.request.user
        ).select_related('artist', 'tattoo_request').order_by('-scheduled_date')

        # Apply filter
        filter_type = self.request.GET.get('filter', 'all')

        if filter_type == 'upcoming':
            queryset = queryset.filter(
                scheduled_date__gte=timezone.now(),
                status__in=['pending', 'confirmed']
            )
        elif filter_type == 'pending':
            queryset = queryset.filter(status='pending')
        elif filter_type == 'confirmed':
            queryset = queryset.filter(status='confirmed')
        elif filter_type == 'completed':
            queryset = queryset.filter(status='completed')
        elif filter_type == 'cancelled':
            queryset = queryset.filter(status='cancelled')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = self.request.GET.get('filter', 'all')
        return context


class TattooRequestDetailView(LoginRequiredMixin, DetailView):
    """View details of a tattoo request"""
    model = TattooRequest
    template_name = 'appointments/request_detail.html'
    context_object_name = 'request'

    def get_queryset(self):
        return TattooRequest.objects.filter(
            client=self.request.user
        ).select_related('artist').prefetch_related('designs')


class DesignListView(LoginRequiredMixin, ListView):
    """List all approved designs for the client"""
    model = Design
    template_name = 'appointments/design_list.html'
    context_object_name = 'designs'

    def get_queryset(self):
        return Design.objects.filter(
            tattoo_request__client=self.request.user
        ).select_related('artist', 'tattoo_request').order_by('-created_at')


class CreateAppointmentView(LoginRequiredMixin, CreateView):
    """Book a new appointment"""
    model = Appointment
    template_name = 'appointments/create_appointment.html'
    fields = ['artist', 'tattoo_request', 'scheduled_date', 'duration_hours', 'notes']
    success_url = reverse_lazy('appointments:dashboard')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)

        # Limit tattoo_request choices to user's requests
        form.fields['tattoo_request'].queryset = TattooRequest.objects.filter(
            client=self.request.user,
            status='approved'
        )

        # Add helpful labels and help text
        form.fields['artist'].help_text = 'Select your preferred artist'
        form.fields['tattoo_request'].help_text = 'Choose an approved design (optional)'
        form.fields['scheduled_date'].help_text = 'Preferred date and time'
        form.fields['duration_hours'].help_text = 'Estimated session duration'

        # Make tattoo_request optional
        form.fields['tattoo_request'].required = False

        return form

    def form_valid(self, form):
        form.instance.client = self.request.user
        form.instance.status = 'pending'
        messages.success(
            self.request,
            'Your appointment request has been submitted and is awaiting approval.'
        )
        return super().form_valid(form)


class CreateTattooRequestView(LoginRequiredMixin, CreateView):
    """Submit a new tattoo request/enquiry"""
    model = TattooRequest
    template_name = 'appointments/create_request.html'
    fields = ['title', 'description', 'reference_image']
    success_url = reverse_lazy('appointments:dashboard')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)

        # Add helpful labels and help text
        form.fields['title'].help_text = 'Give your tattoo idea a title'
        form.fields['description'].help_text = 'Describe your tattoo concept in detail (placement, size, style, colors, etc.)'
        form.fields['reference_image'].help_text = 'Upload a reference image (optional)'
        form.fields['reference_image'].required = False

        return form

    def form_valid(self, form):
        form.instance.client = self.request.user
        form.instance.status = 'submitted'
        messages.success(
            self.request,
            'Your tattoo request has been submitted! An artist will review it soon.'
        )
        return super().form_valid(form)


@login_required
def cancel_appointment(request, pk):
    """Cancel an appointment"""
    appointment = get_object_or_404(
        Appointment,
        pk=pk,
        client=request.user,
        status__in=['pending', 'confirmed']
    )

    if request.method == 'POST':
        appointment.status = 'cancelled'
        appointment.save()
        messages.success(request, 'Your appointment has been cancelled.')
        return redirect('appointments:manage_appointments')

    return render(request, 'appointments/cancel_appointment.html', {
        'appointment': appointment
    })


@login_required
def reschedule_appointment(request, pk):
    """Reschedule an appointment"""
    appointment = get_object_or_404(
        Appointment,
        pk=pk,
        client=request.user,
        status='confirmed'
    )

    # For simplicity, we'll redirect to a form
    # In a real app, this would be a proper form view
    messages.info(request, 'Please contact your artist to reschedule.')
    return redirect('appointments:manage_appointments')
