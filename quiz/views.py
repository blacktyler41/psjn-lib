from django.shortcuts import render, get_object_or_404, redirect
from .models import Quiz, Question,Answer
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Book
from .forms import BookForm


def index(request):
    if  request.user.is_authenticated:
        return redirect('student_dashboard')
    else:
        return redirect("login")
def dev(request):
    return render(request, 'quiz/dev.html')   

def login_view(request):
    if request.method == "POST":
        username= request.POST["username"]
        password= request.POST["password"]
        user= authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('student_dashboard')
        else:
            return render(request, "quiz/login.html", {"message": "Invalid Credentials"})
    return render(request, "quiz/login.html")

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def student_dashboard(request):
    return render(request, 'quiz/user.html')

@login_required
def quiz_list(request):
    quizzes = Quiz.objects.all()
    return render(request, 'quiz/quiz_list.html', {'quizzes': quizzes})

def quiz_detail(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)
    if request.method == 'POST':
        score = 0
        questions = quiz.questions.all()
        for question in questions:
            selected_answer = request.POST.get(str(question.id))
            if selected_answer:
                answer = Answer.objects.get(id=selected_answer)
                if answer.is_correct:
                    score += 1
        return render(request, 'quiz/result.html', {'quiz': quiz, 'score': score, 'total': questions.count(), 'percentage': score * 100 / questions.count()})
    else:
        return render(request, 'quiz/quiz_detail.html', {'quiz': quiz})


def book_list(request):
    books = Book.objects.all()
    return render(request, 'quiz/book_list.html', {'books': books})

def add_book(request):
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('book_list')
    else:
        form = BookForm()
    return render(request, 'quiz/add_book.html', {'form': form})

