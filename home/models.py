from django.db import models
from django.templatetags.static import static
import os
from ckeditor.fields import RichTextField


def logo_upload_path(instance, filename):
    ext = filename.split(".")[-1]
    filename = f"{instance.cpf_cliente}_logo.{ext}"
    return os.path.join("logos", filename)


class Produto(models.Model):
    imagem = models.ImageField(upload_to="produtos/", blank=True, null=True)
    nome = models.CharField(max_length=100)
    descricao = RichTextField()
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    preco_sem_desconto = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.0
    )
    estoque = models.PositiveIntegerField()
    peso = models.DecimalField(max_digits=5, decimal_places=2, help_text="Peso em kg")
    altura = models.DecimalField(
        max_digits=5, decimal_places=2, help_text="Altura em cm"
    )
    largura = models.DecimalField(
        max_digits=5, decimal_places=2, help_text="Largura em cm"
    )
    comprimento = models.DecimalField(
        max_digits=5, decimal_places=2, help_text="Comprimento em cm"
    )
    cep_origem = models.CharField(
        default="58074158", max_length=9, blank=True, null=True
    )

    def __str__(self):
        return self.nome

    @property
    def imagem_segura_url(self):
        if self.imagem and self.imagem.name and self.imagem.storage.exists(self.imagem.name):
            return self.imagem.url

        nome = self.nome.lower()
        if "carrinho" in nome or "combo" in nome:
            return static("assets/images/fullcombo.png")
        return static("assets/images/bomba2.png")


class Evento(models.Model):
    imagem = models.ImageField(upload_to="eventos/")
    categoria = models.CharField(max_length=80, default="Evento")
    titulo = models.CharField(max_length=120)
    descricao = models.CharField(max_length=180, blank=True)
    ordem = models.PositiveIntegerField(default=0)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["ordem", "-criado_em"]
        verbose_name = "Evento"
        verbose_name_plural = "Eventos"

    def __str__(self):
        return self.titulo


class Depoimento(models.Model):
    TIPO_MIDIA_CHOICES = [
        ("video", "Video"),
        ("imagem", "Imagem"),
    ]

    arquivo = models.FileField(upload_to="depoimentos/")
    tipo_midia = models.CharField(max_length=10, choices=TIPO_MIDIA_CHOICES)
    nome_cliente = models.CharField(max_length=100)
    contexto = models.CharField(max_length=120, blank=True)
    texto = models.CharField(max_length=220, blank=True)
    ordem = models.PositiveIntegerField(default=0)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["ordem", "-criado_em"]
        verbose_name = "Depoimento"
        verbose_name_plural = "Depoimentos"

    def __str__(self):
        return self.nome_cliente


def landing_media_upload_path(instance, filename):
    return os.path.join("landing", instance.chave, filename)


class MidiaLanding(models.Model):
    CHAVE_CHOICES = [
        ("hero_principal", "Hero principal"),
        ("lucro_operacao", "Lucro - operação"),
        ("video_thumb", "Vídeo principal - capa"),
        ("video_principal", "Vídeo principal - arquivo"),
        ("prova_social", "Prova social"),
        ("galeria", "Galeria"),
        ("logo_footer", "Logo do rodapé"),
    ]

    TIPO_CHOICES = [
        ("imagem", "Imagem"),
        ("video", "Vídeo"),
    ]

    chave = models.CharField(max_length=40, choices=CHAVE_CHOICES)
    arquivo = models.FileField(upload_to=landing_media_upload_path)
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, default="imagem")
    titulo = models.CharField(max_length=120)
    descricao = models.CharField(max_length=220, blank=True)
    link = models.URLField(blank=True)
    ordem = models.PositiveIntegerField(default=0)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["chave", "ordem", "-criado_em"]
        verbose_name = "Mídia da landing"
        verbose_name_plural = "Mídias da landing"

    def __str__(self):
        return f"{self.get_chave_display()} - {self.titulo}"

    @property
    def arquivo_seguro_url(self):
        if self.arquivo and self.arquivo.name and self.arquivo.storage.exists(self.arquivo.name):
            return self.arquivo.url

        fallbacks = {
            "hero_principal": "assets/images/aed46108-0684-4c51-ad43-86fcb4425c8b.png",
            "lucro_operacao": "assets/images/praia.jpeg",
            "video_thumb": "assets/images/thumb.jpeg",
            "video_principal": "assets/images/video-convertido.mp4",
            "logo_footer": "assets/images/logo.jpeg",
        }
        fallback = fallbacks.get(self.chave, "assets/images/logo2.png")
        return static(fallback)


class Pedido(models.Model):
    CORES_CHOICES = [
        ("amarela_vermelha", "Amarela e vermelha"),
        ("amarela_preta", "Amarela e preta"),
        ("laranja_preta", "Laranja e preta"),
        ("branca_preta", "Branca e preta"),
        ("vermelha", "Vermelha"),
        ("rosa_preta", "Rosa e preta"),
        ("verde_branca", "Verde e branca"),
        ("vermelha_preta", "Vermelha e preta"),
        ("preta_verde", "Preta e verde"),
        ("azul_vermelha", "Azul e vermelha"),
    ]

    nome_cliente = models.CharField(max_length=100)
    cpf_cliente = models.CharField(max_length=11, unique=True)
    endereco_cliente = models.CharField(max_length=255)
    cep_cliente = models.CharField(max_length=9, blank=True, null=True)
    telefone_cliente = models.CharField(max_length=15)
    email_cliente = models.EmailField(
        max_length=100, blank=True, null=True, unique=True
    )
    data_nascimento_cliente = models.DateField()
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField()
    data_pedido = models.DateTimeField(auto_now_add=True)
    cor_produto = models.CharField(
        max_length=50, choices=CORES_CHOICES, blank=True, null=True
    )
    logo = models.ImageField(upload_to=logo_upload_path, blank=True, null=True)

    def __str__(self):
        return f"Pedido {self.id} - {self.nome_cliente}"


class Transacao(models.Model):
    pagamento_id = models.CharField(max_length=50)
    status = models.CharField(max_length=50)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    data = models.DateTimeField()
    items = models.ManyToManyField("Produto", related_name="transacoes")
    payment_type = models.CharField(max_length=50, blank=True, null=True)
    nome_cliente = models.CharField(max_length=100)
    cpf_cliente = models.CharField(max_length=11)
    endereco_cliente = models.CharField(max_length=255)
    cep_cliente = models.CharField(max_length=9, blank=True, null=True)
    telefone_cliente = models.CharField(max_length=15)
    email_cliente = models.EmailField(max_length=100, blank=True, null=True)
    data_nascimento_cliente = models.DateField()
    quantidade = models.PositiveIntegerField()
    data_pedido = models.DateTimeField(auto_now_add=True)
    cor_produto = models.CharField(max_length=50, blank=True, null=True)
    logo = models.ImageField(upload_to=logo_upload_path, blank=True, null=True)

    def __str__(self):
        return f"Transação {self.pagamento_id} - {self.status}"


class Pergunta(models.Model):
    nome = models.CharField(max_length=100)
    whatsapp = models.CharField(max_length=20)
    mensagem = models.TextField()
    resposta = models.TextField(blank=True, null=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-criado_em"]

    def __str__(self):
        return f"{self.nome} — {self.mensagem[:50]}"
