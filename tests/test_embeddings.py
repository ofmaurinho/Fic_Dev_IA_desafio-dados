import numpy as np

from src.embeddings.gerador import (
    calcular_hash_texto,
    calcular_idf,
    carregar_vocabulario,
    extrair_termos,
    gerar_embedding,
    gerar_embedding_conteudo,
    identificar_modelo,
    normalizar_texto,
    preparar_texto,
    salvar_vocabulario,
    tokenizar
)


CONTEUDOS = [
    {
        "titulo": "Fundamentos de Banco de Dados",
        "descricao": "Curso sobre modelagem relacional e PostgreSQL."
    },
    {
        "titulo": "Segurança em APIs",
        "descricao": "Curso sobre prevenção de vazamentos em APIs."
    },
    {
        "titulo": "Machine Learning Supervisionado",
        "descricao": "Curso sobre classificação com Scikit-Learn."
    }
]


def test_normalizar_texto_remove_acentos_e_maiusculas():
    assert normalizar_texto("Inteligência ARTIFICIAL") == "inteligencia artificial"


def test_tokenizar_remove_stopwords_e_palavras_curtas():
    assert tokenizar("Quero aprender sobre banco de dados em IA") == [
        "aprender",
        "banco",
        "dados"
    ]


def test_extrair_termos_inclui_bigramas():
    assert extrair_termos("banco de dados relacional") == [
        "banco",
        "dados",
        "relacional",
        "banco_dados",
        "dados_relacional"
    ]


def test_preparar_texto_une_titulo_e_descricao():
    texto = preparar_texto("  Título  ", " Descrição   com   espaços ")

    assert texto == "Título. Descrição com espaços"


def test_calcular_hash_texto_deterministico():
    assert calcular_hash_texto("abc") == calcular_hash_texto("abc")
    assert calcular_hash_texto("abc") != calcular_hash_texto("abd")
    assert len(calcular_hash_texto("abc")) == 64


def test_calcular_idf_penaliza_termos_comuns():
    idf = calcular_idf(CONTEUDOS)

    assert idf["curso"] == 0
    assert idf["postgresql"] > 0


def test_gerar_embedding_deterministico_e_normalizado():
    idf = calcular_idf(CONTEUDOS)

    vetor_1 = gerar_embedding("banco de dados postgresql", 64, idf)
    vetor_2 = gerar_embedding("banco de dados postgresql", 64, idf)

    assert vetor_1.shape == (64,)
    assert np.array_equal(vetor_1, vetor_2)
    assert np.isclose(np.linalg.norm(vetor_1), 1.0)


def test_gerar_embedding_termos_desconhecidos_retorna_vetor_nulo():
    idf = calcular_idf(CONTEUDOS)

    vetor = gerar_embedding("culinária italiana", 64, idf)

    assert not np.any(vetor)


def test_textos_relacionados_sao_mais_similares():
    idf = calcular_idf(CONTEUDOS)

    vetores = [
        gerar_embedding_conteudo(
            conteudo["titulo"], conteudo["descricao"], 256, 2, idf
        )
        for conteudo in CONTEUDOS
    ]

    consulta = gerar_embedding("modelagem de banco de dados", 256, idf)

    similaridades = [float(vetor @ consulta) for vetor in vetores]

    assert similaridades[0] == max(similaridades)


def test_identificar_modelo_muda_com_vocabulario():
    idf_1 = calcular_idf(CONTEUDOS)
    idf_2 = calcular_idf(CONTEUDOS[:2])

    assert identificar_modelo("simulado", 64, idf_1) == identificar_modelo(
        "simulado", 64, idf_1
    )
    assert identificar_modelo("simulado", 64, idf_1) != identificar_modelo(
        "simulado", 64, idf_2
    )
    assert identificar_modelo("simulado", 64, idf_1).startswith("simulado:64d:")


def test_salvar_e_carregar_vocabulario(tmp_path):
    idf = calcular_idf(CONTEUDOS)
    caminho = tmp_path / "vocabulario.json"

    salvar_vocabulario(idf, caminho)

    assert carregar_vocabulario(caminho) == idf
