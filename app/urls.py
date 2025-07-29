from django.urls import path
from . import views

urlpatterns = [
    path('', views.selection, name='selection'),
    path('addition/<int:problem>/', views.addition, name='addition_problems'),
    path('subtraction/<int:problem>/', views.subtraction, name='subtraction_problems'),
    path('multiplication/<int:problem>/', views.multiplication, name='multiplication_problems'),
    path('division/<int:problem>/', views.division, name='division_problems'),
    path('check_answer/', views.check_answer, name='check_answer'),
    path('store_selected_op/', views.store_selected_op, name='store_selected_op'),
    path('get_leaderboard/', views.get_leaderboard, name='get_leaderboard'),
]  