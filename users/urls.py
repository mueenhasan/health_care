from django.contrib.auth import views
from django.urls import path

from .views import (
    DoctorSignUpView,
    PatientSignUpView,
    DoctorAppointmentListView,
    PatientAppointmentListView,
    AppointmentCreateView,
    AppointmentUpdateView
)

urlpatterns = [
    path('doctor_signup', DoctorSignUpView.as_view(), name='doctor_signup'),
    path('patient_signup', PatientSignUpView.as_view(), name='patient_signup'),
    path('doctor_appointments', DoctorAppointmentListView.as_view(), name='doctor_appointments'),
    path('patient_appointments', PatientAppointmentListView.as_view(), name='patient_appointments'),
    path('book_appointment', AppointmentCreateView.as_view(), name='book_appointment'),
    path('appointments/<int:pk>/update', AppointmentUpdateView.as_view(), name='update_appointment'),
    path(
        'login',
        views.LoginView.as_view(
            template_name="registeration/login.html"
        ),
        name='login'
    ),
    path('logout', views.LogoutView.as_view(), name='logout')
]