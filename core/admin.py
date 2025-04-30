#NECESSÁRIO ALOCAR TODOS OS CAMPOS DO MODEL
from typing import Any
from django.contrib import admin
from django.db.models.query import QuerySet
from django.http import HttpRequest
from django.utils.html import format_html
from datetime import datetime, date, timedelta
import pandas as pd
from django.db.models import Sum
from django.db.models import Q, F, ExpressionWrapper, fields
from rangefilter.filters import DateRangeFilter, DateTimeRangeFilter, NumericRangeFilter

hoje = datetime.today()

# Register your models here.
from core.models import Produto, Periodo, LocalEstoque, Endereco
from core.models import Bairro, Assistenciado, Ocupacao
from core.models import Fornecedor, EntradaProduto, Entregador
from core.models import SaidaProduto, View_Assistenciado, Unidade

@admin.register(Unidade) 
class UnidadeAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    search_fields=('nome',)
    
@admin.register(Produto) 
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'unidade', 'localestoque', 'estoque_atual')
    list_filter=['ativo','localestoque']
    search_fields = ['nome']

    def estoque_atual(self, obj):
        total_inicial = obj.estoqueinicial
        total_saidas = SaidaProduto.objects.filter(produto_id = obj.id).aggregate(soma=Sum('quantidade'))['soma']
        total_entradas = EntradaProduto.objects.filter(produto_id = obj.id).aggregate(soma=Sum('quantidade'))['soma']
        
        if total_saidas==None:
            total_saidas=0
        if total_entradas==None:
            total_entradas=0    
        return int(total_inicial) + int(total_entradas) - int(total_saidas)
    
    def changelist_view(self, request, extra_context=None):        
        response = super().changelist_view(request, extra_context)

        try:
            response.context_data['total'] = '10.250,00'
        except (AttributeError, TypeError):
            response.context_data = {'total': '10.300'}
        return response        

@admin.register(Periodo) 
class PeriodoAdmin(admin.ModelAdmin):   
    list_display = ('cor', 'prazo', 'image')
    list_filter=['ativo']
    search_fields = ['cor']

@admin.register(LocalEstoque) 
class LocalEstoqueAdmin(admin.ModelAdmin):
    list_display = ('local', 'ativo')
    list_filter=['ativo']
    search_fields = ['local']

@admin.register(Endereco) 
class EnderecoAdmin(admin.ModelAdmin):
    list_display = ('endereco', 'bairro', 'ativo')
    list_filter=['bairro']
    search_fields = ['endereco']


@admin.register(Bairro) 
class BairroAdmin(admin.ModelAdmin):
    list_display = ('bairro', 'ativo')

    search_fields = ['bairro']
    list_filter=['ativo']


@admin.register(Ocupacao) 
class OcupacaoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'ativo')

    search_fields = ['nome']
    list_filter=['ativo']

@admin.register(Fornecedor) 
class FornecedorAdmin(admin.ModelAdmin):
    list_display = ('nome', 'endereco', 'bairro', 'cidade', 'telefone', 'cnpj')            

    search_fields = ['nome']
    list_filter=('ativo','cidade')

@admin.register(Entregador) 
class EntregadorAdmin(admin.ModelAdmin):
    list_display = ['nome']            

    search_fields = ['nome']
    list_filter=['ativo']

@admin.register(EntradaProduto) 
class EntradaProdutoAdmin(admin.ModelAdmin):        
    list_display = ('fornecedor', 'notafiscal', 'dataentrega', 'produto', 'quantidade')    
    search_fields = ['produto__nome']
    list_filter=(('dataentrega', DateRangeFilter),'ativo','fornecedor')   
    date_hierarchy=('dataentrega')

    def changelist_view(self, request, extra_context=None, **kwargs):
        extra_context = extra_context or {}                              
       
        response = super().changelist_view(request, extra_context=extra_context, )
        qs=response.context_data['cl'].queryset

        soma_entrada = qs.filter(quantidade__gt=0).aggregate(soma_total=Sum('quantidade'))['soma_total']
        
        if soma_entrada is None: 
            soma_entrada = 0

        extra_context['soma_entrada'] = soma_entrada
        
        return super(EntradaProdutoAdmin, self).changelist_view(request, extra_context)

@admin.register(Assistenciado) 
class AssistenciadoAdmin(admin.ModelAdmin):

    def get_actions(self, request):
        # Desabilita todas as ações
        return {}

    def prazo(self, obj):
        a=Assistenciado.objects.get(id=obj.id)
        prazo=a.periodo.prazo        
        return prazo    
    
    def cor(self, obj):
        f=Assistenciado.objects.get(id=obj.id)        
        return f.periodo.image
    
    def get_bairro(self, obj):
        return obj.endereco.bairro.bairro
 
    get_bairro.short_description = 'Bairro'  # Texto que será exibido como título da coluna
    get_bairro.admin_order_field = 'endereco__bairro__bairro'  # Permite ordenar pela coluna

    list_display = ('id', 'nome', 'cor', 'prazo', 'endereco', 'numero', 'get_bairro','telefone',)
    list_display_links=('nome',)
    list_filter=('periodo', 'endereco__bairro__bairro', 'endereco')
    search_fields = ['id', 'nome']
    search_help_text = ['Texto de ajuda aqui']

    fieldsets = (
                ('Dados Básicos', {
                    'fields': ('nome', 'periodo', ('endereco', 'numero'), ('telefone'), ('nascimento', 'ativo'))
                }),
                ('Dados Profissionais', {
                    'fields': ('ocupacao',),
                }),
                ('Outros', {
                    'fields': ('observacao',),
                }),
                )

@admin.register(View_Assistenciado) 
class View_AssistenciadoAdmin(admin.ModelAdmin):
    
    read_only_fields = ('ativo', 'nome', 'bairro_nome', 'endereco', 'numero', 
                        'telefone', 'image','ult_entrega', 'prox_entrega', 
                        'status', 'criado', 'prazo')
    actions = None
    #action_form = None

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    def  has_delete_permission(self, request: HttpRequest, obj: Any | None = ...) -> bool:
        return False
    
    def has_change_permission(self, request: HttpRequest, obj: Any | None = ...) -> bool:
        return True
    
    def cor_img(self, obj):        
        return obj.image

    fieldsets = (('Situação do Cadastro', {
                    'fields': (('ativo'), )
                }),)

    list_display = ('nome', 'cor_img', 'prazo', 'criado', 
                    'ult_entrega', 'prox_entrega', 
                    'endereco', 'numero', 'bairro','telefone',)
    search_fields = ['nome']
    search_help_text  = "Pesquisa por Nome"
    list_filter=(('ult_entrega', DateRangeFilter), 'cor', 'status', 'bairro', 'endereco')
    #filter_input_length =({'status': 15, 'bairro':100, 'endereco':100})

@admin.register(SaidaProduto) 
class SaidaProdutoAdmin(admin.ModelAdmin):

    def get_actions(self, request):
        # Desabilita todas as ações
        return {}

    def prazo(self, obj):
        a=Assistenciado.objects.get(id=obj.assistenciado_id)
        prazo=a.periodo.prazo        
        return prazo    

    prazo.short_description = 'Prazo'  # Texto que será exibido como título da coluna
    prazo.admin_order_field = 'assistenciado__periodo__prazo'  # Permite ordenar pela coluna


    def cor(self, obj):
        p=Periodo.objects.get(id=obj.cor_id)        
        return p.image
    
    cor.short_description = 'Cor'  # Texto que será exibido como título da coluna
    cor.admin_order_field = 'cor_id'  # Permite ordenar pela coluna

    def get_bairro(self, obj):
        return obj.assistenciado.endereco.bairro.bairro
 
    get_bairro.short_description = 'Bairro'  # Texto que será exibido como título da coluna
    get_bairro.admin_order_field = 'assistenciado__endereco__bairro__bairro'  # Permite ordenar pela coluna
        
    list_display = ('assistenciado','get_bairro', 'cor', 'prazo', 'entregador', 'dataentrega', 'produto','quantidade','recebeu')
    list_filter=(('dataentrega', DateRangeFilter), 'entregador', 'produto', 'assistenciado__endereco__bairro__bairro', 'ativo')
    search_fields =['assistenciado__id', 'assistenciado__nome']
    date_hierarchy=('dataentrega')

    def changelist_view(self, request, extra_context=None, **kwargs):
        extra_context = extra_context or {}                              
       
        response = super().changelist_view(request, extra_context=extra_context, )
        qs=response.context_data['cl'].queryset

        soma_saida = qs.filter(quantidade__gt=0).aggregate(soma_total=Sum('quantidade'))['soma_total']
        
        if soma_saida is None: 
            soma_saida = 0

        extra_context['soma_saida'] = soma_saida
        
        return super(SaidaProdutoAdmin, self).changelist_view(request, extra_context)


    fieldsets = (
                ('Dados Básicos', {
                    'fields': (('dataentrega','entregador'), )
                }),
                ('Dados Recebedor', {
                    'fields': ('assistenciado', )
                }),
                ('Dados do Produto', {
                    'fields': ('produto', 'quantidade'),
                }),
                ('Pessoa que recebeu a entrega', {
                    'fields': ('recebeu', 
                               )                    
                }),)

#class MyModelAdmin(ModelAdminTotals):
#    list_display = ['col_a', 'col_b', 'col_c']
#    list_totals = [('col_b', lambda field: Coalesce(Sum(field), 0)), ('col_c', Avg)]
    
    