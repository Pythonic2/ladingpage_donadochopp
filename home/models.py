from django.db import models
import os
from ckeditor.fields import RichTextField


def logo_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{instance.cpf_cliente}_logo.{ext}"
    return os.path.join('logos', filename)


class Produto(models.Model):
    imagem = models.ImageField(upload_to='produtos/', blank=True, null=True)
    nome = models.CharField(max_length=100)
    descricao = RichTextField()
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    estoque = models.PositiveIntegerField()
    peso = models.DecimalField(max_digits=5, decimal_places=2, help_text="Peso em kg")
    altura = models.DecimalField(max_digits=5, decimal_places=2, help_text="Altura em cm")
    largura = models.DecimalField(max_digits=5, decimal_places=2, help_text="Largura em cm")
    comprimento = models.DecimalField(max_digits=5, decimal_places=2, help_text="Comprimento em cm")
    cep_origem = models.CharField(default="58074158",max_length=9, blank=True, null=True)

    def __str__(self):
        return self.nome
    

class Pedido(models.Model):
    nome_cliente = models.CharField(max_length=100)
    cpf_cliente = models.CharField(max_length=11, unique=True)
    endereco_cliente = models.CharField(max_length=255)
    telefone_cliente = models.CharField(max_length=15)
    email_cliente = models.EmailField(max_length=100, blank=True, null=True, unique=True)
    data_nascimento_cliente = models.DateField()
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField()
    data_pedido = models.DateTimeField(auto_now_add=True)
    cor_produto = models.CharField(max_length=50, blank=True, null=True)
    logo = models.ImageField(upload_to=logo_upload_path, blank=True, null=True)

    def __str__(self):
        return f"Pedido {self.id} - {self.nome_cliente}"
    

class Transacao(models.Model):
    pagamento_id = models.CharField(max_length=50)
    status = models.CharField(max_length=50)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    data = models.DateTimeField()
    items = models.ManyToManyField('Produto', related_name='transacoes')
    payment_type = models.CharField(max_length=50, blank=True, null=True)
    nome_cliente = models.CharField(max_length=100)
    cpf_cliente = models.CharField(max_length=11)
    endereco_cliente = models.CharField(max_length=255)
    telefone_cliente = models.CharField(max_length=15)
    email_cliente = models.EmailField(max_length=100, blank=True, null=True)
    data_nascimento_cliente = models.DateField()
    quantidade = models.PositiveIntegerField()
    data_pedido = models.DateTimeField(auto_now_add=True)
    cor_produto = models.CharField(max_length=50, blank=True, null=True)
    logo = models.ImageField(upload_to=logo_upload_path, blank=True, null=True)

    def __str__(self):
        return f"Transação {self.pagamento_id} - {self.status}"