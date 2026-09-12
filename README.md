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
│   └── banco/
│       ├── __init__.py
│       └── postgresql.py
├── dados/
│   ├── brutos/
│   │   ├── catalogo.csv
│   │   ├── interacoes.json
│   │   └── comentarios.json
│   └── processados/
├── sql/
│   ├── criar_banco.sql
│   └── consultas.sql
├── logs/
├── tests/
│   ├── test_validadores.py
│   ├── test_tratamentos.py
│   ├── test_resumo.py
│   └── test_postgresql.py
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
geração do resumo
    ↓
finalização
```

Execução:

```bash
python -m src.main
```

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
```

`pytest` é utilizado nos testes automatizados.

As dependências específicas de MongoDB, embeddings, busca vetorial e Superset serão adicionadas nas próximas etapas.

### Passo 2 — Configurar as variáveis de ambiente

Criar o arquivo `.env` a partir do `.env.example`.

Configuração utilizada atualmente:

```env
POSTGRES_DB=desafio_dados
POSTGRES_USER=postgres
POSTGRES_PASSWORD=coloque_sua_senha
POSTGRES_PORT=5433
MONGO_PORT=27017
```

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

O PostgreSQL utiliza a porta `5433` no host e o MongoDB utiliza a porta `27017`.

### Passo 4 — Criar as tabelas do PostgreSQL

Executar:

```bash
type sql\criar_banco.sql | docker exec -i desafio_dados_postgres psql -U postgres -d desafio_dados
```

O comando acima foi utilizado no ambiente Windows.

O script cria as tabelas:

```text
usuario
categoria
conteudo
interacao
recomendacao
```

Também cria as chaves primárias, chaves estrangeiras, restrições de unicidade e integridade referencial.

### Passo 5 — Executar os testes antes do pipeline

```bash
python -m pytest -v
```

Resultado validado na etapa atual:

```text
64 passed
```

Os testes verificam os validadores, tratamentos, resumo e operações principais do PostgreSQL.

### Passo 6 — Executar o pipeline

```bash
python -m src.main
```

O pipeline lê os três arquivos, valida, trata, remove duplicidades, grava os arquivos processados e carrega catálogo e interações no PostgreSQL.

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

contém consultas para verificar quantidades, distribuição dos dados e integridade referencial.

Para acessar o PostgreSQL pelo container:

```bash
docker exec -it desafio_dados_postgres psql -U postgres -d desafio_dados
```

Depois, as consultas de `sql/consultas.sql` podem ser executadas no PostgreSQL/pgAdmin.

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
recomendacao
```

Relações principais:

```text
categoria 1 ─── N conteudo
usuario   1 ─── N interacao
conteudo  1 ─── N interacao
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

Os comentários ainda não são carregados no PostgreSQL nesta etapa. Eles permanecem disponíveis nos arquivos processados para a etapa de MongoDB.

---

## 11. Resumo do processamento

O arquivo `dados/processados/resumo.json` registra a classificação dos registros, correções e tempo total do processamento.

A estrutura atual contém:

```text
catalogo
interacoes
comentarios
registros_carregados
registros_corrigidos
tempo_processamento_segundos
```

A nomenclatura de `registros_carregados` deverá ser refinada na integração das próximas etapas para diferenciar claramente registros processados de registros efetivamente carregados em cada banco.

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
- tempo total de processamento.

Como melhoria final do Estudante 01, podem ser adicionados tempos individuais das principais etapas do pipeline.

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

Cria o modelo relacional e suas restrições.

### `sql/consultas.sql`

Contém consultas utilizadas para verificar:

- quantidade de registros por tabela;
- conteúdos por categoria;
- interações por tipo;
- conteúdos mais avaliados;
- interações sem conteúdo;
- interações sem usuário.

---

## 15. Testes

Os testes estão organizados em:

```text
tests/test_validadores.py
tests/test_tratamentos.py
tests/test_resumo.py
tests/test_postgresql.py
```

Executar todos os testes com:

```bash
python -m pytest -v
```

Resultado validado na etapa atual:

```text
64 passed in 0.46s
```

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

## 18. Próxima etapa — Estudante 02

O Estudante 02 deve partir do estado produzido pelo Estudante 01, sem alterar os arquivos brutos.

A sequência recomendada é:

```text
1. Reproduzir o ambiente conforme a seção "Ordem de execução".
2. Executar os testes e confirmar 64 testes aprovados.
3. Executar `python -m src.main`.
4. Conferir `dados/processados/`.
5. Conferir `logs/processamento.log`.
6. Conferir o PostgreSQL e as consultas de `sql/consultas.sql`.
7. Utilizar os dados processados como entrada da etapa de MongoDB.
8. Implementar MongoDB para os dados semiestruturados.
9. Implementar embeddings.
10. Implementar armazenamento/busca vetorial conforme a arquitetura definida pela equipe.
11. Implementar a estratégia de recomendação.
12. Documentar as novas dependências, configurações, scripts e decisões no README.
```

---

## 19. Arquitetura atual e evolução prevista

Etapa implementada:

```text
CSV / JSON
    ↓
Leitura
    ↓
Validação
    ↓
Tratamento
    ↓
Dados processados
    ↓
PostgreSQL
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
- Os comentários permanecem fora da carga PostgreSQL nesta etapa e serão utilizados no MongoDB.
- O resumo deverá ser ajustado quando as próximas bases forem integradas, principalmente para distinguir registros processados e registros carregados em cada banco.
- Os logs já registram o tempo total e as principais etapas; tempos individuais por etapa podem ser acrescentados na revisão final.

---

## 21. Checklist rápido para reprodução

```text
[ ] Clonar/obter o projeto
[ ] Criar o .env a partir do .env.example
[ ] Instalar requirements.txt
[ ] Executar docker compose up -d
[ ] Conferir docker ps
[ ] Executar sql/criar_banco.sql
[ ] Executar python -m pytest -v
[ ] Confirmar 64 passed
[ ] Executar python -m src.main
[ ] Conferir dados/processados/
[ ] Conferir logs/processamento.log
[ ] Executar as consultas de sql/consultas.sql
[ ] Confirmar PostgreSQL com 1000 conteúdos, 150 usuários e 1000 interações
[ ] Entregar os dados processados para a próxima etapa
```