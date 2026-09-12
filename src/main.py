import logging
import time

from src.config.configuracao import carregar_configuracao
from src.config.logging_config import configurar_logging
from src.ingestao.leitores import (
    ler_fontes,
    salvar_catalogo,
    salvar_json
)
from src.ingestao.validadores import validar_registros
from src.ingestao.tratamentos import tratar_registros, remover_duplicados
from src.ingestao.resumo import gerar_resumo, salvar_resumo
from src.banco.postgresql import carregar_postgresql


def main() -> None:
    """Executa a leitura, validação, tratamento e carga dos dados."""

    configurar_logging()
    logger = logging.getLogger(__name__)

    inicio = time.time()

    print("Início do processamento.")
    logger.info("Início do processamento.")

    config = carregar_configuracao()

    logger.info(
        "Arquivos de entrada: %s, %s, %s",
        config["dados"]["catalogo"],
        config["dados"]["interacoes"],
        config["dados"]["comentarios"]
    )

    dados = ler_fontes(config)

    logger.info(
        "Registros lidos: catálogo=%d, interações=%d, comentários=%d",
        len(dados["catalogo"]),
        len(dados["interacoes"]),
        len(dados["comentarios"])
    )

    resultados_catalogo = validar_registros(
        dados["catalogo"],
        "catalogo",
        config["validacao"]["catalogo"]
    )

    resultados_interacoes = validar_registros(
        dados["interacoes"],
        "interacoes",
        config["validacao"]["interacoes"]
    )

    resultados_comentarios = validar_registros(
        dados["comentarios"],
        "comentarios",
        config["validacao"]["comentarios"]
    )

    logger.info(
        "Registros rejeitados: catálogo=%d, interações=%d, comentários=%d",
        sum(
            1 for resultado in resultados_catalogo
            if resultado["situacao"] != "valido"
        ),
        sum(
            1 for resultado in resultados_interacoes
            if resultado["situacao"] != "valido"
        ),
        sum(
            1 for resultado in resultados_comentarios
            if resultado["situacao"] != "valido"
        )
    )

    dados["catalogo"], corrigidos_catalogo = tratar_registros(
        dados["catalogo"], "catalogo"
    )

    dados["interacoes"], corrigidos_interacoes = tratar_registros(
        dados["interacoes"], "interacoes"
    )

    dados["comentarios"], corrigidos_comentarios = tratar_registros(
        dados["comentarios"], "comentarios"
    )

    logger.info(
        "Registros corrigidos: catálogo=%d, interações=%d, comentários=%d",
        corrigidos_catalogo,
        corrigidos_interacoes,
        corrigidos_comentarios
    )

    dados["catalogo"] = remover_duplicados(
        dados["catalogo"], "catalogo"
    )

    dados["interacoes"] = remover_duplicados(
        dados["interacoes"], "interacoes"
    )

    dados["comentarios"] = remover_duplicados(
        dados["comentarios"], "comentarios"
    )

    salvar_catalogo(
        dados["catalogo"],
        config["dados"]["processados"]["catalogo"]
    )

    salvar_json(
        dados["interacoes"],
        config["dados"]["processados"]["interacoes"]
    )

    salvar_json(
        dados["comentarios"],
        config["dados"]["processados"]["comentarios"]
    )

    logger.info("Arquivos processados salvos.")

    logger.info("Início da carga no PostgreSQL.")

    carregar_postgresql(
        config,
        dados["catalogo"],
        dados["interacoes"]
    )

    logger.info("Carga no PostgreSQL concluída.")

    tempo_processamento = time.time() - inicio

    resumo = gerar_resumo(
        resultados_catalogo,
        resultados_interacoes,
        resultados_comentarios,
        {
            "catalogo": len(dados["catalogo"]),
            "interacoes": len(dados["interacoes"]),
            "comentarios": len(dados["comentarios"])
        },
        {
            "catalogo": corrigidos_catalogo,
            "interacoes": corrigidos_interacoes,
            "comentarios": corrigidos_comentarios
        },
        tempo_processamento
    )

    salvar_resumo(
        resumo,
        config["dados"]["processados"]["resumo"]
    )

    logger.info(
        "Tempo total de processamento: %.4f segundos",
        tempo_processamento
    )

    logger.info("Fim do processamento.")

    print("Validação, tratamento e carga concluídos.")
    print(f"Catálogo: {len(dados['catalogo'])} registros")
    print(f"Interações: {len(dados['interacoes'])} registros")
    print(f"Comentários: {len(dados['comentarios'])} registros")
    print("Fim do processamento.")


if __name__ == "__main__":
    main()