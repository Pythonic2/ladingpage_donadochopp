from django.db import models
from django.templatetags.static import static
from django.urls import reverse
from django.utils.text import slugify
import os
from ckeditor.fields import RichTextField


def logo_upload_path(instance, filename):
    ext = filename.split(".")[-1]
    filename = f"{instance.cpf_cliente}_logo.{ext}"
    return os.path.join("logos", filename)


class Produto(models.Model):
    imagem = models.ImageField(upload_to="produtos/", blank=True, null=True)
    nome = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True, blank=True, null=True)
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

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.nome) or "produto"
            slug = base_slug
            counter = 2
            while Produto.objects.exclude(pk=self.pk).filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("produto-detalhe-slug", kwargs={"slug": self.slug})

    def get_checkout_url(self):
        return reverse("cadastrar-usuario-slug", kwargs={"slug": self.slug})

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


class ConfiguracaoLanding(models.Model):
    url_publica_site = models.URLField(
        blank=True,
        help_text="URL pública usada em links enviados no WhatsApp. Ex: https://vendas1.donadochopp.com.br",
    )
    mostrar_barra_topo = models.BooleanField(default=True)
    texto_barra_topo = models.CharField(
        max_length=140,
        default="Oferta ativa: 10% off no PIX para todo o Brasil",
        blank=True,
    )
    modo_black_friday = models.BooleanField(default=False)
    texto_selo_black = models.CharField(
        max_length=80,
        default="Black Friday",
        blank=True,
    )
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Configuração da landing"
        verbose_name_plural = "Configuração da landing"

    def __str__(self):
        return "Configuração da landing"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get_solo(cls):
        obj, _created = cls.objects.get_or_create(pk=1)
        return obj


def landing_media_upload_path(instance, filename):
    return os.path.join("landing", instance.chave, filename)


def landing_section_upload_path(instance, filename):
    return os.path.join("landing", "secoes", instance.slug, filename)


def landing_section_media_upload_path(instance, filename):
    return os.path.join("landing", "secoes", instance.secao.slug, filename)


class MidiaLanding(models.Model):
    CHAVE_CHOICES = [
        ("hero_principal", "Hero principal"),
        ("lucro_operacao", "Lucro - operação"),
        ("video_thumb", "Vídeo principal - capa"),
        ("video_principal", "Vídeo principal - arquivo"),
        ("prova_social", "Prova social"),
        ("galeria", "Galeria"),
        ("logo_header", "Logo do cabeçalho"),
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
        ordering = ["ordem", "chave", "-criado_em"]
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


class SecaoLanding(models.Model):
    TIPO_CHOICES = [
        ("hero_principal", "Hero principal"),
        ("barra_confianca", "Barra de confiança"),
        ("produtos", "Produtos"),
        ("metricas_tabela", "Texto, cards e tabela"),
        ("painel_destaque", "Painel de destaque"),
        ("eventos", "Eventos"),
        ("passos", "Como funciona"),
        ("beneficios", "Benefícios"),
        ("video", "Vídeo"),
        ("depoimentos", "Depoimentos"),
        ("personalizar", "Personalizar"),
        ("prova_social", "Prova social"),
        ("galeria", "Galeria"),
        ("faq", "FAQ"),
        ("contato", "Contato"),
        ("fechamento", "Fechamento"),
        ("logo_header", "Logo do cabeçalho"),
        ("logo_footer", "Logo do rodapé"),
    ]

    FUNDO_CHOICES = [
        ("branco", "Branco"),
        ("bege", "Bege"),
        ("marrom", "Marrom"),
    ]

    COR_CHOICES = [
        ("vermelho", "Vermelho"),
        ("amarelo", "Amarelo"),
        ("marrom", "Marrom"),
        ("branco", "Branco"),
    ]

    slug = models.SlugField(
        max_length=80,
        unique=True,
        help_text="Usado como identificador interno e na URL da seção.",
    )
    ancora = models.CharField(
        max_length=80,
        blank=True,
        help_text="ID usado no menu/âncora. Se ficar vazio, usa o slug.",
    )
    tipo = models.CharField(max_length=30, choices=TIPO_CHOICES, default="metricas_tabela")
    etiqueta = models.CharField(max_length=140, blank=True)
    titulo = models.CharField(max_length=220)
    titulo_destaque = models.CharField(
        max_length=160,
        blank=True,
        help_text="Trecho do título que deve receber cor diferente.",
    )
    cor_titulo_destaque = models.CharField(
        max_length=40,
        default="#169b4f",
        help_text="Cor aplicada ao trecho destacado. Use #169b4f, rgb(22,155,79), rgba(...) ou hsl(...).",
    )
    descricao = models.TextField(blank=True)
    texto_final = models.TextField(blank=True)
    observacao = models.TextField(blank=True)
    imagem = models.FileField(upload_to=landing_section_upload_path, blank=True)
    imagem_titulo = models.CharField(max_length=140, blank=True)
    cabecalho_tabela_esquerda = models.CharField(max_length=80, blank=True)
    cabecalho_tabela_direita = models.CharField(max_length=80, blank=True)
    destaque_etiqueta = models.CharField(max_length=140, blank=True)
    destaque_valor = models.CharField(max_length=80, blank=True)
    destaque_descricao = models.CharField(max_length=180, blank=True)
    destaque_observacao = models.TextField(blank=True)
    fundo = models.CharField(max_length=10, choices=FUNDO_CHOICES, default="branco")
    cor_titulo = models.CharField(max_length=10, choices=COR_CHOICES, default="vermelho")
    ordem = models.PositiveIntegerField(default=0)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["ordem", "-criado_em"]
        verbose_name = "Seção da landing"
        verbose_name_plural = "Seções da landing"

    def __str__(self):
        return self.titulo

    @property
    def anchor_id(self):
        return self.ancora or self.slug

    @property
    def background_class(self):
        return {
            "branco": "bg-white text-ink",
            "bege": "bg-cream text-ink",
            "marrom": "bg-ink text-white",
        }.get(self.fundo, "bg-white text-ink")

    @property
    def highlight_text_class(self):
        return {
            "vermelho": "text-flame",
            "amarelo": "text-beer",
            "marrom": "text-ink",
            "branco": "text-white",
        }.get(self.cor_titulo, "text-flame")

    @property
    def body_text_class(self):
        return "text-white/70" if self.fundo == "marrom" else "text-ink/62"

    @property
    def muted_text_class(self):
        return "text-white/62" if self.fundo == "marrom" else "text-ink/55"

    @property
    def small_text_class(self):
        return "text-white/45" if self.fundo == "marrom" else "text-ink/45"

    @property
    def card_class(self):
        return "bg-white/10" if self.fundo == "marrom" else "bg-cream"

    @property
    def table_class(self):
        return "border border-ink/10 bg-cream text-ink" if self.fundo != "marrom" else "border border-white/10 bg-white/10 text-white"

    @property
    def table_header_class(self):
        return "bg-ink text-white" if self.fundo != "marrom" else "bg-white text-ink"

    @property
    def table_row_highlight_class(self):
        return "bg-white" if self.fundo != "marrom" else "bg-white/10"

    @property
    def imagem_segura_url(self):
        if self.imagem and self.imagem.name and self.imagem.storage.exists(self.imagem.name):
            return self.imagem.url
        return ""

    @property
    def midias_ativas(self):
        return self.midias.filter(ativo=True)

    @property
    def primeira_midia(self):
        return self.midias_ativas.first()

    @property
    def primeira_imagem(self):
        return self.midias_ativas.filter(tipo="imagem").first()

    @property
    def primeiro_video(self):
        return self.midias_ativas.filter(tipo="video").first()


class SecaoLandingMidia(models.Model):
    TIPO_CHOICES = [
        ("imagem", "Imagem"),
        ("video", "Vídeo"),
    ]

    PAPEL_CHOICES = [
        ("principal", "Principal"),
        ("desktop", "Desktop"),
        ("mobile", "Mobile"),
        ("logo_header", "Logo do cabeçalho"),
        ("capa", "Capa do vídeo"),
        ("item", "Item da galeria/lista"),
    ]

    secao = models.ForeignKey(SecaoLanding, on_delete=models.CASCADE, related_name="midias")
    arquivo = models.FileField(upload_to=landing_section_media_upload_path)
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, default="imagem")
    papel = models.CharField(max_length=12, choices=PAPEL_CHOICES, default="principal")
    titulo = models.CharField(max_length=120, blank=True)
    descricao = models.CharField(max_length=220, blank=True)
    link = models.URLField(blank=True)
    ordem = models.PositiveIntegerField(default=0)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-criado_em", "-id"]
        verbose_name = "Mídia da seção"
        verbose_name_plural = "Mídias da seção"

    def __str__(self):
        return self.titulo or self.arquivo.name

    @property
    def arquivo_seguro_url(self):
        if self.arquivo and self.arquivo.name and self.arquivo.storage.exists(self.arquivo.name):
            return self.arquivo.url
        return static("assets/images/logo2.png")


class SecaoLandingCard(models.Model):
    secao = models.ForeignKey(SecaoLanding, on_delete=models.CASCADE, related_name="cards")
    titulo = models.CharField(max_length=120)
    valor = models.CharField(max_length=80, blank=True)
    descricao = models.TextField(blank=True)
    ordem = models.PositiveIntegerField(default=0)
    ativo = models.BooleanField(default=True)

    class Meta:
        ordering = ["ordem", "id"]
        verbose_name = "Card da seção"
        verbose_name_plural = "Cards da seção"

    def __str__(self):
        return self.titulo


class SecaoLandingLinhaTabela(models.Model):
    secao = models.ForeignKey(SecaoLanding, on_delete=models.CASCADE, related_name="linhas_tabela")
    rotulo = models.CharField(max_length=140)
    valor = models.CharField(max_length=80)
    destacar = models.BooleanField(default=False)
    ordem = models.PositiveIntegerField(default=0)
    ativo = models.BooleanField(default=True)

    class Meta:
        ordering = ["ordem", "id"]
        verbose_name = "Linha de tabela da seção"
        verbose_name_plural = "Linhas de tabela da seção"

    def __str__(self):
        return f"{self.rotulo}: {self.valor}"


class BlocoFixoLanding(models.Model):
    CHAVE_CHOICES = [
        ("barra_confianca", "Barra de confiança"),
        ("produtos", "Produtos"),
        ("eventos", "Eventos"),
        ("passos", "Como funciona"),
        ("beneficios", "Benefícios"),
        ("video", "Vídeo"),
        ("depoimentos", "Depoimentos"),
        ("personalizar", "Personalizar"),
        ("prova_social", "Prova social"),
        ("galeria", "Galeria"),
        ("faq", "FAQ"),
        ("contato", "Contato"),
        ("fechamento", "Fechamento"),
    ]

    chave = models.CharField(max_length=30, choices=CHAVE_CHOICES, unique=True)
    ordem = models.PositiveIntegerField(default=0)
    ativo = models.BooleanField(default=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["ordem", "chave"]
        verbose_name = "Bloco fixo da landing"
        verbose_name_plural = "Blocos fixos da landing"

    def __str__(self):
        return self.get_chave_display()


class Pedido(models.Model):
    TIPO_ENTREGA_CHOICES = [
        ("retirada_aeroporto", "Retirada grátis no aeroporto da capital"),
        ("receber_em_casa", "Receber em casa - chamar especialista"),
    ]

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
    cpf_cliente = models.CharField(max_length=11, unique=False)
    endereco_cliente = models.CharField(max_length=255)
    cep_cliente = models.CharField(max_length=9)
    tipo_entrega = models.CharField(
        max_length=30,
        choices=TIPO_ENTREGA_CHOICES,
        default="retirada_aeroporto",
    )
    capital_retirada = models.CharField(max_length=80, blank=True)
    telefone_cliente = models.CharField(max_length=15)
    email_cliente = models.EmailField(
        max_length=100, blank=True, null=True, unique=False
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
    tipo_entrega = models.CharField(max_length=30, blank=True, null=True)
    capital_retirada = models.CharField(max_length=80, blank=True)
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
