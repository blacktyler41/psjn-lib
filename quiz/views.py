from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.http import HttpResponse, JsonResponse
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Book
from .forms import BookForm
from django.core.paginator import Paginator



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
    recent_books = Book.objects.order_by('-id')[:6]
    return render(request, 'quiz/user.html',{
        'count_religious': Book.objects.filter(category='religious').count(),
        'count_science': Book.objects.filter(category='science').count(),
        'count_other': Book.objects.filter(category='other').count(),
        'count_all': Book.objects.count(),
        'recent_books': recent_books,
    })


@login_required
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


def book_list(request):
   
   
    # ?category=science in the address gives "science". If missing, use "all"
    q = request.GET.get('q', '').strip()
    selected = request.GET.get('category', 'all')

    # Treat unknown values like ?category=abc as "all"
    if selected not in ('religious', 'science', 'other'):
        selected = 'all'

    books = Book.objects.all()
    if selected != 'all':
        books = books.filter(category=selected)

    for word in q.split():
        books = books.filter(title__icontains=word)



# Divide books into pages of 50
    paginator = Paginator(books, 50)

# Find the requested page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

# Send data to your existing HTML template
    return render(request, 'quiz/book_list.html', {
    'books': page_obj.object_list,
    'page_obj': page_obj,
    'selected': selected,
    'q': q,
    'result_count': paginator.count,
   })
    
    
    