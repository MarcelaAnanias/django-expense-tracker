from django.shortcuts import render #Imprimir pág HTML

# Create your views here.

def index(request): #def = public function
    return render(request, 'expenses/index.html')
def add_expense(request):
    return render(request, 'expenses/add_expense.html')