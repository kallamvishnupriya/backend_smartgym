from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


# =========================
# CUSTOM USER
# =========================
class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('trainer', 'Trainer'),
        ('member', 'Member'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.username} ({self.role})"


# =========================
# MEMBERSHIP
# =========================
class Membership(models.Model):
    member = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'member'}
    )
    start_date = models.DateField()
    end_date = models.DateField()
    active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if self.end_date < timezone.now().date():
            self.active = False
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.member.username} Membership"


# =========================
# WORKOUT PLAN
# =========================
class WorkoutPlan(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    trainer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='trainer_workouts',
        limit_choices_to={'role': 'trainer'}
    )

    member = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='member_workouts',
        limit_choices_to={'role': 'member'}
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.member.username}"


# =========================
# WORKOUT LOG
# =========================
class WorkoutLog(models.Model):
    member = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'member'}
    )
    workout_plan = models.ForeignKey(WorkoutPlan, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    duration_minutes = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.member.username} - {self.workout_plan.name}"


# =========================
# DIET PLAN
# =========================
class DietPlan(models.Model):
    trainer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='trainer_diets',
        limit_choices_to={'role': 'trainer'}
    )

    member = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='member_diets',
        limit_choices_to={'role': 'member'}
    )

    calories = models.PositiveIntegerField()
    protein = models.PositiveIntegerField()
    carbs = models.PositiveIntegerField()
    fats = models.PositiveIntegerField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Diet for {self.member.username}"


# =========================
# ATTENDANCE
# =========================
class Attendance(models.Model):
    member = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'member'}
    )
    check_in = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-check_in']

    def __str__(self):
        return f"{self.member.username} - {self.check_in.date()}"
