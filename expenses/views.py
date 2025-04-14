from django.shortcuts import render, redirect  # Importa funções para renderizar templates e redirecionar páginas.
from .models import Category, Expense  # Importa os modelos Category e Expense do app atual.
from django.contrib.auth.decorators import login_required  # Importa um decorador para exigir login antes de acessar uma view.
# Create your views here.
from django.contrib import messages  # Importa o módulo para exibir mensagens no Django (ex: erro, sucesso).
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.http import JsonResponse
import json
import datetime
from django.db.models import Sum
import plotly.graph_objs as go
from plotly.offline import plot
from collections import defaultdict
from django.db.models.functions import TruncDate
import plotly.graph_objs as go
from datetime import timedelta


def search_expense(request):
    if request.method == 'POST':
        search_str=json.loads(request.body).get('searchText') # Converte o JSON recebido e extrai o texto digitado no campo de busca
        expenses = Expense.objects.filter(
            amount__istartswith=search_str, owner=request.user) | Expense.objects.filter(
            date__istartswith=search_str, owner=request.user) | Expense.objects.filter(
            description__icontains=search_str, owner=request.user) | Expense.objects.filter(
            category__icontains=search_str, owner=request.user)
        data = expenses.values()
        return JsonResponse(list(data), safe=False)      
    

@login_required(login_url='/authentication/login')
def index(request): #def = public function
    categories = Category.objects.all()
    expenses = Expense.objects.filter(owner=request.user)
    paginator = Paginator(expenses, 3) # Cria um objeto Paginator com a lista de despesas, dividindo em páginas de 3 itens cada
    page_number = request.GET.get('page') # Obtém o número da página atual a partir da URL (ex: ?page=2, então page_number = 2)
    page_obj = Paginator.get_page(paginator, page_number) # Busca os dados da página correspondente (se page_number = 2, pega os 3 itens da página 2)

    # Gráfico aqui
    todays_date = datetime.date.today()
    six_months_ago = todays_date - datetime.timedelta(days=30 * 3)
    filtered_expenses = expenses.filter(date__gte=six_months_ago, date__lte=todays_date)
    category_totals = filtered_expenses.values('category').annotate(total=Sum('amount'))
    labels = [item['category'] for item in category_totals]
    values = [float(item['total']) for item in category_totals]
    fig = go.Figure(data=[go.Pie(
        labels=labels, 
        values=values, 
        hole=0.3, #donalts
        textfont=dict(color='white'),
        marker=dict( #cores
        colors=['#027381', '#0eb9cb', '#ff6f61', '#f33829', '#440b11'],
        line=dict(color='white', width=2) #margem branca
    )
    )])
    fig.update_layout(
         title={
            'text': '<span style="letter-spacing:2px; text-transform:uppercase;">Expenses per Category (last 3 months)</span>',
            #'y': 0.90,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': dict(
                family='Nunito Sans',
                size=12,
                color='#55595c'  # ou qualquer outra cor
            )
        },
        width=520,
        height=530,
        margin=dict(l=30, r=40, t=100, b=30),
        showlegend=True,
        legend=dict(                   #legenda
            orientation='h',
            yanchor='top',
            y=-0.1,
            xanchor='center',
            x=0.5
        )
    )
    plot_div = plot(fig, output_type='div')

    # Agrupar por categoria e data
    grouped_expenses = (
        filtered_expenses
        .values('category', day=TruncDate('date'))
        .annotate(total=Sum('amount'))
        .order_by('date')
    )

    # Cria a lista de todas as datas entre o intervalo
    date_list = []
    current_date = six_months_ago
    while current_date <= todays_date:
        date_list.append(current_date.strftime('%Y-%m-%d'))
        current_date += timedelta(days=1)

    # Inicializa os dados por categoria com 0 para todas as datas
    category_data = defaultdict(lambda: {'dates': date_list.copy(), 'totals': [0]*len(date_list)})

    
    for item in grouped_expenses:
        category = item['category']
        date_str = item['day'].strftime('%Y-%m-%d')
        total = float(item['total'])

        index = date_list.index(date_str)
        category_data[category]['totals'][index] = total

    # Monta o gráfico de linhas por categoria
    line_fig = go.Figure()

    category_colors = {
        'Clothes and Accessories': '#f33829',  
        'Restaurants': '#027381',   
        'Insurance': '#ff7751',
        'Travel': '#0eb9cb',
        'Fixed Expenses': '#440b11'
    }

    # Criação dos traços com cor fixa
    for category, data in category_data.items():
        line_fig.add_trace(go.Scatter(
            x=data['dates'],
            y=data['totals'],
            mode='lines',
            name=category,
            line=dict(
                color=category_colors.get(category, '#888'), # cor fixa ou fallback
                width=2,
            )  
        ))

    line_fig.update_layout(
        title={
            'text': '<span style="letter-spacing:2px; text-transform:uppercase;"> Category Cumulative Comparison (Last 3 months)</span>',
            #'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': dict(
                family='Nunito Sans',
                size=12,
                color='#55595c'
            )
        },
        width=520,
        height=530,
        margin=dict(l=65, r=30, t=100, b=10),
        plot_bgcolor='white',
        paper_bgcolor='white',
        showlegend=True,
        legend=dict( #config legenda
            orientation='h',
            yanchor='top',
            y=-0.2,
            xanchor='center',
            x=0.5,
        ),
        xaxis=dict(
            showgrid=True,
            gridcolor='#dadada',   # cor das linhas verticais
            gridwidth=1
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='#dadada',   # cor das linhas horizontais
            gridwidth=1
        ),

    )

    plot_line_div = plot(line_fig, output_type='div')

    context = {
        'expenses':expenses,
        'page_obj': page_obj,
        'plot_div': plot_div,
        'plot_line_div': plot_line_div
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
    print(f"Editing expense with ID: {id}") #Só pra ter certeza
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

def stats_view(request):
    todays_date = datetime.date.today()
    six_months_ago = todays_date-datetime.timedelta(days=30*3) # Define o intervalo de 6 meses

    # Filtra despesas no período
    expenses = Expense.objects.filter(
        owner=request.user,
        date__gte=six_months_ago,
        date__lte=todays_date
    )

    # Agrupa e soma os valores por categoria
    category_totals = expenses.values('category').annotate(total=Sum('amount'))

    labels = [item['category'] for item in category_totals]
    values = [float(item['total']) for item in category_totals]

    # Cria o gráfico de pizza
    fig = go.Figure(data=[go.Pie(
        labels=labels, 
        values=values, 
        textinfo='percent+label',
        textfont=dict(color='white'), #cor da fonte
        marker=dict( #cores
        colors=['#027381', '#0eb9cb', '#ff6f61', '#f33829', '#440b11'],
        line=dict(color='white', width=3) #margem branca
    )
    )])

    fig.update_layout(
        title={
            'text': '<span style="letter-spacing:2px; text-transform:uppercase;">Expenses per Category (last 3 months)</span>',
            'y': 0.95,
            'x': 0.43,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': dict(
                family='Nunito Sans',
                size=18,
                color='#55595c',  # ou qualquer outra cor
            )
        },
        width=1000,
        height=630,
        showlegend=True,
    )

    plot_div = plot(fig, output_type='div')

    return render(request, 'expenses/stats.html', {'plot_div': plot_div})


