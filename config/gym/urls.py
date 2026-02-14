from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *
from rest_framework_simplejwt.views import TokenRefreshView

router = DefaultRouter()

router.register(r'users', UserViewSet, basename='users')
router.register(r'memberships', MembershipViewSet, basename='memberships')
router.register(r'workout-plans', WorkoutPlanViewSet, basename='workout-plans')
router.register(r'workout-logs', WorkoutLogViewSet, basename='workout-logs')
router.register(r'diet-plans', DietPlanViewSet, basename='diet-plans')
router.register(r'attendance', AttendanceViewSet, basename='attendance')

urlpatterns = [

    # JWT
    path('token/', CustomTokenView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # First time admin registration
    path('admin-register/', admin_register),

    # Dashboard
    path('dashboard/', dashboard_stats),

    # ViewSets
    path('', include(router.urls)),
]
