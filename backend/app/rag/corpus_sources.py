from dataclasses import dataclass


@dataclass(frozen=True)
class CorpusSource:
    url: str
    topic: str


# The mandatory source (proposal) plus 6 additional Getnet Brasil pages
# covering every required topic: Get Clássica, Get Smart, Payment Link
# (including selling via WhatsApp), antecipação de recebíveis, and general
# FAQ/blog content. Real, publicly reachable URLs verified during
# implementation (see README's ingestion manifest for the fetch date).
CORPUS_SOURCES: list[CorpusSource] = [
    CorpusSource(
        url="https://www.getnet.net/en",
        topic="institutional",
    ),
    CorpusSource(
        url="https://site.getnet.com.br/maquininha/get-classica/",
        topic="get-classica",
    ),
    CorpusSource(
        url="https://site.getnet.com.br/get-ajuda-maquininha/solucoes-get-smart/",
        topic="get-smart",
    ),
    CorpusSource(
        url="https://site.getnet.com.br/link-de-pagamento/",
        topic="payment-link",
    ),
    CorpusSource(
        url="https://site.getnet.com.br/get-ajuda-antecipacao-de-venda/como-antecipar-sua-vendas-pelo-app/",
        topic="antecipacao-recebiveis",
    ),
    CorpusSource(
        url="https://site.getnet.com.br/duvidas/",
        topic="faq",
    ),
    CorpusSource(
        url="https://site.getnet.com.br/link-de-pagamento-getnet/",
        topic="blog-payment-link",
    ),
]
