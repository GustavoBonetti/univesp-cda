from django.db import models
from datetime import datetime
from django.utils import timezone
import pandas as pd
from django.db.models import Q, F, ExpressionWrapper, fields
from datetime import datetime, date, timedelta
from django.conf import settings

#SIGNALS
from django.db.models import signals
from django.template.defaultfilters import slugify

hoje = datetime.today()

class Base(models.Model):
    criado = models.DateField('Data da Criação', auto_now_add = True)
    modificado = models.DateField('Data de Atualização', auto_now = True)
    ativo = models.BooleanField('Ativo', default = True)

    class Meta:
        abstract = True

class LocalEstoque(Base):
    local = models.CharField('Localização', max_length = 100)    
    
    def __str__(self):
        return self.local

    def save(self, *args, **kwargs):
        self.local = self.local.upper()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = '01-Local do Estoque'
        verbose_name_plural = '01-Locais do Estoque'

class Unidade(Base):
    nome = models.CharField('Unidade', max_length=10)

    def __str__(self):
        return self.nome

    def save(self, *args, **kwargs):
        self.nome = self.nome.upper()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = '02-Unidade de Medida '
        verbose_name_plural = '02-Unidades de Medida'


class Produto(Base):
    nome = models.CharField('Nome', max_length = 100)
    unidade = models.ForeignKey(Unidade, verbose_name='Unidade', on_delete=models.DO_NOTHING)
    localestoque = models.ForeignKey(LocalEstoque, verbose_name='Local', on_delete = models.DO_NOTHING)
    estoqueinicial = models.IntegerField("Estoque Inicial", default=0)

    def __str__(self):
        return self.nome
    
    def save(self, *args, **kwargs):
        self.nome = self.nome.upper()
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = '03-Produto'
        verbose_name_plural = '03-Produtos'
        ordering=['nome']    

class Periodo(Base):
    cor = models.CharField('Cor', max_length = 15 )
    prazo = models.IntegerField('Prazo para Entrega')    
    image = models.CharField('Icone', max_length=5)        
    
    def __str__(self):
        return self.cor + ' ' + self.image
    
    def save(self, *args, **kwargs):
        self.cor = self.cor.upper()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = '04-Período de Entrega'
        verbose_name_plural = '04-Períodos de Entrega'       
        ordering=['prazo']    

class Bairro(Base):
    bairro = models.CharField('Bairro', max_length = 100)        
    
    def __str__(self):
        return self.bairro

    def save(self, *args, **kwargs):
        self.bairro = self.bairro.upper()
        super().save(*args, **kwargs)    

    class Meta:
        verbose_name = '05-Bairro'
        verbose_name_plural = '05-Bairros'
        ordering=['bairro']

class Entregador(Base):
    nome = models.CharField('Entregador', max_length = 50)        
    
    def __str__(self):
        return self.nome

    def save(self, *args, **kwargs):
        self.nome = self.nome.upper()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = '09-Entregador'
        verbose_name_plural = '09-Entregadores'
        ordering=['nome']


class Endereco(Base):
    endereco = models.CharField('Endereço', max_length = 200)
    bairro = models.ForeignKey(Bairro, verbose_name='Bairro', on_delete = models.DO_NOTHING)
    
    def __str__(self):        
        b=Bairro.objects.get(id=self.bairro_id)                
        return f'{self.endereco} - {b.bairro}'

    def save(self, *args, **kwargs):
        self.endereco = self.endereco.upper()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = '06-Endereço'
        verbose_name_plural = '06-Endereços'
        ordering=['endereco']

    
class Ocupacao(Base):
    nome = models.CharField('Ocupação', max_length=100)

    def __str__(self):
        return self.nome

    def save(self, *args, **kwargs):
        self.nome = self.nome.upper()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = '07-Ocupação'
        verbose_name_plural = '07-Ocupações'
        ordering=['nome']  

class View_Assistenciado(models.Model):
    ativo = models.BooleanField('Ativo')
    nome = models.CharField('Nome', max_length = 100)        
    bairro = models.CharField('Bairro', max_length=100)
    endereco = models.CharField('Endereço', max_length=100)
    numero = models.IntegerField('Nº')    
    telefone = models.CharField('Telefone', max_length = 100)    
    image = models.CharField('Icone', max_length=4)
    ult_entrega = models.DateField('Entrega', auto_now=False, auto_now_add=False)
    prox_entrega = models.DateField('Próx. Entrega', auto_now=False, auto_now_add=False)
    status = models.CharField('Status', max_length=15)
    criado = models.DateField('Cadastro')
    prazo = models.IntegerField('Prazo')
    cor = models.CharField('Cor', max_length = 15 )

    def __str__(self):
        return f'{self.id} - {self.nome}'

    class Meta:    
        managed = False
        db_table = 'view_assistenciado' 
        verbose_name = '13-Listagem de Assistenciado'
        verbose_name_plural = '13-Listagem de Assistenciados'

class Assistenciado(Base):
    nome = models.CharField('Nome', max_length = 100)
    periodo = models.ForeignKey(Periodo, verbose_name='Cor', 
                                on_delete = models.DO_NOTHING, 
                                limit_choices_to= {'ativo': True}, 
                                related_name='assistenciados')     
    endereco = models.ForeignKey(Endereco, verbose_name='Endereço', 
                                 on_delete = models.DO_NOTHING, 
                                 limit_choices_to= {'ativo': True}, 
                                 related_name='enderecos')            
    telefone = models.CharField('Telefone', max_length = 100, default='-')    
    nascimento = models.DateField('Data Nasc.', null = True)  
    numero = models.IntegerField('Nº')
    #rg = models.CharField('RG', max_length = 20, default='-')
    #cpf= models.CharField('CPF', max_length = 20, default='-')
    ocupacao = models.ForeignKey(Ocupacao, verbose_name="Ocupação", on_delete=models.DO_NOTHING, limit_choices_to= {'ativo': True})
    observacao = models.TextField('Informações adicionais',default='-')
        
    def __str__(self):        
        return f'{self.id}-{self.nome}'

    def save(self, *args, **kwargs):
        self.nome = self.nome.upper()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = '08-Assistenciado'
        verbose_name_plural = '08-Assistenciados'
        ordering=['id']

class Fornecedor(Base):
    nome = models.CharField('Fornecedor', max_length=100)
    endereco = models.CharField('Endereço', max_length=100)
    bairro = models.CharField('Bairro', max_length=50)
    cidade = models.CharField('Cidade', max_length=100)
    telefone = models.CharField('Telefone', max_length=100, null=True, blank=True)
    cnpj = models.CharField('CNPJ', max_length=20, null=True, blank=True)

    class Meta:
        verbose_name = '10-Fornecedor/Doador'
        verbose_name_plural = '10-Fornecedores/Doadores'
        ordering=['nome']

    def __str__(self):
        return self.nome

    def save(self, *args, **kwargs): 
        self.nome = self.nome.upper()
        self.endereco = self.endereco.upper()
        self.bairro = self.bairro.upper()
        self.cidade = self.cidade.upper()
        
        super().save(*args, **kwargs)    


class EntradaProduto(Base):
    data = timezone.now()
    fornecedor = models.ForeignKey(Fornecedor, verbose_name="Fornecedor/Doador", on_delete = models.DO_NOTHING, limit_choices_to= {'ativo': True})     
    produto = models.ForeignKey(Produto, verbose_name="Produto", on_delete = models.DO_NOTHING, limit_choices_to= {'ativo': True})
    quantidade = models.IntegerField('Quantidade')
    dataentrega = models.DateField('Data Recebimento', default=data)    
    notafiscal = models.IntegerField('Nº Nota Fiscal', null=True, blank=True)
    observacao = models.TextField('Observações', null=True, blank=True)

    class Meta:
        verbose_name = '12-Recebimento'
        verbose_name_plural = '12-Recebimentos'
        ordering=['-dataentrega']

    def __str__(self):
        return f'Fornecedor: {self.fornecedor} -> Produto: {self.produto}'    

    
class SaidaProduto(Base):    
    data = timezone.now()
    entregador = models.ForeignKey(Entregador, verbose_name="Entregador", on_delete=models.DO_NOTHING, limit_choices_to= {'ativo': True})         
    assistenciado = models.ForeignKey(Assistenciado, related_name='saida_assistenciado', verbose_name="Recebedor", on_delete=models.DO_NOTHING, limit_choices_to= {'ativo': True})                
    cor_id = models.IntegerField()
    produto = models.ForeignKey(Produto, verbose_name="Produto", on_delete=models.DO_NOTHING, limit_choices_to= {'ativo': True}, default = 1)
    quantidade = models.IntegerField('Quantidade', default = 1)
    recebeu = models.CharField('Quem Recebeu?', max_length=50)    
    dataentrega = models.DateField('Data da Entrega', default=data)

    def __str__(self):
        return f'Entrega nº : {str(self.id).zfill(6)}'

    def save(self, *args, **kwargs):
        self.recebeu = self.recebeu.upper()
        a=Assistenciado.objects.get(id=self.assistenciado_id)
        self.cor_id = a.periodo.id       
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = '11-Entrega'
        verbose_name_plural = '11-Entregas'
        ordering=['-dataentrega', 'assistenciado']

