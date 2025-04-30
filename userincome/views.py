from django.shortcuts import render, redirect  # Importa funções para renderizar templates e redirecionar páginas.
from .models import Source, UserIncome  # Importa os modelos Source e UserIncome do app atual.
from django.contrib.auth.decorators import login_required  # Importa um decorador para exigir login antes de acessar uma view.
from django.contrib import messages  # Importa o módulo para exibir mensagens no Django (ex: erro, sucesso).
from django.core.paginator import Paginator
import json
from userpreferences.models import UserPreference
from django.http import JsonResponse, HttpResponse


# Create your views here.

def search_income(request):
    if request.method == 'POST':
        search_str = json.loads(request.body).get('searchText')
        income = UserIncome.objects.filter(
            amount__istartswith=search_str, owner=request.user) | UserIncome.objects.filter(
            date__istartswith=search_str, owner=request.user) | UserIncome.objects.filter(
            description__icontains=search_str, owner=request.user) | UserIncome.objects.filter(
            source__icontains=search_str, owner=request.user)
        data = income.values()
        return JsonResponse(list(data), safe=False)

@login_required(login_url='/authentication/login')
def index(request): #def = public function
    categories = Source.objects.all()
    income = UserIncome.objects.filter(owner=request.user)
    paginator = Paginator(income, 5) # Cria um objeto Paginator com a lista de despesas, dividindo em páginas de 3 itens cada
    page_number = request.GET.get('page') # Obtém o número da página atual a partir da URL (ex: ?page=2, então page_number = 2)
    page_obj = Paginator.get_page(paginator, page_number) # Busca os dados da página correspondente (se page_number = 2, pega os 3 itens da página 2)
    currency = UserPreference.objects.get(user=request.user).currency

    context = {
        'income':income,
        'page_obj': page_obj,
        'currency': currency
    }
    return render(request, 'income/index.html', context)

@login_required(login_url='/authentication/login')
def add_income(request):
    sources = Source.objects.all()
    context = {
        'sources': sources,
        'values': request.POST
    }
    if request.method == 'GET':
        return render(request, 'income/add_income.html', context)

    if request.method == 'POST':
        amount = request.POST['amount']

        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, 'income/add_income.html', context)
        description = request.POST['description']
        date = request.POST['income_date']
        source = request.POST['source']

        if not description:
            messages.error(request, 'description is required')
            return render(request, 'income/add_income.html', context)

        UserIncome.objects.create(owner=request.user, amount=amount, date=date,
                                  source=source, description=description)
        messages.success(request, 'Record saved successfully')

        return redirect('income')
    

@login_required(login_url='/authentication/login')
def edit_income(request, id):
    income = UserIncome.objects.get(pk=id)
    sources = Source.objects.all()
    context = {
        'income': income,
        'values': income,
        'sources': sources
    }
    if request.method == 'GET':
        return render(request, 'income/edit_income.html', context)
    if request.method == 'POST':
        amount = request.POST['amount']

        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, 'income/edit_income.html', context)
        description = request.POST['description']
        date = request.POST['income_date']
        source = request.POST['source']

        if not description:
            messages.error(request, 'description is required')
            return render(request, 'income/edit_income.html', context)
        income.amount = amount
        income. date = date
        income.source = source
        income.description = description

        income.save()
        messages.success(request, 'Record updated  successfully')

        return redirect('income')
    
def delete_income(request, id):
    income = UserIncome.objects.get(pk=id)
    income.delete()
    messages.success(request, 'record removed')
    return redirect('income')