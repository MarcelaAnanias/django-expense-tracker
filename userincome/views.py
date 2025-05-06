from django.shortcuts import render, redirect  # Importa funções para renderizar templates e redirecionar páginas.
from .models import Source, UserIncome  # Importa os modelos Source e UserIncome do app atual.
from django.contrib.auth.decorators import login_required  # Importa um decorador para exigir login antes de acessar uma view.
from django.contrib import messages  # Importa o módulo para exibir mensagens no Django (ex: erro, sucesso).
from django.core.paginator import Paginator
import json
from userpreferences.models import UserPreference
from django.http import JsonResponse, HttpResponse
import datetime
from django.db.models import Sum
import plotly.graph_objs as go
from plotly.offline import plot
from collections import defaultdict
from django.db.models.functions import TruncDate
import plotly.graph_objs as go
from datetime import timedelta



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
    sources = Source.objects.all()
    income = UserIncome.objects.filter(owner=request.user)
    paginator = Paginator(income, 3) # Cria um objeto Paginator com a lista de despesas, dividindo em páginas de 3 itens cada
    page_number = request.GET.get('page') # Obtém o número da página atual a partir da URL (ex: ?page=2, então page_number = 2)
    page_obj = Paginator.get_page(paginator, page_number) # Busca os dados da página correspondente (se page_number = 2, pega os 3 itens da página 2)
    currency = UserPreference.objects.get(user=request.user).currency


    # Gráfico aqui
    todays_date = datetime.date.today()
    six_months_ago = todays_date - datetime.timedelta(days=30 * 3)
    filtered_income = income.filter(date__gte=six_months_ago, date__lte=todays_date)
    source_totals = filtered_income.values('source').annotate(total=Sum('amount'))
    labels = [item['source'] for item in source_totals]
    values = [float(item['total']) for item in source_totals]
    fig = go.Figure(data=[go.Pie(
        labels=labels, 
        values=values, 
        hole=0.3, #donalts
        textfont=dict(color='white'),
        marker=dict( #cores
        colors=['#2d7f48', '#3eb265', '#5aff91','#9cffbd', '#dafde8'],
        line=dict(color='white', width=2) #margem branca
    )
    )])
    
    fig.update_layout(
         title={
            'text': '<span style="letter-spacing:2px; text-transform:uppercase;">income per source (last 3 months)</span>',
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
    plot_div = plot(fig, output_type='div', config={'responsive': False})

    # Agrupar por categoria e data
    grouped_income = (
        filtered_income
        .values('source', day=TruncDate('date'))
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
    source_data = defaultdict(lambda: {'dates': date_list.copy(), 'totals': [0]*len(date_list)})

    
    for item in grouped_income:
        source = item['source']
        date_str = item['day'].strftime('%Y-%m-%d')
        total = float(item['total'])

        index = date_list.index(date_str)
        source_data[source]['totals'][index] = total

    # Monta o gráfico de linhas por categoria
    line_fig = go.Figure()

    source_colors = {
        'Interest Income': '#dafde8',  
        'House Rental': '#2d7f48',   
        'Business': '#5aff91',
        'Salary': '#3eb265',
        'Dividend Income': '#9cffbd'
    }

    # Criação dos traços com cor fixa
    for source, data in source_data.items():
        line_fig.add_trace(go.Scatter(
            x=data['dates'],
            y=data['totals'],
            mode='lines',
            name=source,
            line=dict(
                color=source_colors.get(source, '#888'), # cor fixa ou fallback
                width=2,
            )  
        ))

    line_fig.update_layout(
        title={
            'text': '<span style="letter-spacing:2px; text-transform:uppercase;"> source Cumulative Comparison (Last 3 months)</span>',
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
        margin=dict(l=65, r=30, t=100, b=20),
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

    plot_line_div = plot(line_fig, output_type='div', config={'responsive': False})

    context = {
        'income':income,
        'page_obj': page_obj,
        'plot_div': plot_div,
        'currency': currency,
        'plot_line_div': plot_line_div,
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


@login_required(login_url='/authentication/login')
def stats_income(request):
    todays_date = datetime.date.today()
    six_months_ago = todays_date-datetime.timedelta(days=30*3) # Define o intervalo de 6 meses

    # Filtra despesas no período
    income = UserIncome.objects.filter(
        owner=request.user,
        date__gte=six_months_ago,
        date__lte=todays_date
    )

    # Agrupa e soma os valores por categoria
    source_totals = income.values('source').annotate(total=Sum('amount'))

    labels = [item['source'] for item in source_totals]
    values = [float(item['total']) for item in source_totals]

    # Cria o gráfico de pizza
    fig = go.Figure(data=[go.Pie(
        labels=labels, 
        values=values, 
        textinfo='percent+label',
        textfont=dict(color='white'), #cor da fonte
        marker=dict( #cores
        colors=['#2d7f48', '#3eb265', '#5aff91','#9cffbd', '#dafde8'],
        line=dict(color='white', width=2) #margem branca
    )
    )])

    fig.update_layout(
        title={
            'text': '<span style="letter-spacing:2px; text-transform:uppercase;">Incomes per Source (last 3 months)</span>',
            #'y': 0.95,
            'x': 0.43,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': dict(
                family='Nunito Sans',
                size=18,
                color='#55595c',  # ou qualquer outra cor
            )
        },
        width=1050,
        height=630,
        showlegend=True,
    )

    plot_div = plot(fig, output_type='div')

    return render(request, 'income/stats.html', {'plot_div': plot_div})


    