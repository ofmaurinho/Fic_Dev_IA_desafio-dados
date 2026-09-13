import logging
from datetime import datetime

import numpy as np
from pgvector.psycopg2 import register_vector

from src.banco.postgresql import conectar_postgresql
from src.embeddings.gerador import (
    calcular_hash_texto,
    calcular_idf,
    gerar_embedding_conteudo,
    identificar_modelo,
    preparar_texto,
    salvar_vocabulario
)


logger = logging.getLogger(__name__)


def conectar_vetorial(config):
    """Abre uma conexão com o PostgreSQL já preparada para o tipo vector."""

    conexao = conectar_postgresql(config)

    register_vector(conexao)

    return conexao


def obter_conteudos(conexao) -> list[dict]:
    """Retorna os conteúdos persistidos no PostgreSQL."""

    with conexao.cursor() as cursor:
        cursor.execute(
            """
            SELECT conteudo_id, titulo, descricao
            FROM conteudo
            ORDER BY conteudo_id
            """
        )

        registros = cursor.fetchall()

    return [
        {"conteudo_id": conteudo_id, "titulo": titulo, "descricao": descricao}
        for conteudo_id, titulo, descricao in registros
    ]


def obter_embeddings_existentes(conexao) -> dict[int, tuple[str, str]]:
    """Retorna modelo e hash do texto dos embeddings já armazenados."""

    with conexao.cursor() as cursor:
        cursor.execute(
            """
            SELECT conteudo_id, modelo, texto_hash
            FROM conteudo_embedding
            """
        )

        registros = cursor.fetchall()

    return {
        conteudo_id: (modelo, texto_hash)
        for conteudo_id, modelo, texto_hash in registros
    }


def salvar_embedding(
    conexao,
    conteudo_id: int,
    vetor: np.ndarray,
    modelo: str,
    texto_hash: str
) -> None:
    """Insere ou atualiza o embedding de um conteúdo."""

    with conexao.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO conteudo_embedding (
                conteudo_id,
                embedding,
                modelo,
                texto_hash,
                gerado_em
            )
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (conteudo_id) DO UPDATE SET
                embedding = EXCLUDED.embedding,
                modelo = EXCLUDED.modelo,
                texto_hash = EXCLUDED.texto_hash,
                gerado_em = EXCLUDED.gerado_em
            """,
            (conteudo_id, vetor, modelo, texto_hash, datetime.now())
        )


def remover_embedding(conexao, conteudo_id: int) -> None:
    """Remove o embedding de um conteúdo."""

    with conexao.cursor() as cursor:
        cursor.execute(
            "DELETE FROM conteudo_embedding WHERE conteudo_id = %s",
            (conteudo_id,)
        )


def sincronizar_embeddings(
    conexao,
    conteudos: list[dict],
    idf: dict[str, float],
    modelo: str,
    parametros: dict
) -> dict:
    """Gera, atualiza ou remove embeddings sem confirmar a transação.

    Conteúdos cujo modelo e texto não mudaram são reaproveitados. Quando a
    geração falha, o embedding anterior do conteúdo (se houver) é removido
    para não continuar sendo usado desatualizado.
    """

    existentes = obter_embeddings_existentes(conexao)

    contagem = {"gerados": 0, "reaproveitados": 0, "falhas": 0}

    for conteudo in conteudos:
        conteudo_id = conteudo["conteudo_id"]

        texto = preparar_texto(conteudo["titulo"], conteudo["descricao"])
        texto_hash = calcular_hash_texto(texto)

        if existentes.get(conteudo_id) == (modelo, texto_hash):
            contagem["reaproveitados"] += 1
            continue

        try:
            vetor = gerar_embedding_conteudo(
                conteudo["titulo"],
                conteudo["descricao"],
                parametros["dimensao"],
                parametros["peso_titulo"],
                idf
            )

            if not np.any(vetor):
                raise ValueError("texto sem termos do vocabulário")

        except Exception as erro:
            contagem["falhas"] += 1
            logger.error(
                "Falha na geração do embedding (conteudo_id=%s): %s",
                conteudo_id,
                erro
            )

            if conteudo_id in existentes:
                remover_embedding(conexao, conteudo_id)
                logger.warning(
                    "Embedding desatualizado removido (conteudo_id=%s).",
                    conteudo_id
                )

            continue

        salvar_embedding(conexao, conteudo_id, vetor, modelo, texto_hash)
        contagem["gerados"] += 1

    return contagem


def gerar_embeddings(config) -> dict:
    """Gera e armazena os embeddings dos conteúdos no pgvector.

    Somente conteúdos sem embedding, ou cujo texto ou modelo mudou, têm o
    vetor gerado novamente. Retorna as quantidades geradas, reaproveitadas
    e com falha.
    """

    parametros = config["embeddings"]

    conexao = conectar_vetorial(config)

    try:
        conteudos = obter_conteudos(conexao)

        idf = calcular_idf(conteudos)

        modelo = identificar_modelo(
            parametros["modelo"],
            parametros["dimensao"],
            idf
        )

        logger.info(
            "Modelo de embeddings: %s (vocabulário com %d termos)",
            modelo,
            len(idf)
        )

        contagem = sincronizar_embeddings(
            conexao,
            conteudos,
            idf,
            modelo,
            parametros
        )

        conexao.commit()

        # O vocabulário só é gravado após o commit, para que o arquivo usado
        # nas consultas corresponda sempre aos vetores armazenados.
        salvar_vocabulario(idf, parametros["vocabulario"])

        logger.info(
            "Embeddings: gerados=%d, reaproveitados=%d, falhas=%d",
            contagem["gerados"],
            contagem["reaproveitados"],
            contagem["falhas"]
        )

        return contagem

    except Exception:
        conexao.rollback()
        logger.exception("Falha na persistência dos embeddings no PostgreSQL.")
        raise

    finally:
        conexao.close()
        logger.info("Conexão com PostgreSQL (vetorial) encerrada.")


def obter_modelos_armazenados(conexao) -> list[str]:
    """Retorna os identificadores de modelo presentes nos embeddings."""

    with conexao.cursor() as cursor:
        cursor.execute("SELECT DISTINCT modelo FROM conteudo_embedding")

        return [modelo for (modelo,) in cursor.fetchall()]


def buscar_similares(
    conexao,
    vetor: np.ndarray,
    quantidade: int
) -> list[dict]:
    """Retorna os conteúdos mais próximos do vetor pela distância cosseno."""

    with conexao.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                co.conteudo_id,
                co.titulo,
                ca.nome AS categoria,
                co.tipo,
                ce.embedding <=> %s AS distancia
            FROM conteudo_embedding ce
            JOIN conteudo co
                ON co.conteudo_id = ce.conteudo_id
            JOIN categoria ca
                ON ca.categoria_id = co.categoria_id
            ORDER BY distancia ASC, co.conteudo_id ASC
            LIMIT %s
            """,
            (vetor, quantidade)
        )

        registros = cursor.fetchall()

    return [
        {
            "posicao": posicao,
            "conteudo_id": conteudo_id,
            "titulo": titulo,
            "categoria": categoria,
            "tipo": tipo,
            "distancia": float(distancia),
            "similaridade": 1 - float(distancia)
        }
        for posicao, (conteudo_id, titulo, categoria, tipo, distancia)
        in enumerate(registros, start=1)
    ]
