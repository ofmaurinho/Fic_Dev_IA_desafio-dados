import logging

import numpy as np

from src.banco.vetorial import (
    buscar_similares,
    conectar_vetorial,
    obter_modelos_armazenados
)
from src.embeddings.gerador import (
    carregar_vocabulario,
    gerar_embedding,
    identificar_modelo
)


logger = logging.getLogger(__name__)


def buscar_conteudos(
    config,
    consulta: str,
    quantidade: int | None = None
) -> list[dict]:
    """Retorna os conteúdos semanticamente mais próximos da consulta."""

    parametros = config["embeddings"]

    if quantidade is None:
        quantidade = config["busca"]["top_k"]

    if quantidade <= 0:
        raise ValueError(
            f"Quantidade de resultados deve ser positiva: {quantidade}"
        )

    try:
        idf = carregar_vocabulario(parametros["vocabulario"])

    except FileNotFoundError:
        logger.error(
            "Vocabulário de embeddings não encontrado em %s. "
            "Execute o pipeline completo antes da busca.",
            parametros["vocabulario"]
        )
        raise

    modelo = identificar_modelo(
        parametros["modelo"],
        parametros["dimensao"],
        idf
    )

    vetor = gerar_embedding(consulta, parametros["dimensao"], idf)

    if not np.any(vetor):
        logger.warning(
            "Consulta sem termos conhecidos pelo vocabulário: %s",
            consulta
        )
        return []

    conexao = conectar_vetorial(config)

    try:
        modelos = obter_modelos_armazenados(conexao)

        if modelos != [modelo]:
            logger.warning(
                "Modelo da consulta (%s) difere dos embeddings armazenados "
                "(%s). Execute o pipeline para regenerá-los.",
                modelo,
                ", ".join(modelos) or "nenhum"
            )

        resultados = buscar_similares(conexao, vetor, quantidade)

    finally:
        conexao.close()

    logger.info(
        "Busca semântica executada: consulta='%s', resultados=%d",
        consulta,
        len(resultados)
    )

    return resultados


def exibir_resultados(consulta: str, resultados: list[dict]) -> None:
    """Exibe os resultados da busca semântica em formato de tabela."""

    print(f"\nConsulta: {consulta}")

    if not resultados:
        print("  Nenhum conteúdo encontrado.")
        return

    print(
        f"  {'Pos':>3} | {'ID':>4} | {'Similaridade':>12} | "
        f"{'Tipo':<8} | {'Categoria':<24} | Título"
    )

    for resultado in resultados:
        print(
            f"  {resultado['posicao']:>3} | "
            f"{resultado['conteudo_id']:>4} | "
            f"{resultado['similaridade']:>12.4f} | "
            f"{resultado['tipo']:<8} | "
            f"{resultado['categoria']:<24} | "
            f"{resultado['titulo']}"
        )
