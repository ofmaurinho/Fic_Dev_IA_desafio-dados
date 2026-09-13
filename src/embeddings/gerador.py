import hashlib
import json
import math
import re
import unicodedata
from collections import Counter

import numpy as np


STOPWORDS = {
    "das", "dos", "uma", "umas", "uns", "nos", "nas", "aos",
    "para", "por", "pela", "pelo", "pelas", "pelos", "com", "sem",
    "sobre", "entre", "ate", "apos", "desde", "que", "qual", "quais",
    "como", "onde", "quando", "porque", "mais", "menos", "muito",
    "sua", "seu", "suas", "seus", "meu", "minha", "este", "esta",
    "esse", "essa", "isso", "isto", "voce", "nao", "sim", "tambem",
    "ser", "ter", "sao", "quero", "gostaria"
}


def normalizar_texto(texto: str) -> str:
    """Converte para minúsculas e remove acentos."""

    texto = unicodedata.normalize("NFKD", texto.lower())

    return "".join(
        caractere for caractere in texto
        if not unicodedata.combining(caractere)
    )


def tokenizar(texto: str) -> list[str]:
    """Separa o texto em palavras relevantes, sem stopwords."""

    palavras = re.findall(r"[a-z0-9]+", normalizar_texto(texto))

    return [
        palavra for palavra in palavras
        if len(palavra) >= 3 and palavra not in STOPWORDS
    ]


def extrair_termos(texto: str) -> list[str]:
    """Retorna as palavras e os pares de palavras consecutivas do texto."""

    palavras = tokenizar(texto)

    bigramas = [
        f"{palavras[i]}_{palavras[i + 1]}"
        for i in range(len(palavras) - 1)
    ]

    return palavras + bigramas


def preparar_texto(titulo: str, descricao: str) -> str:
    """Monta a representação textual do conteúdo a partir de título e descrição."""

    texto = f"{titulo.strip()}. {descricao.strip()}"

    return re.sub(r"\s+", " ", texto)


def calcular_hash_texto(texto: str) -> str:
    """Calcula o hash SHA-256 do texto usado para gerar o embedding."""

    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


def calcular_idf(conteudos: list[dict]) -> dict[str, float]:
    """Calcula o IDF de cada termo do catálogo.

    Termos presentes em todos os conteúdos (frases padrão das descrições)
    recebem peso próximo de zero; termos raros recebem peso maior.
    """

    total = len(conteudos)
    frequencia_documentos = Counter()

    for conteudo in conteudos:
        termos = (
            extrair_termos(conteudo["titulo"])
            + extrair_termos(conteudo["descricao"])
        )
        frequencia_documentos.update(set(termos))

    return {
        termo: round(math.log((1 + total) / (1 + frequencia)), 6)
        for termo, frequencia in sorted(frequencia_documentos.items())
    }


def calcular_assinatura_vocabulario(idf: dict[str, float]) -> str:
    """Retorna uma assinatura curta que identifica o vocabulário."""

    conteudo = json.dumps(idf, sort_keys=True, ensure_ascii=False)

    return hashlib.sha256(conteudo.encode("utf-8")).hexdigest()[:12]


def identificar_modelo(
    nome: str,
    dimensao: int,
    idf: dict[str, float]
) -> str:
    """Monta o identificador do modelo registrado junto aos vetores."""

    assinatura = calcular_assinatura_vocabulario(idf)

    return f"{nome}:{dimensao}d:vocab-{assinatura}"


def salvar_vocabulario(idf: dict[str, float], caminho) -> None:
    """Salva o vocabulário (IDF) utilizado pelo modelo simulado."""

    with open(caminho, "w", encoding="utf-8") as arquivo:
        json.dump(idf, arquivo, ensure_ascii=False, indent=2)


def carregar_vocabulario(caminho) -> dict[str, float]:
    """Carrega o vocabulário (IDF) gerado na etapa de embeddings."""

    with open(caminho, "r", encoding="utf-8") as arquivo:
        return json.load(arquivo)


def acumular_termos(
    vetor: np.ndarray,
    texto: str,
    peso: float,
    idf: dict[str, float]
) -> None:
    """Soma ao vetor a contribuição de cada termo do texto (feature hashing).

    O hash de cada termo define uma posição e um sinal no vetor, e o valor
    somado é o peso do campo multiplicado pelo IDF do termo. Termos fora do
    vocabulário do catálogo são ignorados.
    """

    for termo in extrair_termos(texto):
        peso_termo = idf.get(termo, 0.0)

        if peso_termo == 0:
            continue

        digest = hashlib.sha256(termo.encode("utf-8")).digest()

        indice = int.from_bytes(digest[:4], "little") % len(vetor)
        sinal = 1.0 if digest[4] & 1 else -1.0

        vetor[indice] += sinal * peso * peso_termo


def normalizar_vetor(vetor: np.ndarray) -> np.ndarray:
    """Normaliza o vetor para norma 1; vetores nulos são mantidos."""

    norma = np.linalg.norm(vetor)

    if norma == 0:
        return vetor

    return vetor / norma


def gerar_embedding(
    texto: str,
    dimensao: int,
    idf: dict[str, float]
) -> np.ndarray:
    """Simula o embedding de um texto livre, como uma consulta."""

    vetor = np.zeros(dimensao, dtype=np.float32)

    acumular_termos(vetor, texto, 1.0, idf)

    return normalizar_vetor(vetor)


def gerar_embedding_conteudo(
    titulo: str,
    descricao: str,
    dimensao: int,
    peso_titulo: float,
    idf: dict[str, float]
) -> np.ndarray:
    """Simula o embedding de um conteúdo, com peso maior para o título."""

    vetor = np.zeros(dimensao, dtype=np.float32)

    acumular_termos(vetor, titulo, peso_titulo, idf)
    acumular_termos(vetor, descricao, 1.0, idf)

    return normalizar_vetor(vetor)
