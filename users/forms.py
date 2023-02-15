import datetime
from select import select
from django import forms
from django.contrib.auth.forms import UserCreationForm
from users.models import User
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
        fields = ['first_name', 'last_name', 'gender','blood_group', 'age' ,'phone', 'username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_patient = True
        if commit:
            user.save()
        return user


class DoctorSignUpForm(UserCreationForm):
    QUALIFICATIONS_CHOICES= [
        ('MBBS', 'MBBS'),
        ('FCPS', 'FCPS'),
        ('FRCP', 'FRCP'),
        ('FACC', 'FACC'),
    ]
    qualifications =forms.ChoiceField(choices=QUALIFICATIONS_CHOICES, widget=forms.Select)
    
    EXPERTISE_CHOICES= [
        ('Cardiology', 'Cardiology'),
        ('Rheumatology', 'Rheumatology'),
        ('Nephrology', 'Nephrology'),
        ('Endocrinology', 'Endocrinology'),
        ('Diabetes', 'Diabetes'),
        ('Geriatric Medicine', 'Geriatric Medicine'),
    ]
    expertise = forms.ChoiceField(choices=EXPERTISE_CHOICES, widget=forms.Select )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2', 'qualifications', 'expertise']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_doctor = True
        if commit:
            user.save()
        return user


class AppointmentForm(forms.ModelForm):
    date = forms.DateField(widget=forms.SelectDateWidget(years=range(datetime.date.today().year, datetime.date.today().year + 2)), initial=datetime.date.today)
    time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time', 'min': '09:00', 'max': '18:00'}))
    blood_group= forms.ChoiceField (choices=PatientSignUpForm.BLOOD_GROUP_CHOICES)
    
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]
    gender= forms.ChoiceField(choices= GENDER_CHOICES)
    hemoglobin = forms.IntegerField(min_value =8, max_value = 20)
    bmi = forms.FloatField (min_value=10.0, max_value=50.0)
    platelets = forms.IntegerField(min_value= 100000, max_value=800000)
    blood_sugar = forms.IntegerField(min_value=50, max_value=300)
    blood_pressure = forms.IntegerField(min_value= 50, max_value= 400)
    
    class Meta:
        model = Appointment
        fields = ['doctor', 'date', 'time','gender', 'blood_group', 'hemoglobin', 'bmi', 'platelets', 'blood_sugar', 'blood_pressure', 'symptoms']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['doctor'].queryset = User.objects.filter(is_doctor=True)

    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get("date")
        time = cleaned_data.get("time")
        doctor = cleaned_data.get("doctor")

        appointment = Appointment.objects.filter(date=date, time=time, doctor=doctor).first()
        if appointment:
            raise forms.ValidationError("This appointment has already been taken, please choose another date and time")
        return cleaned_data


class AppointmentUpdateForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['symptoms', 'diagnosis', 'prescription']
