from django.shortcuts import render #Imprimir pág HTML
from django.contrib.auth.decorators import login_required
# Create your views here.

@login_required(login_url='/authentication/login')
def index(request): #def = public function
    return render(request, 'expenses/index.html')

def add_expense(request):
    return render(request, 'expenses/add_expense.html')