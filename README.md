# Uma iniciativa Amazônia de Pé + IPAM

Para facilitar o acesso ao debate e aos dados sobre as Florestas Públicas Não Destinadas da Amazônia, a [Amazônia de Pé](https://www.amazoniadepe.org) e o [Instituto de Pesquisa Ambiental da Amazônia (IPAM)](https://ipam.org.br/pt/) criaram o [Observatório de Florestas Públicas](https://deolhonasflorestaspublicas.org.br/).

A plataforma permite explorar mapas de forma simples, ajudando qualquer pessoa a acompanhar como estão evoluindo as destinações dessas áreas.

Com isso, fica mais fácil para a sociedade brasileira se apropriar de um tema essencial: proteger a floresta, garantir os direitos dos povos tradicionais e enfrentar a crise climática.

## Observatório das Florestas Públicas - Backend

Esse é o Backend do Mapa do Observatório das Florestas Públicas é uma iniciativa do IPAM e da Amazônia de Pé para que a sociedade civil possa monitorar as Florestas Públicas Não Destinadas da Amazônia e cobrar sua proteção. Este projeto é responsável por fornecer a base de dados e APIs do Observatório.

## 📋 Pré-requisitos

Antes de rodar o projeto localmente, você precisa garantir que os seguintes pré-requisitos estão instalados:

- **Docker**
  - Para rodar o projeto em um ambiente isolado com o Docker.
- **Docker Compose**
  - Para rodar o projeto em um ambiente isolado com o Docker.

## Rodando o projeto localmente

### Para subir os serviços basta criar os containers via Docker Compose

```bash
docker-compose up -d
```
O serviço estará disponível em http://0.0.0.0:8000

### Base de dados
É possível obter uma réplica dos dados de produção e inserir dentro do banco PostgreSQL que estará rodando dentro do Container Docker.

## Origem e destino dos dados

Todos os meses, o IPAM envia novos dados para a equipe técnica da Amazônia de Pé.  
Esses dados passam por um processo de **ETL** (Extração, Transformação e Carga), que ajusta as informações para o formato esperado pelo banco de dados da aplicação.  

Depois disso, os dados são inseridos em três tabelas principais:  

- `desmatamento`  
- `floresta_publica_nao_destinada`  
- `informacao`  

## Procedimento de atualização

Ao receber a planilha do IPAM, o primeiro passo é checar se a quantidade de linhas da aba **FPND-AREA** bate com o número de registros na tabela `floresta_publica_nao_destinada`.  

- Se a planilha tiver mais registros que o banco, significa que **novas áreas foram adicionadas ou removidas**. Nesse caso, é preciso incluir ou excluir registros.  
- Por segurança, recomenda-se fazer a **atualização completa da tabela**.  
- Se a quantidade de registros for a mesma, não há necessidade de atualizar.  

### Atualizando a tabela `floresta_publica_nao_destinada`

Essa tabela tem a seguinte estrutura:  

- `codigo`  
- `nome`  
- `esfera`  
- `orgao`  
- `estagio`  
- `estado`  
- `ano`  
- `bioma`  
- `geom`  
- `uf`  

A maior parte desses dados vem direto da planilha **FPND-AREA**:  

- `codigo <- ID_IPAM`  
- `esfera <- Governo (Estadual ou Federal)`  
- `geom <- MULTIPOLYGON da área`  
- os demais campos são autoexplicativos.  

Além da planilha, o IPAM também envia o [shapefile](https://en.wikipedia.org/wiki/Shapefile).  
Para conferir ou visualizar esses dados, você pode usar o [QGIS](https://qgis.org/), um software livre que lê shapefiles e renderiza mapas.  

O shapefile é usado para gerar o `MULTIPOLYGON` da coluna `geom`.  
Uma maneira prática de importar isso para o banco é usando o **`ogr2ogr`**, que faz parte da biblioteca GDAL.  
Documentação oficial: [ogr2ogr](https://gdal.org/en/stable/programs/ogr2ogr.html).  

Exemplo de importação para o PostgreSQL/PostGIS:  

```bash
ogr2ogr -f "PostgreSQL" PG:"host=localhost dbname=nome_do_banco user=usuario password=senha" \
FPND2024_bAmazonia_limpa_IPAM.shp -nln temp_import_geom -t_srs EPSG:4674 -lco GEOMETRY_NAME=geom \
-nlt PROMOTE_TO_MULTI -dim 2 -overwrite
```

Esse comando faz o seguinte:

- importa o shapefile para o banco **PostgreSQL/PostGIS**;  
- cria (ou sobrescreve) a tabela temporária `temp_import_geom`;  
- garante que as geometrias sejam salvas como **MultiPolygon**;  
- converte as coordenadas para o sistema **EPSG:4674**;  
- força a geometria a ser **2D** (`-dim 2`).  

> ⚠️ É essencial manter `-dim 2`. Sem isso, o mapa pode não renderizar corretamente.  

Depois de criar a tabela temporária, confira os dados importados e, então, copie-os para a tabela `floresta_publica_nao_destinada`.  

Exemplo em SQL:  

```sql
INSERT INTO ofpnd.floresta_publica_nao_destinada (
    codigo,
    nome,
    esfera,
    orgao,
    estagio,
    estado,
    ano,
    bioma,
    geom,
    uf
)
SELECT
    t.id_ipam AS codigo,
    t.nome AS nome,
    t.governo AS esfera,
    COALESCE(t.orgao, 'n/a') AS orgao,
    t.estagio AS estagio,
    t.uf AS estado,
    2024 AS ano,
    t.bioma AS bioma,
    t.geom,
    t.uf AS uf
FROM temp_import_geom t;
```

Quando terminar a importação, não esqueça de apagar a tabela temporária:  

```sql
DROP TABLE IF EXISTS temp_import_geom;
```

---

### Dados de Desmatamento

A tabela `desmatamento` possui as colunas:  

- `codigo`  
- `data`  
- `fonte`  
- `area_ha`  

Os dados vêm de duas fontes: **PRODES** e **DETER**.  

Na planilha do IPAM:  
- **DETER** → dados organizados mês a mês (por ano).  
- **PRODES** → dados organizados ano a ano.  

O objetivo é consolidar as duas planilhas para que sigam o mesmo formato esperado pelo banco.  

#### Regras de consolidação

- **`codigo`** → sempre vem de `ID_IPAM`.  
- **`data`** →  
  - Para **DETER**: usar o último dia do mês (exemplo: `2025-07-31`).  
  - Para **PRODES**: usar o último dia do ano (exemplo: `2025-12-31`).  
  - Sempre no formato `yyyy-mm-dd`.  
- **`fonte`** → `"deter"` ou `"prodes"`.  
- **`area_ha`** → valor informado na planilha.  
  - Se o campo estiver vazio ou com valor inválido, usar `0`.  

Para consolidar os dados, você pode usar o **Pandas** (Python) ou, se preferir algo mais manual, criar uma planilha de consolidação usando fórmulas (tipo um PROCV).  

---

### Atualização da tabela `informacao`

A tabela `informacao` guarda todos os demais indicadores da plataforma: Mineração, Áreas totais, CAR, Carbono, Riqueza de espécies, entre outros.  

Esses indicadores aparecem nas laterais do mapa conforme os filtros aplicados.  
Todos eles estão nas outras abas da planilha enviada pelo IPAM.  
