import datetime
from datetime import timedelta
from django import forms
from django.contrib.auth.forms import UserCreationForm
from users.models import Doctor, Patient, User
from .models import Appointment


class PatientSignUpForm(UserCreationForm):
    age = forms.IntegerField()
    phone = forms.CharField(max_length=15)
    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'),
        ('B+', 'B+'),
        ('O+', 'O+'),
        ('AB+', 'AB+'),
        ('A-', 'A-'),
        ('B-', 'B-'),
        ('O-', 'O-'),
        ('AB-', 'AB-'),
    ]
    blood_group = forms.ChoiceField( choices=BLOOD_GROUP_CHOICES, widget=forms.Select )
    gender = forms.ChoiceField (choices=[('Male','Male'), ('Female','Female'), ('Other', 'Other')], widget=forms.widgets.Select)
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'gender', 'blood_group', 'age' ,'phone', 'username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_patient = True
        if commit:
            user.save()
        Patient.objects.create(
            user=user,
            gender=self.cleaned_data.get('gender'),
            blood_group=self.cleaned_data.get('blood_group'),
            age=self.cleaned_data.get('age'),
            phone=self.cleaned_data.get('phone')
        )
        return user


class DoctorSignUpForm(UserCreationForm):
    QUALIFICATIONS_CHOICES= [
        ('MBBS', 'MBBS'),
        ('FCPS', 'FCPS'),
        ('FRCP', 'FRCP'),
        ('FACC', 'FACC'),
    ]
    qualifications = forms.ChoiceField(choices=QUALIFICATIONS_CHOICES, widget=forms.Select, required=True)
    
    EXPERTISE_CHOICES= [
        ('Cardiology', 'Cardiology'),
        ('Rheumatology', 'Rheumatology'),
        ('Nephrology', 'Nephrology'),
        ('Endocrinology', 'Endocrinology'),
        ('Diabetes', 'Diabetes'),
        ('Geriatric Medicine', 'Geriatric Medicine'),
    ]
    expertise = forms.ChoiceField(choices=EXPERTISE_CHOICES, widget=forms.Select, required=True)
    hospital = forms.CharField(max_length=50)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'hospital', 'password1', 'password2', 'qualifications', 'expertise']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_doctor = True
        if commit:
            user.save()
        Doctor.objects.create(
            user=user,
            qualifications=self.cleaned_data.get('qualifications'),
            expertise=self.cleaned_data.get('expertise'),
            hospital=self.cleaned_data.get('hospital'),
            name=f"{self.cleaned_data.get('first_name')} {self.cleaned_data.get('last_name')}"
        )
        return user


class AppointmentForm(forms.ModelForm):
    date = forms.DateField(widget=forms.SelectDateWidget(years=range(datetime.date.today().year, datetime.date.today().year + 2)), initial=datetime.date.today)
    time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time', 'min': '09:00', 'max': '18:00'}))
    hemoglobin = forms.IntegerField(min_value =8, max_value=20)
    bmi = forms.FloatField(min_value=10.0, max_value=50.0)
    platelets = forms.IntegerField(min_value=100000, max_value=800000)
    blood_sugar = forms.IntegerField(min_value=50, max_value=300)
    blood_pressure = forms.IntegerField(min_value= 50, max_value=400)
    
    class Meta:
        model = Appointment
        fields = ['doctor', 'date', 'time', 'hemoglobin', 'bmi', 'platelets', 'blood_sugar', 'blood_pressure', 'symptoms']
        widgets = {
            'time': forms.TimeInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['doctor'].queryset = User.objects.filter(is_doctor=True)
        self.fields['time'].widget.attrs.update({'class': 'form-control'})

    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get("date")
        time = cleaned_data.get("time")
        doctor = cleaned_data.get("doctor")
        selected_date_time = datetime.datetime(year=date.year, month=date.month, day=date.day, hour=time.hour, minute=time.minute)
        if datetime.datetime.now() > selected_date_time:
            raise forms.ValidationError("Selected time slot is invalid")
        min_time = (selected_date_time - timedelta(minutes=30)).time()
        max_time = (selected_date_time + timedelta(minutes=30)).time()
        appointment = Appointment.objects.filter(time__gte=min_time, time__lte=max_time, date=date, doctor=doctor).first()
        if appointment:
            raise forms.ValidationError("Selected time slot is unavailable")
        return cleaned_data


class AppointmentUpdateForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['symptoms', 'diagnosis', 'prescription']
