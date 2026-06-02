from django.db import migrations


FIXED_SECTIONS = [
    {
        "tipo": "hero_principal",
        "slug": "hero-principal",
        "ancora": "hero",
        "ordem": 0,
        "etiqueta": "Produto exclusivo para eventos, festas e negócios",
        "titulo": "Chopeira Bomba de Gasolina: A Máquina de Fazer Dinheiro",
        "descricao": "Produto exclusivo para venda de chopp em locais estratégicos, eventos, festas, praias, agregar valor ao seu negócio ou até mesmo para uso pessoal.",
        "texto_final": "Fature mais de 2 mil reais com um único barril.",
        "fundo": "bege",
        "cor_titulo": "vermelho",
    },
    {"tipo": "barra_confianca", "slug": "barra-confianca", "ordem": 5, "titulo": "Barra de confiança"},
    {
        "tipo": "produtos",
        "slug": "produtos",
        "ancora": "produtos",
        "ordem": 10,
        "etiqueta": "Escolha o modelo ideal",
        "titulo": "Chopeiras prontas para vender mais",
        "descricao": "Todas podem receber sua marca e suas cores. O objetivo é simples: chamar atenção, passar confiança e facilitar a venda do chopp.",
        "fundo": "bege",
    },
    {
        "tipo": "eventos",
        "slug": "eventos",
        "ancora": "eventos",
        "ordem": 30,
        "etiqueta": "Venda onde houver gente reunida",
        "titulo": "Festa, praia ou casamento: sua chopeira vira ponto de venda.",
        "descricao": "O visual chama, a curiosidade aproxima e o chopp gelado fecha a venda. Leve a operação para horários de pico, eventos privados e lugares de grande circulação sem depender de um ponto fixo.",
        "fundo": "bege",
    },
    {"tipo": "passos", "slug": "como-funciona", "ordem": 40, "titulo": "Como funciona", "fundo": "marrom", "cor_titulo": "amarelo"},
    {
        "tipo": "beneficios",
        "slug": "beneficios",
        "ordem": 50,
        "etiqueta": "Por que escolher a Dona do Chopp?",
        "titulo": "Você não compra apenas uma chopeira.",
        "fundo": "bege",
    },
    {
        "tipo": "video",
        "slug": "video-principal",
        "ordem": 60,
        "etiqueta": "Veja em uso",
        "titulo": "O visual faz o cliente chegar perto.",
        "descricao": "O vídeo mostra a chopeira em ação e ajuda você a imaginar como ela aparece no atendimento real.",
        "fundo": "branco",
    },
    {
        "tipo": "depoimentos",
        "slug": "depoimentos",
        "ancora": "depoimentos",
        "ordem": 70,
        "etiqueta": "Depoimentos",
        "titulo": "Quem coloca para vender mostra o resultado na prática.",
        "descricao": "Veja clientes, eventos e operações reais usando a chopeira para chamar atenção, atender melhor e transformar movimento em faturamento.",
        "fundo": "marrom",
        "cor_titulo": "amarelo",
    },
    {
        "tipo": "personalizar",
        "slug": "personalizar",
        "ancora": "personalizar",
        "ordem": 80,
        "etiqueta": "Teste sua marca",
        "titulo": "Veja sua logo na chopeira.",
        "descricao": "Envie uma imagem da sua marca e ajuste a prévia direto no círculo superior do equipamento.",
        "fundo": "bege",
    },
    {
        "tipo": "prova_social",
        "slug": "prova-social",
        "ancora": "prova",
        "ordem": 90,
        "etiqueta": "Prova social",
        "titulo": "Quem comprou recomenda.",
        "descricao": "Avaliações reais, publicadas no Google.",
        "fundo": "bege",
    },
    {
        "tipo": "galeria",
        "slug": "galeria",
        "ordem": 100,
        "etiqueta": "Galeria",
        "titulo": "Modelos que chamam atenção.",
        "descricao": "Algumas combinações de cores, marcas e acabamentos que fazem a chopeira aparecer no balcão, no evento e nas fotos.",
        "fundo": "branco",
    },
    {
        "tipo": "faq",
        "slug": "faq",
        "ancora": "faq",
        "ordem": 110,
        "etiqueta": "Ainda ficou com dúvidas?",
        "titulo": "Fale com nossa equipe e receba atendimento personalizado.",
        "descricao": "Entenda como começar seu negócio com chopp, escolha o modelo ideal e tire suas dúvidas sobre operação, pagamento e personalização.",
        "fundo": "bege",
    },
    {
        "tipo": "contato",
        "slug": "contato",
        "ancora": "contato",
        "ordem": 120,
        "etiqueta": "Ainda ficou com dúvidas?",
        "titulo": "Pergunte ou fale com um especialista.",
        "descricao": "Fale com nossa equipe e receba atendimento personalizado para entender como começar seu negócio com chopp.",
        "fundo": "branco",
    },
    {
        "tipo": "fechamento",
        "slug": "fechamento",
        "ordem": 130,
        "etiqueta": "Fechamento",
        "titulo": "Você não compra apenas uma chopeira. Investe em uma máquina de faturamento.",
        "descricao": "Um produto validado, lucrativo e respaldado por quem realmente entende do mercado de chopp. Fale com nossa equipe e veja como começar.",
        "fundo": "marrom",
        "cor_titulo": "branco",
    },
    {"tipo": "logo_footer", "slug": "logo-footer", "ordem": 140, "titulo": "Logo do rodapé"},
]


MEDIA_TO_SECTION = {
    "hero_principal": "hero_principal",
    "lucro_operacao": "lucro",
    "video_thumb": "video",
    "video_principal": "video",
    "prova_social": "prova_social",
    "galeria": "galeria",
    "logo_footer": "logo_footer",
}


def seed_unified_sections(apps, schema_editor):
    SecaoLanding = apps.get_model("home", "SecaoLanding")
    SecaoLandingMidia = apps.get_model("home", "SecaoLandingMidia")
    MidiaLanding = apps.get_model("home", "MidiaLanding")
    BlocoFixoLanding = apps.get_model("home", "BlocoFixoLanding")

    blocos = {bloco.chave: bloco for bloco in BlocoFixoLanding.objects.all()}

    for data in FIXED_SECTIONS:
        bloco = blocos.get(data["tipo"])
        defaults = {
            "ancora": data.get("ancora", ""),
            "tipo": data["tipo"],
            "etiqueta": data.get("etiqueta", ""),
            "titulo": data["titulo"],
            "descricao": data.get("descricao", ""),
            "texto_final": data.get("texto_final", ""),
            "fundo": data.get("fundo", "branco"),
            "cor_titulo": data.get("cor_titulo", "vermelho"),
            "ordem": bloco.ordem if bloco else data["ordem"],
            "ativo": bloco.ativo if bloco else True,
        }
        SecaoLanding.objects.get_or_create(
            slug=data["slug"],
            defaults=defaults,
        )

    secoes_por_tipo = {secao.tipo: secao for secao in SecaoLanding.objects.all()}
    secoes_por_slug = {secao.slug: secao for secao in SecaoLanding.objects.all()}

    for midia in MidiaLanding.objects.all():
        destino = MEDIA_TO_SECTION.get(midia.chave)
        if not destino or not midia.arquivo:
            continue
        secao = secoes_por_slug.get(destino) or secoes_por_tipo.get(destino)
        if not secao:
            continue
        papel = "principal"
        if midia.chave == "video_thumb":
            papel = "capa"
        elif midia.chave in ("galeria", "prova_social"):
            papel = "item"
        SecaoLandingMidia.objects.get_or_create(
            secao=secao,
            arquivo=midia.arquivo,
            defaults={
                "tipo": midia.tipo,
                "papel": papel,
                "titulo": midia.titulo,
                "descricao": midia.descricao,
                "link": midia.link,
                "ordem": midia.ordem,
                "ativo": midia.ativo,
            },
        )


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("home", "0015_alter_secaolanding_tipo_secaolandingmidia"),
    ]

    operations = [
        migrations.RunPython(seed_unified_sections, noop_reverse),
    ]
