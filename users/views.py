from ajax_datatable.views import AjaxDatatableView
from django.contrib.auth import authenticate, login
from django.http import HttpResponseForbidden
from django.views.generic import CreateView, ListView, CreateView, UpdateView
from .forms import PatientSignUpForm, DoctorSignUpForm, AppointmentForm, AppointmentUpdateForm
from .models import Appointment, Doctor, User

from django.shortcuts import render, redirect
from django.urls import reverse


class DoctorSignUpView(CreateView):
    template_name = 'doctor_signup.html'

    def get(self, request):
        if request.user.is_anonymous:
            form = DoctorSignUpForm()
            context = {'form': form}
            return render(request, self.template_name, context)
        return redirect('index')

    def post(self, request):
        form = DoctorSignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password2')
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('index')
        else:
            return render(request, self.template_name, {'form': form})


class PatientSignUpView(CreateView):
    template_name = 'patient_signup.html'

    def get(self, request):
        if request.user.is_anonymous:
            form = PatientSignUpForm()
            context = {'form': form}
            return render(request, self.template_name, context)
        return redirect('index')

    def post(self, request):
        form = PatientSignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password2')
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('index')
        else:
            return render(request, self.template_name, {'form': form})


class AppointmentCreateView(CreateView):
    model = Appointment
    form_class = AppointmentForm
    template_name = 'appointments/appointment_form.html'
    qualifications = Doctor.objects.values_list('qualifications', flat=True).distinct().order_by('qualifications')
    expertise = Doctor.objects.values_list('expertise', flat=True).distinct().order_by('expertise')
    doctors = User.objects.filter(is_doctor=True).order_by('first_name', 'last_name')

    def get(self, request):
        form = self.form_class()
        return render(
            request,
            self.template_name,
            {
                'form': form,
                "doctors": self.doctors,
                "expertise": self.expertise,
                "qualifications": self.qualifications,
                "selected_doctor": None
        })

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.patient = request.user
            appointment.save()
            return redirect('patient-appointments')
        selected_doctor = form.cleaned_data.get('doctor').id
        return render(
            request,
            self.template_name, {
                'form': form,
                "doctors": self.doctors,
                "expertise": self.expertise,
                "qualifications": self.qualifications,
                "selected_doctor": selected_doctor
        })


def load_doctors(request):
    expertise = request.GET.get('expertise')
    qualifications = request.GET.get('qualifications')
    if expertise and qualifications:
        doctors = User.objects.filter(doctor__expertise=expertise, doctor__qualifications=qualifications).order_by('first_name', 'last_name')
    elif expertise:
        doctors = User.objects.filter(doctor__expertise=expertise).order_by('first_name', 'last_name')
    else:
        doctors = User.objects.filter(doctor__qualifications=qualifications).order_by('first_name', 'last_name')
    return render(request, 'appointments/doctors_dropdown_options.html', {'doctors': doctors})


class DoctorAppointmentListView(ListView):
    model = Appointment
    template_name = 'appointments/doctor_appointment_list.html'
    context_object_name = 'appointments'

    def get_queryset(self):
        return Appointment.objects.filter(doctor=self.request.user)


class DoctorAppointmentsDatatableView(AjaxDatatableView):

    model = Appointment
    title = 'Appointments'
    initial_order = [["date", "desc"], ]
    length_menu = [[10, 20, 50, 100, -1], [10, 20, 50, 100, 'all']]
    search_values_separator = '+'

    column_defs = [
        AjaxDatatableView.render_row_tools_column_def(),
        {'name': 'id', 'visible': False, },
        {'name': 'patient', 'foreign_field': 'patient__first_name', 'visible': True, },
        {'name': 'date', 'visible': True, },
        {'name': 'time', 'visible': True, },
        {'name': 'blood_sugar', 'visible': True, },
        {'name': 'blood_pressure', 'visible': True, },
        {'name': 'hemoglobin', 'visible': True, },
        {'name': 'bmi', 'visible': True, },
        {'name': 'platelets', 'visible': True, },
        {'name': 'symptoms', 'visible': True, },
        {'name': 'diagnosis', 'visible': True, },
        {'name': 'prescription', 'visible': True, },
        {'name': 'edit', 'title': 'Edit', 'placeholder': True, 'searchable': False, 'orderable': False, },
    ]

    def customize_row(self, row, obj):
        row['edit'] = """
            <a href="/user/appointments/{}" class="btn-sm btn btn-success" type="button">
               Edit
            </a>
        """.format(obj.id)
        row['patient'] = "{} {}".format(obj.patient.first_name, obj.patient.last_name)
        return


class PatientAppointmentListView(ListView):
    model = Appointment
    template_name = 'appointments/patient_appointment_list.html'
    context_object_name = 'appointments'

    def get_queryset(self):
        return Appointment.objects.filter(patient=self.request.user)


class AppointmentUpdateView(UpdateView):
    model = Appointment
    form_class = AppointmentUpdateForm
    template_name = 'appointments/appointment_update.html'

    def form_valid(self, form):
        if not self.request.user.is_doctor:
            return HttpResponseForbidden()
        form.instance.doctor = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('doctor_appointments')
