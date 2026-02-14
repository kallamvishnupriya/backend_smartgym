from rest_framework import viewsets, status, serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import *
from .serializers import *
from .permissions import *

User = get_user_model()


# =========================
# ADMIN REGISTER
# =========================
@api_view(['POST'])
@permission_classes([AllowAny])
def admin_register(request):

    if User.objects.filter(role="admin").exists():
        return Response(
            {"error": "Admin already exists."},
            status=status.HTTP_403_FORBIDDEN
        )

    data = request.data
    data["role"] = "admin"

    serializer = RegisterSerializer(data=data)

    if serializer.is_valid():
        user = serializer.save()
        user.is_staff = True
        user.is_superuser = True
        user.save()

        return Response(
            {"message": "Admin registered successfully"},
            status=status.HTTP_201_CREATED
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# =========================
# TOKEN
# =========================
class CustomTokenView(TokenObtainPairView):
    serializer_class = CustomTokenSerializer


# =========================
# USERS (ADMIN ONLY)
# =========================
class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.role == "admin":
            return User.objects.all()

        if user.role == "trainer":
            return User.objects.filter(role="member")

        return User.objects.none()



# =========================
# MEMBERSHIP
# =========================
class MembershipViewSet(viewsets.ModelViewSet):
    queryset = Membership.objects.all()
    serializer_class = MembershipSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role == "admin":
            return Membership.objects.all()
        return Membership.objects.filter(member=self.request.user)


# =========================
# WORKOUT PLAN
# =========================
class WorkoutPlanViewSet(viewsets.ModelViewSet):
    queryset = WorkoutPlan.objects.all()
    serializer_class = WorkoutPlanSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.role == "admin":
            return WorkoutPlan.objects.all()

        if user.role == "trainer":
            return WorkoutPlan.objects.filter(trainer=user)

        if user.role == "member":
            return WorkoutPlan.objects.filter(member=user)

        return WorkoutPlan.objects.none()

    def perform_create(self, serializer):
        user = self.request.user

        if user.role not in ["trainer", "admin"]:
            raise serializers.ValidationError("Only trainer or admin can create workout plans")

        serializer.save(trainer=user)


# =========================
# WORKOUT LOG (MEMBER ONLY)
# =========================
class WorkoutLogViewSet(viewsets.ModelViewSet):
    queryset = WorkoutLog.objects.all()
    serializer_class = WorkoutLogSerializer
    permission_classes = [IsAuthenticated, IsMember]

    def get_queryset(self):
        return WorkoutLog.objects.filter(member=self.request.user)

    def perform_create(self, serializer):
        serializer.save(member=self.request.user)


# =========================
# DIET PLAN
# =========================
class DietPlanViewSet(viewsets.ModelViewSet):
    queryset = DietPlan.objects.all()
    serializer_class = DietPlanSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.role == "admin":
            return DietPlan.objects.all()

        if user.role == "trainer":
            return DietPlan.objects.filter(trainer=user)

        if user.role == "member":
            return DietPlan.objects.filter(member=user)

        return DietPlan.objects.none()

    def perform_create(self, serializer):
        user = self.request.user

        if user.role not in ["trainer", "admin"]:
            raise serializers.ValidationError("Only trainer or admin can create diet plans")

        serializer.save(trainer=user)


# =========================
# ATTENDANCE
# =========================
class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role == "admin":
            return Attendance.objects.all()
        return Attendance.objects.filter(member=self.request.user)

    def perform_create(self, serializer):
        user = self.request.user

        if user.role != "member":
            raise serializers.ValidationError("Only members can mark attendance")

        today = timezone.now().date()

        if Attendance.objects.filter(
            member=user,
            check_in__date=today
        ).exists():
            raise serializers.ValidationError(
                {"error": "Attendance already marked today"}
            )

        serializer.save(member=user)


# =========================
# DASHBOARD (Admin Only)
# =========================
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):

    if request.user.role != "admin":
        return Response({"error": "Not authorized"}, status=403)

    return Response({
        "total_members": User.objects.filter(role='member').count(),
        "active_memberships": Membership.objects.filter(active=True).count(),
        "total_workouts": WorkoutLog.objects.count(),
        "today_attendance": Attendance.objects.filter(
            check_in__date=timezone.now().date()
        ).count()
    })
