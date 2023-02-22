from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError


class User(AbstractUser):
    is_patient = models.BooleanField(default=False)
    is_doctor = models.BooleanField(default=False)


class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    name = models.CharField(max_length=100)
    qualifications = models.CharField(max_length=20, null=True)
    expertise = models.CharField(max_length=50)
    hospital = models.CharField(max_length=50)


class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    age = models.PositiveIntegerField()
    phone = models.CharField(max_length=15)
    gender = models.CharField(max_length=6, null=True, blank=True)
    blood_group = models.CharField(max_length=5, null=True, blank=True)


class Appointment(models.Model):
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='doctor_appointments')
    date = models.DateField()
    time = models.TimeField()
    hemoglobin = models.FloatField()
    bmi = models.FloatField()
    platelets = models.IntegerField()
    blood_sugar = models.FloatField()
    blood_pressure = models.FloatField()
    symptoms = models.TextField(blank=True)
    diagnosis = models.TextField(blank=True)
    prescription = models.TextField(blank=True)

    class Meta:
        unique_together = (('date', 'time', 'doctor'),)

    def save(self, *args, **kwargs):
        current_month = self.date.month
        appointments_this_month = Appointment.objects.filter(
            doctor=self.doctor,
            date__month=current_month
        ).count()
        if appointments_this_month >= 15:
            raise ValidationError('Doctor is busy this month you can have appointment for another month!')
        super().save(*args, **kwargs)
