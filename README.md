# Desafio Prático 1 — Pipeline de Recomendação e Dashboard de Conteúdos Educacionais

## Participantes

- João Flavio
- Fabricio Mauro
- Eduardo Borges

## 1. Sobre o projeto

Este projeto implementa um pipeline de dados para uma plataforma fictícia de conteúdos educacionais.

O objetivo é construir um fluxo reproduzível desde a ingestão dos dados de origem até o armazenamento, processamento, recomendação de conteúdos e apresentação dos resultados em dashboard.

O desafio prevê a integração de:

- arquivos CSV e JSON;
- ingestão, validação e tratamento;
- PostgreSQL;
- MongoDB;
- armazenamento vetorial com pgvector;
- busca por similaridade semântica;
- sistema de recomendação;
- métricas e KPIs;
- Apache Superset.

A divisão inicial de responsabilidades adotada pela equipe segue a orientação do desafio:

- Estudante 01: ingestão, tratamento e PostgreSQL;
- Estudante 02: MongoDB, embeddings e recomendações;
- Estudante 03: métricas, consultas e dashboard.

---

## 2. Estrutura do projeto

```text
desafio_dados/
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── config/
│   │   ├── __init__.py
│   │   ├── configuracao.py
│   │   └── logging_config.py
│   ├── ingestao/
│   │   ├── __init__.py
│   │   ├── leitores.py
│   │   ├── validadores.py
│   │   ├── tratamentos.py
│   │   └── resumo.py
│   ├── banco/
│   │   ├── __init__.py
│   │   ├── postgresql.py
│   │   ├── mongodb.py
│   │   └── vetorial.py
│   ├── embeddings/
│   │   ├── __init__.py
│   │   └── gerador.py
│   └── recomendacao/
│       ├── __init__.py
│       ├── busca.py
│       └── motor.py
├── dados/
│   ├── brutos/
│   │   ├── catalogo.csv
│   │   ├── interacoes.json
│   │   └── comentarios.json
│   └── processados/
│       └── vocabulario_embeddings.json
├── sql/
│   ├── criar_banco.sql
│   ├── migracao_estudante2.sql
│   └── consultas.sql
├── mongodb/
│   └── consultas.js
├── logs/
├── tests/
│   ├── test_validadores.py
│   ├── test_tratamentos.py
│   ├── test_resumo.py
│   ├── test_postgresql.py
│   ├── test_mongodb.py
│   ├── test_embeddings.py
│   ├── test_vetorial.py
│   ├── test_recomendacao.py
│   └── test_main.py
├── config.yaml
├── .env
├── .env.example
├── .gitignore
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## 3. Fontes de dados

São utilizadas três fontes de dados fictícios.

### Catálogo — `dados/brutos/catalogo.csv`

Campos:

```text
conteudo_id
titulo
tipo
categoria
nivel
carga_horaria_min
data_publicacao
descricao
autor
```

### Interações — `dados/brutos/interacoes.json`

Campos:

```text
usuario_id
conteudo_id
tipo_interacao
data_hora
tempo_consumido
percentual_conclusao
avaliacao_atribuida
```

### Comentários e avaliações — `dados/brutos/comentarios.json`

Campos:

```text
usuario_id
conteudo_id
avaliacao
comentario
tags
data
```

Os arquivos originais permanecem em `dados/brutos/`. Os dados tratados são gravados em `dados/processados/`.

---

## 4. Scripts Python e responsabilidades

### `src/main.py`

É o ponto de entrada da aplicação e executa o pipeline completo da etapa atual:

```text
configuração
    ↓
leitura
    ↓
validação
    ↓
tratamento
    ↓
remoção de duplicidades
    ↓
salvamento dos processados
    ↓
carga PostgreSQL
    ↓
carga MongoDB + consultas de demonstração
    ↓
geração de embeddings (pgvector)
    ↓
busca semântica (consultas de demonstração)
    ↓
geração e persistência das recomendações
    ↓
geração do resumo
    ↓
finalização
```

Execução:

```bash
python -m src.main
```

Opções adicionais:

```bash
# somente a busca semântica (usa busca.top_k do config.yaml quando --top-k é omitido)
python -m src.main --consulta "Quero aprender os fundamentos de banco de dados para inteligência artificial." --top-k 5

# somente exibir as recomendações de um usuário na execução mais recente do pipeline
python -m src.main --usuario 3
```

Os argumentos são validados: `--consulta` não pode ser vazia, `--top-k` só é aceito junto com `--consulta` e deve ser positivo, e `--consulta` e `--usuario` não podem ser usados ao mesmo tempo. Argumentos inválidos encerram com erro, sem executar o pipeline.

Cada etapa é registrada no log com início, término e duração.

### `src/config/configuracao.py`

Carrega as configurações do `config.yaml`, incluindo caminhos dos arquivos e regras de validação.

### `src/config/logging_config.py`

Configura os logs em `logs/processamento.log`.

### `src/ingestao/leitores.py`

Responsável pela leitura dos arquivos CSV/JSON e pela gravação dos arquivos processados.

Principais funções:

```text
ler_catalogo()
ler_interacoes()
ler_comentarios()
ler_fontes()
salvar_catalogo()
salvar_json()
```

### `src/ingestao/validadores.py`

Centraliza as regras de validação, classificação e duplicidade dos registros.

Principais funções:

```text
validar_campos_obrigatorios()
validar_identificador()
validar_data()
validar_tipo()
validar_nivel()
validar_numero_nao_negativo()
validar_catalogo()
validar_avaliacao()
validar_percentual()
validar_data_hora()
validar_tipo_interacao()
validar_interacao()
validar_comentario()
gerar_chave_duplicidade()
identificar_duplicidades()
validar_registros()
```

### `src/ingestao/tratamentos.py`

Realiza limpeza, padronização, conversão de tipos e remoção de duplicidades.

Principais funções:

```text
limpar_espacos()
padronizar_catalogo()
padronizar_interacao()
padronizar_comentario()
tratar_registros()
remover_duplicados()
```

### `src/ingestao/resumo.py`

Gera e salva o resumo do processamento em `dados/processados/resumo.json`.

### `src/banco/postgresql.py`

Responsável pela conexão e persistência no PostgreSQL.

Principais funções:

```text
conectar_postgresql()
inserir_categorias()
obter_categorias()
inserir_conteudos()
inserir_usuarios()
inserir_interacoes()
carregar_postgresql()
```

A carga é realizada dentro de uma transação. Em caso de erro, é executado `ROLLBACK`; em caso de sucesso, `COMMIT`.

### `src/banco/mongodb.py`

Conexão e persistência dos comentários no MongoDB (RF07).

```text
conectar_mongodb()
criar_indices()
preparar_documentos_comentarios()
carregar_mongodb()
inserir_documento()
consultar_comentarios_por_conteudo()
buscar_por_tag()
filtrar_por_nota()
agregar_por_categoria()
obter_avaliacoes_positivas()
demonstrar_consultas()
```

### `src/embeddings/gerador.py`

Preparação dos textos e simulação dos embeddings (RF08).

```text
preparar_texto()
calcular_hash_texto()
calcular_idf()
identificar_modelo()
gerar_embedding()
gerar_embedding_conteudo()
salvar_vocabulario() / carregar_vocabulario()
```

### `src/banco/vetorial.py`

Armazenamento dos vetores no PostgreSQL com pgvector e busca por distância cosseno.

```text
conectar_vetorial()
gerar_embeddings()
sincronizar_embeddings()
salvar_embedding()
remover_embedding()
obter_embeddings_existentes()
buscar_similares()
```

### `src/recomendacao/busca.py`

Busca semântica por consulta em linguagem natural (RF09).

```text
buscar_conteudos()
exibir_resultados()
```

### `src/recomendacao/motor.py`

Cálculo dos índices, pontuação, classificação e persistência das recomendações (RF10 e RF11).

```text
calcular_candidatos()
calcular_pontuacao()
classificar_status()
normalizar_indices()
selecionar_recomendacoes()
gerar_recomendacoes()
consultar_recomendacoes_usuario()
obter_recomendacoes_usuario()
```

---

## 5. Ordem de execução para reprodução do projeto

Esta seção deve ser seguida pelo próximo integrante para reproduzir exatamente a etapa implementada até o momento.

### Passo 1 — Instalar as dependências

Na raiz do projeto:

```bash
pip install -r requirements.txt
```

Dependências atuais:

```text
PyYAML
psycopg2-binary
python-dotenv
pytest
pymongo
pgvector
numpy
```

`pytest` é utilizado nos testes automatizados. `pymongo` acessa o MongoDB, `pgvector` adapta o tipo `vector` para o `psycopg2` e `numpy` é usado na geração dos vetores.

Nenhum modelo de linguagem é baixado: os embeddings são simulados (ver seção 22).

### Passo 2 — Configurar as variáveis de ambiente

Criar o arquivo `.env` a partir do `.env.example`.

Configuração utilizada atualmente:

```env
POSTGRES_DB=desafio_dados
POSTGRES_USER=postgres
POSTGRES_PASSWORD=coloque_sua_senha
POSTGRES_PORT=5433
MONGO_PORT=27018
MONGO_USER=
MONGO_PASSWORD=
```

`MONGO_USER` e `MONGO_PASSWORD` são opcionais; o container do projeto não exige autenticação.

A senha não deve ser colocada no código nem no `config.yaml`.

O `.env` está incluído no `.gitignore` e não deve ser versionado.

### Passo 3 — Subir os bancos com Docker

```bash
docker compose up -d
```

Verificar:

```bash
docker ps
```

Devem estar disponíveis os containers:

```text
desafio_dados_postgres
desafio_dados_mongo
```

O PostgreSQL utiliza a porta `5433` no host e o MongoDB utiliza a porta `27018`.

As portas diferentes das padrão (`5432` e `27017`) evitam conflito com instalações locais de PostgreSQL ou MongoDB. Durante o desenvolvimento, um MongoDB instalado como serviço do Windows em `127.0.0.1:27017` recebia as conexões no lugar do container, por isso a porta do host passou a ser `27018`.

A imagem do PostgreSQL é `pgvector/pgvector:pg16`, que é o PostgreSQL 16 com a extensão pgvector. Quem já tinha o volume criado com `postgres:16` pode apenas executar `docker compose up -d` novamente: a versão principal é a mesma e os dados são preservados.

### Passo 4 — Criar as tabelas do PostgreSQL

Banco novo:

```bash
type sql\criar_banco.sql | docker exec -i desafio_dados_postgres psql -U postgres -d desafio_dados
```

Banco já criado na etapa do Estudante 01 (habilita o pgvector, cria `conteudo_embedding` e recria `recomendacao` somente se ela ainda estiver no esquema antigo, que não tinha registros; executar a migração de novo preserva o histórico):

```bash
type sql\migracao_estudante2.sql | docker exec -i desafio_dados_postgres psql -U postgres -d desafio_dados
```

Os comandos acima foram utilizados no ambiente Windows (no Git Bash/Linux, usar `docker exec -i ... < sql/arquivo.sql`).

O script cria a extensão `vector` e as tabelas:

```text
usuario
categoria
conteudo
interacao
conteudo_embedding
recomendacao
```

Também cria as chaves primárias, chaves estrangeiras, restrições de unicidade, restrições de domínio (`CHECK`) e integridade referencial.

### Passo 5 — Executar os testes antes do pipeline

Os containers precisam estar em execução, pois parte dos testes acessa o PostgreSQL e o MongoDB. Em um banco recém-criado, execute o pipeline (Passo 6) uma vez antes dos testes, porque `test_postgresql.py` usa registros já carregados (por exemplo `conteudo_id = 1`).

```bash
python -m pytest -v
```

Resultado validado na etapa atual:

```text
115 passed
```

Os testes verificam os validadores, tratamentos, resumo, operações do PostgreSQL, MongoDB, embeddings, busca vetorial e recomendação. Os testes de banco usam transação com `ROLLBACK` (PostgreSQL) e um banco temporário `desafio_dados_teste` removido ao final (MongoDB).

### Passo 6 — Executar o pipeline

```bash
python -m src.main
```

O pipeline lê os três arquivos, valida, trata, remove duplicidades, grava os arquivos processados, carrega catálogo e interações no PostgreSQL, carrega os comentários no MongoDB, gera os embeddings no pgvector, executa três buscas semânticas de demonstração e gera as recomendações.

### Passo 7 — Conferir os arquivos processados

Após a execução, verificar:

```text
dados/processados/
```

Arquivos esperados:

```text
catalogo.csv
interacoes.json
comentarios.json
resumo.json
vocabulario_embeddings.json
```

### Passo 8 — Conferir os logs

Verificar:

```text
logs/processamento.log
```

### Passo 9 — Executar as consultas de validação

O arquivo:

```text
sql/consultas.sql
```

contém consultas para verificar quantidades, distribuição dos dados, integridade referencial, embeddings, busca vetorial e recomendações.

Para acessar o PostgreSQL pelo container:

```bash
docker exec -it desafio_dados_postgres psql -U postgres -d desafio_dados
```

Depois, as consultas de `sql/consultas.sql` podem ser executadas no PostgreSQL/pgAdmin.

### Passo 10 — Executar as consultas do MongoDB

```bash
docker cp mongodb/consultas.js desafio_dados_mongo:/tmp/consultas.js
docker exec desafio_dados_mongo mongosh --quiet "mongodb://localhost:27017/desafio_dados" /tmp/consultas.js
```

O script precisa ser passado como arquivo; com redirecionamento (`<`) o `mongosh` entra no modo interativo e quebra os comandos escritos em várias linhas.

### Passo 11 — Executar buscas semânticas avulsas

```bash
python -m src.main --consulta "Como proteger APIs contra vazamentos de dados?" --top-k 5
```

---

## 6. Decisões técnicas — validação

Os registros podem ser classificados como:

```text
valido
invalido
incompleto
duplicado
```

Um registro incompleto é aquele que possui campo obrigatório ausente ou vazio.

Identificadores (`usuario_id` e `conteudo_id`) devem ser inteiros positivos.

Datas do catálogo e comentários devem estar no formato `YYYY-MM-DD`. `data_hora` das interações é validada como data e hora válida.

Os campos categóricos são comparados com os valores permitidos configurados no `config.yaml`.

Campos numéricos são validados para garantir que sejam numéricos e, quando aplicável, não negativos.

Percentuais são verificados dentro do intervalo configurado.

Avaliações são verificadas dentro do intervalo configurado. `avaliacao_atribuida` das interações pode ser nula quando permitido pela configuração.

O valor nulo de uma avaliação não é convertido para zero, pois zero representaria uma informação diferente da ausência de avaliação.

O campo `tags` dos comentários deve possuir estrutura de lista.

Os motivos das classificações inválidas ou incompletas são armazenados junto ao resultado da validação.

---

## 7. Regras de duplicidade

As regras de duplicidade foram definidas de forma diferente para cada fonte.

### Catálogo

```text
conteudo_id
```

O `conteudo_id` identifica unicamente um conteúdo.

### Interações

```text
usuario_id + conteudo_id + tipo_interacao + data_hora
```

A combinação completa identifica uma interação.

Repetições somente de `usuario_id + conteudo_id` não são consideradas duplicidades, pois um usuário pode possuir diferentes interações com o mesmo conteúdo.

### Comentários

```text
usuario_id + conteudo_id + data + comentario
```

Repetições somente de `usuario_id + conteudo_id` não são consideradas duplicidades, pois o mesmo usuário pode realizar comentários distintos sobre o mesmo conteúdo.

---

## 8. Decisões técnicas — tratamento dos dados

Os arquivos brutos são preservados e nunca sobrescritos pelo pipeline.

### Catálogo

São aplicados:

- remoção de espaços no início e no final dos valores textuais;
- padronização de `tipo` e `nivel`;
- conversão de `conteudo_id` para inteiro;
- conversão de `carga_horaria_min` para número;
- remoção de duplicidades conforme `conteudo_id`.

As datas já estavam no formato esperado e não precisaram ser transformadas.

### Interações

São aplicados:

- remoção de espaços nas extremidades;
- padronização de `tipo_interacao` para letras minúsculas;
- conversão de IDs para inteiro;
- conversão de `tempo_consumido` para número;
- conversão de `percentual_conclusao` para número;
- conversão de `avaliacao_atribuida` para número quando preenchida;
- preservação dos valores nulos permitidos;
- remoção de duplicidades conforme a chave definida.

### Comentários

São aplicados:

- remoção de espaços nas extremidades;
- conversão de IDs para inteiro;
- conversão de `avaliacao` para número;
- preservação da estrutura de `tags`;
- remoção de duplicidades conforme a chave definida.

As datas já estavam no formato esperado.

Não são alterados conteúdos semânticos de títulos, descrições ou comentários.

Os espaços internos dos textos não são modificados; somente os espaços nas extremidades são removidos.

---

## 9. Resultado da validação atual

Na execução validada foram processados 1.000 registros de cada fonte.

```text
Catálogo:
1000 válidos
0 inválidos
0 incompletos
0 duplicados

Interações:
1000 válidos
0 inválidos
0 incompletos
0 duplicados

Comentários:
1000 válidos
0 inválidos
0 incompletos
0 duplicados
```

Registros corrigidos durante o tratamento:

```text
Catálogo: 1000
Interações: 0
Comentários: 0
```

A quantidade de registros corrigidos do catálogo ocorre principalmente pelas conversões de tipos realizadas durante a padronização.

---

## 10. PostgreSQL

O modelo relacional atual possui:

```text
usuario
categoria
conteudo
interacao
conteudo_embedding
recomendacao
```

Relações principais:

```text
categoria 1 ─── N conteudo
usuario   1 ─── N interacao
conteudo  1 ─── N interacao
conteudo  1 ─── 1 conteudo_embedding
usuario   1 ─── N recomendacao
conteudo  1 ─── N recomendacao
```

A tabela `interacao` utiliza chave primária composta por:

```text
usuario_id
conteudo_id
tipo_interacao
data_hora
```

A persistência utiliza transação e as restrições do banco garantem integridade referencial.

Resultado validado no banco:

```text
Categorias: 8
Conteúdos: 1000
Usuários: 150
Interações: 1000
Interações sem conteúdo: 0
Interações sem usuário: 0
```

Os comentários não são carregados no PostgreSQL: eles são armazenados no MongoDB (seção 23).

As tabelas `conteudo_embedding` e `recomendacao` são descritas nas seções 24 e 26.

---

## 11. Resumo do processamento

O arquivo `dados/processados/resumo.json` registra a classificação dos registros, correções, cargas em cada banco e tempo total do processamento.

A estrutura atual contém:

```text
catalogo
interacoes
comentarios
registros_carregados
    postgresql      → catalogo, interacoes
    mongodb         → comentarios
    pgvector        → gerados, reaproveitados, falhas
    recomendacoes   → data_geracao, total, por_status
registros_corrigidos
tempo_processamento_segundos
```

`registros_carregados` diferencia o que foi persistido em cada banco. Em `pgvector`, `reaproveitados` indica embeddings que já existiam com o mesmo texto e o mesmo modelo e por isso não foram gerados novamente.

---

## 12. Logs

Os logs são gravados em:

```text
logs/processamento.log
```

São registrados:

- início e fim do processamento;
- arquivos de entrada;
- quantidade de registros lidos;
- quantidade de registros rejeitados;
- quantidade de registros corrigidos;
- salvamento dos arquivos processados;
- início e fim da carga PostgreSQL;
- sucesso da conexão;
- falhas de conexão;
- categorias, conteúdos, usuários e interações processados;
- sucesso ou falha da transação;
- encerramento da conexão;
- tempo total de processamento;
- início, término e duração de cada etapa (`src.etapas`), inclusive a etapa em que ocorreu uma falha;
- carga no MongoDB (inseridos, atualizados, sem alteração) e comentários rejeitados por referenciar conteúdo inexistente;
- falhas de conexão com o MongoDB, com host e porta;
- modelo de embeddings, tamanho do vocabulário e contagem de embeddings gerados, reaproveitados e com falha;
- falhas na geração de embeddings, com o `conteudo_id`;
- falhas de persistência de embeddings e recomendações;
- consultas semânticas executadas e divergência entre o modelo da consulta e o dos vetores armazenados;
- totais de recomendações por status.

Cada linha do log inclui o módulo de origem (por exemplo `src.banco.mongodb`), o que ajuda a identificar onde ocorreu o problema.

---

## 13. Docker e persistência

Para iniciar os serviços:

```bash
docker compose up -d
```

Para parar os serviços preservando os volumes:

```bash
docker compose down
```

Durante o desenvolvimento, evitar:

```bash
docker compose down -v
```

pois `-v` remove os volumes persistentes dos bancos.

---

## 14. Arquivos SQL

### `sql/criar_banco.sql`

Cria a extensão `vector`, o modelo relacional e suas restrições.

### `sql/migracao_estudante2.sql`

Atualiza um banco criado na etapa do Estudante 01: habilita o pgvector, cria `conteudo_embedding` e recria `recomendacao` com os novos campos somente quando a tabela ainda está no esquema antigo (sem a coluna `posicao`). Pode ser executado mais de uma vez sem apagar recomendações.

### `sql/consultas.sql`

Contém consultas utilizadas para verificar:

- quantidade de registros por tabela;
- conteúdos por categoria;
- interações por tipo;
- conteúdos mais avaliados;
- interações sem conteúdo;
- interações sem usuário;
- embeddings armazenados por modelo e conteúdos sem embedding;
- conteúdos mais semelhantes a um conteúdo (pgvector);
- recomendações de um usuário na execução mais recente do pipeline;
- recomendações por execução e status;
- ausência de conteúdos concluídos entre as recomendações.

### `mongodb/consultas.js`

Contém as consultas do MongoDB: inserção, comentários por conteúdo, busca por tag, filtro por nota, agregação por categoria e tags mais frequentes.

---

## 15. Testes

Os testes estão organizados em:

```text
tests/test_validadores.py
tests/test_tratamentos.py
tests/test_resumo.py
tests/test_postgresql.py
tests/test_mongodb.py
tests/test_embeddings.py
tests/test_vetorial.py
tests/test_recomendacao.py
tests/test_main.py
```

Executar todos os testes com:

```bash
python -m pytest -v
```

Resultado validado na etapa atual:

```text
115 passed
```

- `test_embeddings.py`: normalização e tokenização, IDF, determinismo e norma dos vetores, similaridade maior entre textos relacionados, identificação do modelo.
- `test_recomendacao.py`: fórmula da pontuação, limites 70 e 40, `Iconc = 0`, normalização dos índices e seleção das recomendações.
- `test_mongodb.py`: carga idempotente, inserção, consulta por conteúdo, tag, nota, agregação por categoria e avaliações positivas.
- `test_vetorial.py`: gravação e atualização de embeddings, busca por similaridade e cálculo de `Ivis`, `Icur` e `Iconc` no PostgreSQL com vetores de valores conhecidos; remoção do embedding desatualizado quando a geração falha; vocabulário não gravado se a persistência falhar; recomendações do usuário restritas à execução mais recente.
- `test_main.py`: validação dos argumentos `--consulta`, `--top-k` e `--usuario` e rejeição de quantidade não positiva na busca.

---

## 16. Segurança e versionamento

O arquivo `.env` contém informações de acesso e não deve ser versionado.

O `.gitignore` atual contempla:

```text
.env
__pycache__/
*.pyc
.venv/
logs/
```

Não devem ser armazenadas no código, README ou repositório senhas ou outros segredos.

---

## 17. Estado atual do Estudante 01

A etapa do Estudante 01 possui implementações funcionais para:

- leitura das três fontes;
- validação dos registros;
- classificação de registros;
- identificação de duplicidades;
- tratamento e padronização;
- preservação dos dados brutos;
- geração dos dados processados;
- geração do resumo;
- PostgreSQL;
- consultas de validação;
- testes automatizados;
- logs da aplicação;
- execução reproduzível por `python -m src.main`.

---

## 18. Estado atual do Estudante 02 e próxima etapa — Estudante 03

A etapa do Estudante 02 partiu do estado do Estudante 01, sem alterar os arquivos brutos, e implementou:

- MongoDB para comentários e avaliações, com carga idempotente e as consultas exigidas (RF07);
- embeddings simulados armazenados no PostgreSQL com pgvector, sem geração duplicada (RF08);
- busca semântica com quantidade de resultados configurável (RF09);
- motor de recomendação com a fórmula do enunciado (RF10);
- persistência das recomendações no PostgreSQL (RF11);
- ampliação do resumo, dos logs e dos testes.

O Estudante 03 pode partir deste estado:

```text
1. Reproduzir o ambiente conforme a seção "Ordem de execução".
2. Executar os testes e confirmar 115 testes aprovados.
3. Executar `python -m src.main`.
4. Conferir as consultas de `sql/consultas.sql` e `mongodb/consultas.js`.
5. Criar as views de métricas e KPIs no PostgreSQL (RF12).
6. Construir o dashboard no Apache Superset (RF13).
```

Dados disponíveis para métricas: `usuario`, `conteudo`, `categoria`, `interacao` e `recomendacao`. A tabela `recomendacao` guarda o histórico de todas as execuções (`data_geracao`); para indicadores da situação atual, filtrar a execução mais recente, como na consulta 10 de `sql/consultas.sql`. Os campos `status`, `pontuacao`, `i_vis` e `i_cur` permitem, por exemplo, medir a distribuição das recomendações por status ou calcular a conversão de recomendações (conteúdos recomendados que depois receberam interação).

---

## 19. Arquitetura atual e evolução prevista

Etapa implementada:

```text
CSV / JSON
    ↓
Leitura → Validação → Tratamento → Dados processados
    ↓                                   ↓
PostgreSQL (estruturados)         MongoDB (comentários)
    ↓                                   ↓
pgvector (embeddings) ──→ Busca semântica
    ↓                                   ↓
Motor de recomendação ←─────────────────┘
    ↓
PostgreSQL (recomendacao)
```

Arquitetura final prevista pelo desafio:

```text
CSV / JSON
    ↓
Ingestão
    ↓
PostgreSQL
    ↓
MongoDB
    ↓
Embeddings / armazenamento vetorial
    ↓
Busca semântica
    ↓
Recomendação
    ↓
Métricas e KPIs
    ↓
Apache Superset
```

---

## 20. Limitações e pontos para evolução

- A validação de referências entre usuários e conteúdos é garantida na persistência do PostgreSQL por meio das chaves estrangeiras; a validação prévia independente dessas referências pode ser ampliada futuramente.
- A padronização atual de categorias e níveis utiliza os valores configurados. Caso novos valores sejam adicionados, as regras devem ser atualizadas.
- O método atual de padronização com `capitalize()` deve ser revisado caso sejam introduzidos valores categóricos com múltiplas palavras cuja capitalização tenha significado específico.
- O tratamento remove somente espaços nas extremidades dos textos e não altera espaços internos.
- As datas que já estão no formato esperado não são transformadas desnecessariamente.
- Os embeddings são simulados por feature hashing com IDF. A similaridade é lexical (palavras em comum), não semântica de fato: sinônimos sem termos em comum não se aproximam e consultas com termos fora do vocabulário do catálogo não retornam resultados. Ver seção 24.
- Consultas amplas, que misturam temas (por exemplo, "banco de dados para inteligência artificial"), retornam resultados mais dispersos do que consultas específicas.
- A normalização min-max dos índices é relativa a cada usuário: `Positivo` indica os conteúdos mais afins ao histórico daquele usuário, e não uma afinidade absoluta comparável entre usuários.
- Conteúdos visualizados ou iniciados, mas não concluídos, continuam elegíveis para recomendação, pois o enunciado exige remover apenas os concluídos.
- O perfil do usuário é recalculado a cada execução para todos os 150 usuários e 1000 conteúdos; em volumes maiores seria necessário processamento incremental e um índice vetorial (HNSW) no pgvector.
- A tabela `recomendacao` acumula uma geração por execução do pipeline; não há rotina de expurgo do histórico.

---

## 21. Checklist rápido para reprodução

```text
[ ] Clonar/obter o projeto
[ ] Criar o .env a partir do .env.example
[ ] Instalar requirements.txt
[ ] Executar docker compose up -d
[ ] Conferir docker ps (desafio_dados_postgres com pgvector e desafio_dados_mongo)
[ ] Executar sql/criar_banco.sql (ou sql/migracao_estudante2.sql em banco existente)
[ ] Executar python -m src.main
[ ] Executar python -m pytest -v
[ ] Confirmar 115 passed
[ ] Conferir dados/processados/
[ ] Conferir logs/processamento.log
[ ] Executar as consultas de sql/consultas.sql
[ ] Executar mongodb/consultas.js
[ ] Confirmar PostgreSQL com 1000 conteúdos, 150 usuários, 1000 interações e 1000 embeddings
[ ] Confirmar MongoDB com 1000 comentários
[ ] Executar python -m src.main novamente e confirmar 1000 embeddings reaproveitados
[ ] Confirmar recomendações geradas para os 150 usuários
```

Os testes do PostgreSQL usam registros existentes (por exemplo `conteudo_id = 1`), por isso o pipeline deve ser executado antes dos testes em um banco novo.

---

## 22. Estudante 02 — visão geral

| Requisito | Implementação |
|---|---|
| RF07 — MongoDB | `src/banco/mongodb.py`, `mongodb/consultas.js` |
| RF08 — Embeddings | `src/embeddings/gerador.py`, `src/banco/vetorial.py`, tabela `conteudo_embedding` |
| RF09 — Busca semântica | `src/recomendacao/busca.py`, `python -m src.main --consulta` |
| RF10 — Recomendações | `src/recomendacao/motor.py` |
| RF11 — Persistência das recomendações | tabela `recomendacao` |

Parâmetros no `config.yaml`:

```yaml
mongodb:        host, porta, banco, colecao_comentarios, timeout_ms
embeddings:     modelo, dimensao, peso_titulo, vocabulario
busca:          top_k, consultas_demo
recomendacao:   top_n, tipos_visualizacao, tipo_curtida, tipo_conclusao,
                nota_minima_curtida, limiar_positivo, limiar_negativo,
                normalizar_indices
```

`validar_configuracao()` exige essas seções e verifica dimensão, `top_k`, `top_n` e limiares.

---

## 23. MongoDB — comentários e avaliações

### Justificativa

Os comentários ficam no MongoDB porque:

- são texto livre, com tamanho variável;
- `tags` é uma lista de tamanho variável, que no modelo relacional exigiria uma tabela associativa;
- a estrutura pode evoluir (respostas, reações, anexos) sem alterar esquema;
- as consultas necessárias (por conteúdo, por tag, por nota, agregação por categoria) são atendidas por índices e pelo pipeline de agregação, sem JOIN transacional;
- não participam das restrições de integridade que justificam o PostgreSQL para usuários, conteúdos, interações e recomendações.

### Documento armazenado

```json
{
  "usuario_id": 137,
  "conteudo_id": 587,
  "avaliacao": 5.0,
  "comentario": "Conteúdo introdutório, claro e objetivo. Superou minhas expectativas!",
  "tags": ["anonimizacao", "lgpd", "essencial"],
  "data": "2026-03-02",
  "titulo": "Curso Completo de Controle de Acesso Baseado em Papéis (RBAC): Da Teoria à Prática",
  "tipo": "Curso",
  "categoria": "Segurança & Governança"
}
```

Decisões:

- Cada documento mantém `usuario_id` e `conteudo_id`.
- `titulo`, `tipo` e `categoria` são copiados do catálogo (desnormalização). A agregação por categoria (RF07) não precisa consultar o PostgreSQL.
- Comentários que referenciam conteúdo inexistente no catálogo são descartados e registrados no log.
- A carga usa `upsert` pela chave `usuario_id + conteudo_id + data + comentario`, a mesma regra de duplicidade da ingestão, com índice único. Executar o pipeline várias vezes mantém 1000 documentos.
- Índices: `uq_comentario` (único), `conteudo_id`, `tags`, `avaliacao`, `categoria`.
- Banco `desafio_dados`, coleção `comentarios`.

### Consultas

| Operação | Função Python | `mongodb/consultas.js` |
|---|---|---|
| Inserir documentos | `inserir_documento()`, `carregar_mongodb()` | seção 1 |
| Comentários de um conteúdo | `consultar_comentarios_por_conteudo()` | seção 2 |
| Documentos por tag | `buscar_por_tag()` | seção 3 |
| Avaliações por nota | `filtrar_por_nota()` | seção 4 |
| Quantidade por categoria | `agregar_por_categoria()` | seção 5 |

Resultado da agregação por categoria:

```text
Business Intelligence      155 comentários | nota média 4.18
Inteligência Artificial    140 comentários | nota média 4.01
Banco de Dados             130 comentários | nota média 4.3
Segurança & Governança     130 comentários | nota média 4.04
Ciência de Dados           126 comentários | nota média 4.33
Engenharia de Dados        117 comentários | nota média 4.17
DevOps & Cloud             105 comentários | nota média 3.88
Programação & Software      97 comentários | nota média 4.26
```

---

## 24. Embeddings simulados e pgvector

### Por que simulados

Seguindo a abordagem da Aula 05 ("Construindo um Pipeline de Dados de Recomendação Simples"), os embeddings são **simulados** por um script Python, sem modelo de linguagem. Na aula, o vetor é aleatório (`random.uniform`, 3 dimensões). Aqui foi necessário um ajuste: o RF09 exige transformar uma consulta em linguagem natural em vetor, e um vetor aleatório não representa o texto. A simulação é, portanto, **determinística e baseada nos termos do texto**. O mesmo texto sempre gera o mesmo vetor, e textos com termos em comum ficam próximos.

### Preparação do texto

1. Representação textual: `"<titulo>. <descricao>"`, com espaços repetidos removidos.
2. Normalização: minúsculas e remoção de acentos (`Inteligência` → `inteligencia`).
3. Tokenização: sequências alfanuméricas; descarte de palavras com menos de 3 letras e de stopwords em português (`para`, `com`, `sobre`, `quero`...).
4. Termos: palavras e pares de palavras consecutivas (bigramas), para capturar expressões como `banco_dados` e `machine_learning`.

### Geração do vetor

- **Peso do termo (IDF)**: `idf = ln((1 + N) / (1 + df))`, calculado sobre os 1000 conteúdos. As descrições do catálogo seguem modelos fixos ("Neste curso aprofundado, você aprenderá..."); termos presentes em todos os conteúdos, como `nivel`, recebem peso zero. Sem o IDF, essas frases dominavam a similaridade e as buscas retornavam conteúdos com o mesmo formato, e não com o mesmo tema.
- **Feature hashing**: o SHA-256 de cada termo define uma posição (mod 384) e um sinal (+/−) no vetor, e soma `peso_do_campo × idf`.
- **Peso do título**: 2 (`peso_titulo`); a descrição tem peso 1.
- **Normalização L2**: o vetor tem norma 1.
- **Dimensão**: 384, a mesma de modelos reais como `all-MiniLM-L6-v2`, o que facilita trocar por um modelo real sem mudar o esquema.
- Termos da consulta que não existem no vocabulário do catálogo são ignorados.

O vocabulário (IDF) é salvo em `dados/processados/vocabulario_embeddings.json` e reutilizado para vetorizar as consultas.

### Modelo registrado

O campo `modelo` de `conteudo_embedding` registra o identificador completo:

```text
simulado-hashing-idf-v1:384d:vocab-d803f63d9f2a
```

`vocab-...` é uma assinatura do vocabulário. Se o catálogo mudar, o vocabulário muda, o identificador muda e todos os vetores são gerados novamente.

### Tabela `conteudo_embedding`

```text
conteudo_id  INTEGER PK / FK → conteudo
embedding    VECTOR(384)
modelo       VARCHAR(100)
texto_hash   CHAR(64)     -- SHA-256 do texto preparado
gerado_em    TIMESTAMP
```

### Sem geração duplicada

Antes de gerar, o pipeline compara `(modelo, texto_hash)` de cada conteúdo com o que já está armazenado:

- igual → reaproveitado;
- ausente ou diferente → gerado e gravado com `INSERT ... ON CONFLICT DO UPDATE`.

A chave primária `conteudo_id` garante no máximo um vetor por conteúdo. Resultado validado:

```text
1ª execução: 1000 gerados, 0 reaproveitados, 0 falhas
2ª execução: 0 gerados, 1000 reaproveitados, 0 falhas
```

Somente conteúdos persistidos no PostgreSQL recebem embedding. Um vetor nulo (texto sem termos do vocabulário) é registrado como falha no log.

---

## 25. Busca por similaridade semântica

A consulta é vetorizada com o mesmo vocabulário e comparada pela distância cosseno do pgvector (`<=>`):

```sql
SELECT co.conteudo_id, co.titulo, ca.nome AS categoria, co.tipo,
       ce.embedding <=> %s AS distancia
FROM conteudo_embedding ce
JOIN conteudo co ON co.conteudo_id = ce.conteudo_id
JOIN categoria ca ON ca.categoria_id = co.categoria_id
ORDER BY distancia ASC, co.conteudo_id ASC
LIMIT %s;
```

A saída mostra posição, identificador, similaridade (`1 - distância`), tipo, categoria e título. A quantidade de resultados vem de `busca.top_k` ou de `--top-k`.

Resultados das três consultas de demonstração (`busca.consultas_demo`):

```text
Consulta: Quero aprender os fundamentos de banco de dados para inteligência artificial.
  Pos |   ID | Similaridade | Tipo     | Categoria                | Título
    1 |  160 |       0.2647 | Curso    | Inteligência Artificial  | Construindo Aplicações Robustas com Fundamentos de Deep Learning com PyTorch
    2 |  685 |       0.2254 | Artigo   | Banco de Dados           | Estudo Técnico e Decisões de Arquitetura em Armazenamento de Documentos com MongoDB
    3 |  366 |       0.2202 | Curso    | Engenharia de Dados      | Construindo Aplicações Robustas com Pipelines de Ingestão Batch e Streaming
    4 |  359 |       0.2158 | Curso    | Inteligência Artificial  | Masterclass de Engenharia de Prompts e Agentes Inteligentes para Projetos Reais
    5 |  170 |       0.2104 | Curso    | DevOps & Cloud           | Construindo Aplicações Robustas com Gerenciamento de Ambientes e Segredos em Nuvem

Consulta: Como proteger APIs contra vazamentos de dados?
    1 |   11 |       0.6319 | Vídeo    | Segurança & Governança   | Análise Prática e Demonstração de Prevenção contra Vazamentos e Segurança em APIs
    2 |  525 |       0.5881 | Vídeo    | Segurança & Governança   | Guia Rápido e Hands-on: Prevenção contra Vazamentos e Segurança em APIs
    3 |  286 |       0.5874 | Vídeo    | Segurança & Governança   | Guia Rápido e Hands-on: Prevenção contra Vazamentos e Segurança em APIs
    4 |  276 |       0.5871 | Podcast  | Segurança & Governança   | Data Insights Ep. 82: Experiências Reais com Prevenção contra Vazamentos e Segurança em APIs
    5 |  885 |       0.5804 | Artigo   | Segurança & Governança   | Estudo Técnico e Decisões de Arquitetura em Prevenção contra Vazamentos e Segurança em APIs

Consulta: Podcast sobre machine learning supervisionado
    1 |  740 |       0.6460 | Vídeo    | Ciência de Dados         | Melhores Práticas e Arquitetura de Machine Learning Supervisionado com Scikit-Learn
    2 |  732 |       0.6393 | Podcast  | Ciência de Dados         | Deep Dive Ep. 97: Casos de Sucesso em Machine Learning Supervisionado com Scikit-Learn
    3 |  427 |       0.6303 | Artigo   | Ciência de Dados         | Como Obter Alta Performance Utilizando Machine Learning Supervisionado com Scikit-Learn
    4 |  910 |       0.6293 | Artigo   | Ciência de Dados         | Como Obter Alta Performance Utilizando Machine Learning Supervisionado com Scikit-Learn
    5 |  798 |       0.6293 | Artigo   | Ciência de Dados         | Como Obter Alta Performance Utilizando Machine Learning Supervisionado com Scikit-Learn
```

As consultas específicas trazem conteúdos do tema certo com similaridade próxima de 0.6. A consulta ampla do enunciado mistura dois temas e retorna resultados mais dispersos (limitação da simulação lexical). Na última consulta, a palavra "podcast" tem pouco peso porque o tipo do conteúdo não faz parte do título nem da descrição.

---

## 26. Motor de recomendação

### Fórmula

```text
Pontuação = ((Ivis + Icur) / 2) * 100 * Iconc
```

Para cada usuário, todos os conteúdos com embedding são avaliados. Os índices são calculados em SQL com pgvector (`AVG(embedding)` e `<=>`):

| Índice | Cálculo |
|---|---|
| **Ivis** | Perfil de visualização = `AVG(embedding)` dos conteúdos com interação `visualização`, `início` ou `conclusão` (interações repetidas pesam mais, refletindo a frequência). `Ivis = 1 - (embedding <=> perfil)`. |
| **Icur** | Perfil de aprovação = `AVG(embedding)` dos conteúdos com `curtida`, com `avaliacao_atribuida >= 4` nas interações **ou** com comentário de `avaliacao >= 4` no MongoDB. `Icur = 1 - (embedding <=> perfil)`. |
| **Iconc** | `0` se o usuário tem interação `conclusão` ou `percentual_conclusao >= 100` com o conteúdo; senão `1`. |

Sem histórico de visualização ou de aprovação, o índice correspondente é 0. Os índices são limitados a [0, 1].

### Normalização dos índices (`normalizar_indices: true`)

Com vetores simulados, a similaridade cosseno bruta é baixa (a média entre conteúdos é cerca de 0.03). Sem normalização, a primeira execução gerou 0 recomendações `Positivo`, apenas 301 `Estável` e 73 usuários sem nenhuma recomendação. Por isso `Ivis` e `Icur` passam por min-max entre os candidatos de cada usuário: o conteúdo mais afim recebe 1.0 e o menos afim 0.0, e os valores continuam entre 0.0 e 1.0, como o enunciado exige.

| Configuração | Positivo | Estável | Usuários sem recomendação |
|---|---|---|---|
| `normalizar_indices: false` | 0 | 301 | 73 |
| `normalizar_indices: true` | 435 | 1063 | 0 |

### Classificação

| Status | Regra |
|---|---|
| Positivo | pontuação >= 70 |
| Estável | 40 < pontuação < 70 |
| Negativo | pontuação <= 40 ou `Iconc = 0` |

O enunciado escreve a faixa estável como "40 > Pontuação < 70"; ela foi interpretada como `40 < Pontuação < 70`, que é a única leitura compatível com as outras duas faixas.

### Seleção e persistência

- Recomendações `Negativo` são descartadas (não entram na lista de sugestões).
- As demais são ordenadas pela pontuação (empate pelo `conteudo_id`) e as `top_n` (10) primeiras recebem `posicao` de 1 a N.
- Todas as recomendações de uma execução compartilham o mesmo `data_geracao` e são gravadas em uma única transação.

Tabela `recomendacao`:

```text
recomendacao_id  SERIAL PK
usuario_id       FK → usuario
conteudo_id      FK → conteudo
pontuacao        NUMERIC(5,2)  CHECK 0–100
posicao          INTEGER       CHECK > 0
i_vis, i_cur     NUMERIC(6,4)
i_conc           SMALLINT      CHECK IN (0, 1)
status           VARCHAR(10)   CHECK IN ('Positivo', 'Estável', 'Negativo')
data_geracao     TIMESTAMP
UNIQUE (usuario_id, conteudo_id, data_geracao)
```

### Resultado validado

```text
1498 recomendações para 150 usuários (Positivo: 435, Estável: 1063, usuários sem recomendação: 0)
Recomendações de conteúdos já concluídos: 0
Posições inconsistentes (fora de 1..N): 0
```

Exemplo (`python -m src.main --usuario 3`):

```text
  Pos |   ID | Pontuação | Status   | Conteúdo
    1 |  396 |     80.08 | Positivo | Análise Prática e Demonstração de Storytelling com Dados para Apresentações Executivas
    2 |  289 |     77.13 | Positivo | Data Insights Ep. 58: Experiências Reais com Storytelling com Dados para Apresentações Executivas
    3 |  605 |     74.85 | Positivo | Data Insights Ep. 78: Experiências Reais com Storytelling com Dados para Apresentações Executivas
    4 |  229 |     74.08 | Positivo | Arquitetura & Código Ep. 79: Inovações em Storytelling com Dados para Apresentações Executivas
    5 |  241 |     67.64 | Estável  | Melhores Práticas e Arquitetura de Storytelling com Dados para Apresentações Executivas
  ...
```

---

## 27. Uso de IA — Estudante 02

### Ferramenta utilizada

- **Claude Code** (Anthropic), modelo Claude Opus 5, executado no terminal com acesso ao repositório, ao Docker e aos bancos locais.

### Exemplos de solicitações realizadas

- "Leia todo o PDF, entenda o que precisa ser feito, avalie o estado atual do projeto e planeje os próximos passos. Nossa responsabilidade está detalhada no PDF como Estudante 2."
- Escolha do modelo de embeddings: a equipe indicou criar "um script Python que fará a ingestão dos dados e simulará a geração de embeddings", tendo como referência o PDF da Aula 05 ("Construindo um Pipeline de Dados de Recomendação Simples").
- Implementação do plano aprovado: MongoDB, embeddings no pgvector, busca semântica, motor de recomendação, testes e documentação.

### Trechos ou decisões apoiados pela IA

- Levantamento das lacunas do projeto para esta etapa: imagem `postgres:16` sem pgvector, tabela `recomendacao` sem posição e data de geração, comentários sem categoria para a agregação do RF07.
- Simulação dos embeddings por *feature hashing* com IDF (`src/embeddings/gerador.py`), em vez do vetor aleatório da Aula 05, para que consultas em linguagem natural possam ser vetorizadas (RF09).
- Controle de geração duplicada por `modelo` + `texto_hash` (`src/banco/vetorial.py`).
- Consultas SQL do motor de recomendação com `AVG(embedding)` e o operador `<=>` do pgvector (`src/recomendacao/motor.py`).
- Carga idempotente no MongoDB com `upsert` e índice único; pipeline de agregação por categoria (`src/banco/mongodb.py`, `mongodb/consultas.js`).
- Estrutura dos testes automatizados (`tests/test_embeddings.py`, `tests/test_recomendacao.py`, `tests/test_mongodb.py`, `tests/test_vetorial.py`, `tests/test_main.py`).
- Redação das seções 22 a 27 deste README.

### Erros ou inadequações encontrados nas respostas

1. **Primeira versão da simulação sem IDF.** O protótipo inicial somava todos os termos com o mesmo peso. Como as descrições do catálogo seguem modelos fixos, termos como "nível", "especialistas" e "práticas" dominaram a similaridade, e a consulta sobre dashboards retornou um artigo sobre tipagem estática com Mypy. A ponderação IDF foi adicionada depois de medir a frequência dos termos no catálogo.
2. **Pontuações baixas demais sem normalização.** Com a similaridade cosseno bruta, a primeira execução gerou 0 recomendações `Positivo` e deixou 73 dos 150 usuários sem recomendação. O risco estava previsto no plano, e a normalização min-max por usuário foi ativada depois de comparar as duas distribuições.
3. **MongoDB errado recebendo os dados.** A primeira execução informou 1000 comentários carregados, mas a consulta feita dentro do container retornou 0. Um MongoDB instalado como serviço do Windows ouvia em `127.0.0.1:27017` e recebia as conexões no lugar do container. A porta do host do container passou a ser `27018`. A IA não apagou o banco `desafio_dados` criado nesse MongoDB local; a remoção ficou a critério do integrante.
4. **Script `consultas.js` executado por redirecionamento.** `mongosh < consultas.js` falhou, porque o modo interativo quebra comandos escritos em várias linhas. A instrução passou a ser executar o arquivo como script.
5. **Fuso horário inconsistente.** `gerado_em` usava o relógio do container (UTC) e `data_geracao` o horário local do Python. As duas datas passaram a ser geradas no Python.
6. **Teste com asserção sem efeito.** Uma primeira versão de `test_calcular_candidatos_aplica_indices_e_conclusao` tinha uma asserção com `or True`. Ela foi substituída por valores exatos, calculados à mão a partir dos vetores do teste.
7. **Problemas apontados na revisão de código (`/code-review`).** A revisão automática das alterações encontrou seis problemas, todos confirmados e corrigidos com testes: (a) `--usuario` mostrava a última execução em que o usuário tinha recomendações, e não a última execução do pipeline, podendo exibir conteúdos já concluídos; (b) o vocabulário era gravado antes do commit dos embeddings e ficava divergente se a transação falhasse; (c) quando a geração de um embedding falhava, o vetor antigo continuava armazenado e em uso; (d) a migração apagava a tabela `recomendacao` sem verificação, destruindo o histórico se fosse executada novamente; (e) `--consulta ""` e `--top-k` sozinho executavam o pipeline completo; (f) `--top-k 0` era trocado silenciosamente pelo padrão e `--top-k -1` causava erro no PostgreSQL.

### Alterações feitas pela equipe

- Definição de que os embeddings seriam simulados, seguindo a Aula 05, em vez de usar um modelo real ou uma API.
- Definição de que nenhum commit seria feito pela IA; o versionamento fica com o integrante.
- _A preencher pelo integrante após a revisão do código: ajustes realizados, trechos reescritos e decisões revistas._