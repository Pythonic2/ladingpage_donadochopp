from django import forms
from .models import Pedido, ProdutoVariacao


CAPITAL_CEP_RANGES = [
    ("Rio Branco - AC", 69900000, 69924999),
    ("Maceió - AL", 57000000, 57099999),
    ("Macapá - AP", 68900000, 68914999),
    ("Manaus - AM", 69000000, 69099999),
    ("Salvador - BA", 40000000, 42599999),
    ("Fortaleza - CE", 60000000, 60999999),
    ("Brasília - DF", 70000000, 73699999),
    ("Vitória - ES", 29000000, 29099999),
    ("Goiânia - GO", 74000000, 74899999),
    ("São Luís - MA", 65000000, 65099999),
    ("Cuiabá - MT", 78000000, 78109999),
    ("Campo Grande - MS", 79000000, 79129999),
    ("Belo Horizonte - MG", 30000000, 31999999),
    ("Belém - PA", 66000000, 66999999),
    ("João Pessoa - PB", 58000000, 58099999),
    ("Curitiba - PR", 80000000, 82999999),
    ("Recife - PE", 50000000, 52999999),
    ("Teresina - PI", 64000000, 64099999),
    ("Rio de Janeiro - RJ", 20000000, 23799999),
    ("Natal - RN", 59000000, 59139999),
    ("Porto Alegre - RS", 90000000, 91999999),
    ("Porto Velho - RO", 76800000, 76849999),
    ("Boa Vista - RR", 69300000, 69339999),
    ("Florianópolis - SC", 88000000, 88099999),
    ("São Paulo - SP", 1000000, 5999999),
    ("São Paulo - SP", 8000000, 8499999),
    ("Aracaju - SE", 49000000, 49099999),
    ("Palmas - TO", 77000000, 77249999),
]


def capital_por_cep(cep):
    digits = "".join(char for char in str(cep or "") if char.isdigit())
    if len(digits) != 8:
        return ""
    cep_number = int(digits)
    for capital, start, end in CAPITAL_CEP_RANGES:
        if start <= cep_number <= end:
            return capital
    return ""


class PedidoForm(forms.ModelForm):
    produto_variacao = forms.ModelChoiceField(
        queryset=ProdutoVariacao.objects.none(),
        required=False,
        label="Variação do produto",
        empty_label="Selecione a variação desejada",
        widget=forms.Select(attrs={'class': 'form-group'}),
    )

    class Meta:
        model = Pedido
        fields = [
            'nome_cliente',
            'email_cliente',
            'telefone_cliente',
            'cpf_cliente',
            'endereco_cliente',
            'cep_cliente',
            'tipo_entrega',
            'capital_retirada',
            'data_nascimento_cliente',
            'quantidade',
            'produto_variacao',
            'logo'
        ]
        labels = {
            'nome_cliente': 'NOME (Obrigatório)',
            'email_cliente': 'EMAIL (Obrigatório)',
            'telefone_cliente': 'Celular (Obrigatório)',
            'cpf_cliente': 'CPF (Obrigatório)',
            'endereco_cliente': 'ENDEREÇO (Obrigatório)',
            'cep_cliente': 'CEP DA CAPITAL PARA RETIRADA (Obrigatório)',
            'tipo_entrega': 'FORMA DE ENTREGA',
            'capital_retirada': 'CAPITAL IDENTIFICADA',
            'data_nascimento_cliente': 'DATA DE NASCIMENTO (Obrigatório)',
            'quantidade': 'QUANTIDADE (Obrigatório)',
            'produto_variacao': 'VARIAÇÃO DO PRODUTO',
            'logo': 'LOGO',
        }
        widgets = {
            'nome_cliente': forms.TextInput(attrs={'class': 'form-group'}),
            'email_cliente': forms.EmailInput(attrs={'class': 'form-group'}),
            'telefone_cliente': forms.TextInput(attrs={'class': 'form-group'}),
            'cpf_cliente': forms.TextInput(attrs={'class': 'form-group', 'type': 'text'}),
            'endereco_cliente': forms.TextInput(attrs={'class': 'form-group'}),
            'cep_cliente': forms.TextInput(attrs={'class': 'form-group', 'placeholder': '00000-000', 'maxlength': '9'}),
            'tipo_entrega': forms.RadioSelect(),
            'capital_retirada': forms.HiddenInput(),
            'data_nascimento_cliente': forms.DateInput(attrs={'class': 'form-group', 'type': 'date'}),
            'quantidade': forms.NumberInput(attrs={'class': 'form-group'}),
            'logo': forms.FileInput(attrs={'class': 'form-group'}),
        }

    def __init__(self, *args, produto=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.produto = produto
        variacoes = ProdutoVariacao.objects.none()
        if produto:
            variacoes = produto.variacoes_ativas
        self.fields["produto_variacao"].queryset = variacoes
        self.fields["produto_variacao"].required = variacoes.exists()
        if not produto or not produto.solicitar_logo:
            self.fields.pop("logo", None)

    def clean(self):
        cleaned_data = super().clean()
        tipo_entrega = cleaned_data.get("tipo_entrega")
        cep_cliente = cleaned_data.get("cep_cliente")
        produto_variacao = cleaned_data.get("produto_variacao")

        if tipo_entrega == "receber_em_casa":
            raise forms.ValidationError(
                "Para receber em casa, chame um especialista pelo WhatsApp para calcular o frete."
            )

        if self.produto and self.produto.tem_variacoes:
            if not produto_variacao:
                self.add_error(
                    "produto_variacao",
                    "Selecione a variação desejada para este produto.",
                )
            elif produto_variacao.produto_id != self.produto.id:
                self.add_error(
                    "produto_variacao",
                    "Selecione uma variação válida para este produto.",
                )

        capital = capital_por_cep(cep_cliente)
        if not capital:
            self.add_error(
                "cep_cliente",
                "Informe um CEP válido de capital. A retirada grátis é nos aeroportos das capitais.",
            )
        else:
            cleaned_data["capital_retirada"] = capital
        return cleaned_data
