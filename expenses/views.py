from django.shortcuts import render, redirect  # Importa funções para renderizar templates e redirecionar páginas.
from .models import Category, Expense  # Importa os modelos Category e Expense do app atual.
from django.contrib.auth.decorators import login_required  # Importa um decorador para exigir login antes de acessar uma view.
# Create your views here.
from django.contrib import messages  # Importa o módulo para exibir mensagens no Django (ex: erro, sucesso).

@login_required(login_url='/authentication/login')
def index(request): #def = public function
    categories = Category.objects.all()
    expenses = Expense.objects.filter(owner=request.user)

    context = {
        'expenses':expenses
    }
    return render(request, 'expenses/index.html', context)

def add_expense(request):
    categories = Category.objects.all()  # Busca todas as categorias cadastradas no banco de dados.
    context = {
        'categories': categories, # Passa as categorias para o template.
        'values': request.POST # Passa os valores do formulário para manter os dados preenchidos no caso de erro.
    }
    if request.method == 'GET': # Se a requisição for GET (ou seja, o usuário apenas acessou a página),
        return render(request, 'expenses/add_expense.html', context) # Renderiza o formulário de adição de despesas.

    if request.method == 'POST':  # Se a requisição for POST (ou seja, o usuário enviou o formulário),
       amount = request.POST['amount'] # Obtém o valor do campo 'amount' do formulário.

       if not amount:
           messages.error(request, 'Amount is required')
           return render(request, 'expenses/add_expense.html', context)
       
       description = request.POST['description']
       date = request.POST['expense_date']
       category = request.POST['category']
       
       if not description:
            messages.error(request, 'Description is required')
            return render(request, 'expenses/add_expense.html', context)
       
       # Cria e salva a nova despesa no banco de dados associada ao usuário logado.
       Expense.objects.create(owner=request.user, amount=amount, date=date, category=category, description=description)
       messages.success(request, 'Expense saved successfully')
       
       return redirect('expenses')
    

def edit_expense(request, id):
    print(f"Editing expense with ID: {id}")
    expense=Expense.objects.get(pk=id)
    categories = Category.objects.all()
    context = {
        'expense': expense,
        'values': expense,
        'categories': categories
    }
    if request.method == "GET":
        return render(request, 'expenses/edit_expense.html', context)
        
    if request.method == 'POST':
        amount = request.POST['amount']

        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, 'expenses/edit-expense.html', context)
        description = request.POST['description']
        date = request.POST['expense_date']
        category = request.POST['category'] 

        if not description:
            messages.error(request, 'description is required')
            return render(request, 'expenses/edit-expense.html', context)
        
        # Atualizando os dados da despesa existente
        expense.owner = request.user
        expense.amount = amount
        expense.date = date
        expense.category = category
        expense.description = description

        expense.save()
        messages.success(request, 'Expense updated  successfully')

        return redirect('expenses')

def delete_expense(request, id):
    expense = Expense.objects.get(pk=id)
    expense.delete()
    messages.error(request, 'Expense removed')
    return redirect('expenses')
