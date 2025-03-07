# Observatório das Florestas Públicas - Backend

Esse é o Backend do Observatório das Florestas Públicas é uma iniciativa do IPAM e da Amazônia de Pé para que a sociedade civil possa monitorar as Florestas Públicas Não Destinadas da Amazônia e cobrar sua proteção. Este projeto é responsável por fornecer a base de dados e APIs do Observatório.

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

