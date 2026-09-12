-- 1. Quantidade de registros por tabela

SELECT COUNT(*) AS total_categorias
FROM categoria;

SELECT COUNT(*) AS total_conteudos
FROM conteudo;

SELECT COUNT(*) AS total_usuarios
FROM usuario;

SELECT COUNT(*) AS total_interacoes
FROM interacao;


-- 2. Conteúdos por categoria

SELECT
    c.nome AS categoria,
    COUNT(co.conteudo_id) AS total_conteudos
FROM categoria c
LEFT JOIN conteudo co
    ON co.categoria_id = c.categoria_id
GROUP BY c.nome
ORDER BY total_conteudos DESC;


-- 3. Interações por tipo

SELECT
    tipo_interacao,
    COUNT(*) AS total_interacoes
FROM interacao
GROUP BY tipo_interacao
ORDER BY total_interacoes DESC;


-- 4. Conteúdos mais avaliados

SELECT
    co.conteudo_id,
    co.titulo,
    AVG(i.avaliacao_atribuida) AS avaliacao_media
FROM conteudo co
JOIN interacao i
    ON i.conteudo_id = co.conteudo_id
WHERE i.avaliacao_atribuida IS NOT NULL
GROUP BY co.conteudo_id, co.titulo
ORDER BY avaliacao_media DESC;


-- 5. Verificar integridade das interações

SELECT COUNT(*) AS interacoes_sem_conteudo
FROM interacao i
LEFT JOIN conteudo c
    ON c.conteudo_id = i.conteudo_id
WHERE c.conteudo_id IS NULL;


-- 6. Verificar integridade dos usuários

SELECT COUNT(*) AS interacoes_sem_usuario
FROM interacao i
LEFT JOIN usuario u
    ON u.usuario_id = i.usuario_id
WHERE u.usuario_id IS NULL;