from django import forms
from .models import Pedido

class PedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = [
            'nome_cliente',
            'email_cliente',
            'telefone_cliente',
            'cpf_cliente',
            'endereco_cliente',
            'data_nascimento_cliente',
            'quantidade',
            'cor_produto',
            'logo'
        ]
        labels = {
            'nome_cliente': 'NOME (Obrigatório)',
            'email_cliente': 'EMAIL',
            'telefone_cliente': 'Celular (Obrigatório)',
            'cpf_cliente': 'CPF (Obrigatório)',
            'endereco_cliente': 'ENDEREÇO (Obrigatório)',
            'data_nascimento_cliente': 'DATA DE NASCIMENTO (Obrigatório)',
            'quantidade': 'QUANTIDADE (Obrigatório)',
            'cor_produto': 'COR DO PRODUTO',
            'logo': 'LOGO',
        }
        widgets = {
            'nome_cliente': forms.TextInput(attrs={'class': 'form-group'}),
            'email_cliente': forms.EmailInput(attrs={'class': 'form-group'}),
            'telefone_cliente': forms.TextInput(attrs={'class': 'form-group'}),
            'cpf_cliente': forms.TextInput(attrs={'class': 'form-group', 'type': 'text'}),
            'endereco_cliente': forms.TextInput(attrs={'class': 'form-group'}),
            'data_nascimento_cliente': forms.DateInput(attrs={'class': 'form-group', 'type': 'date'}),
            'quantidade': forms.NumberInput(attrs={'class': 'form-group'}),
            'cor_produto': forms.Select(attrs={'class': 'form-group'}),
            'logo': forms.FileInput(attrs={'class': 'form-group'}),
        }