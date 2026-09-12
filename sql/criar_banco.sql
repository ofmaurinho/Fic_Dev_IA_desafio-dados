CREATE TABLE usuario (
    usuario_id INTEGER PRIMARY KEY
);

CREATE TABLE categoria (
    categoria_id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE conteudo (
    conteudo_id INTEGER PRIMARY KEY,
    titulo VARCHAR(255) NOT NULL,
    tipo VARCHAR(50) NOT NULL,
    categoria_id INTEGER NOT NULL,
    nivel VARCHAR(50) NOT NULL,
    carga_horaria_min NUMERIC NOT NULL,
    data_publicacao DATE NOT NULL,
    descricao TEXT NOT NULL,
    autor VARCHAR(255) NOT NULL,

    CONSTRAINT fk_conteudo_categoria
        FOREIGN KEY (categoria_id)
        REFERENCES categoria (categoria_id)
);

CREATE TABLE interacao (
    usuario_id INTEGER NOT NULL,
    conteudo_id INTEGER NOT NULL,
    tipo_interacao VARCHAR(50) NOT NULL,
    data_hora TIMESTAMP NOT NULL,
    tempo_consumido NUMERIC NOT NULL,
    percentual_conclusao NUMERIC NOT NULL,
    avaliacao_atribuida NUMERIC,

    PRIMARY KEY (
        usuario_id,
        conteudo_id,
        tipo_interacao,
        data_hora
    ),

    CONSTRAINT fk_interacao_usuario
        FOREIGN KEY (usuario_id)
        REFERENCES usuario (usuario_id),

    CONSTRAINT fk_interacao_conteudo
        FOREIGN KEY (conteudo_id)
        REFERENCES conteudo (conteudo_id)
);

CREATE TABLE recomendacao (
    recomendacao_id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL,
    conteudo_id INTEGER NOT NULL,
    score NUMERIC NOT NULL,

    CONSTRAINT fk_recomendacao_usuario
        FOREIGN KEY (usuario_id)
        REFERENCES usuario (usuario_id),

    CONSTRAINT fk_recomendacao_conteudo
        FOREIGN KEY (conteudo_id)
        REFERENCES conteudo (conteudo_id)
);