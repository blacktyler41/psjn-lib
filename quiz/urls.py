from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('quiz_list', views.quiz_list, name='quiz_list'),
    path('quiz/<int:pk>/', views.quiz_detail, name='quiz_detail'),
    path('student_dashboard', views.student_dashboard, name='student_dashboard'),
    path('login',views.login_view, name="login"),
    path('logout',views.logout_view, name="logout"),
    path('book_list', views.book_list, name='book_list'),
    path('add/', views.add_book, name='add_book'),
    path('dev', views.dev, name='dev'),
]
