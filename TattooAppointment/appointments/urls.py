from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Appointments
    path('appointments/', views.AppointmentListView.as_view(), name='manage_appointments'),
    path('appointments/book/', views.CreateAppointmentView.as_view(), name='book_session'),
    path('appointments/<int:pk>/cancel/', views.cancel_appointment, name='cancel_appointment'),
    path('appointments/<int:pk>/reschedule/', views.reschedule_appointment, name='reschedule_appointment'),

    # Tattoo Requests
    path('requests/new/', views.CreateTattooRequestView.as_view(), name='new_enquiry'),
    path('requests/<int:pk>/', views.TattooRequestDetailView.as_view(), name='request_detail'),

    # Designs
    path('designs/', views.DesignListView.as_view(), name='view_designs'),
]
