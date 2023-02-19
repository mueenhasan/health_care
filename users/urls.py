from django.contrib.auth import views
from django.urls import path

from .views import (
    DoctorSignUpView,
    PatientSignUpView,
    DoctorAppointmentListView,
    PatientAppointmentListView,
    AppointmentCreateView,
    AppointmentUpdateView,
    load_doctors
)

urlpatterns = [
    path('doctor-signup', DoctorSignUpView.as_view(), name='doctor-signup'),
    path('patient-signup', PatientSignUpView.as_view(), name='patient-signup'),
    path('doctor-appointments', DoctorAppointmentListView.as_view(), name='doctor-appointments'),
    path('patient-appointments', PatientAppointmentListView.as_view(), name='patient-appointments'),
    path('book-appointment', AppointmentCreateView.as_view(), name='book-appointment'),
    path('ajax/load-doctors/', load_doctors, name='ajax_load_doctors'),
    path('appointments/<int:pk>', AppointmentUpdateView.as_view(), name='update-appointment'),
    path(
        'login',
        views.LoginView.as_view(
            template_name="registeration/login.html"
        ),
        name='login'
    ),
    path('logout', views.LogoutView.as_view(), name='logout')
]