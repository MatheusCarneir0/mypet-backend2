# MyPet - Sistema de Gerenciamento para Pet Shop

Sistema completo de gerenciamento para a FarmaVet - Pet Shop em Boa Viagem, CE.

## 🚀 Tecnologias

- Python 3.11+
- Django 5.0
- Django REST Framework 3.14
- PostgreSQL 15
- Redis
- Celery
- Docker & Docker Compose

## 📋 Pré-requisitos

- Docker
- Docker Compose
- Git

## 🔧 Instalação

1. Clone o repositório:

```bash
git clone https://github.com/seu-usuario/mypet-backend.git
cd mypet-backend
```

2. Copie o arquivo de ambiente:

```bash
cp .env.example .env
```

3. Configure as variáveis de ambiente no arquivo `.env`

4. Suba os containers:

```bash
docker-compose up -d
```

5. Execute as migrações:

```bash
docker-compose exec web python manage.py migrate
```

6. Popule o banco com dados iniciais:

```bash
docker-compose exec web python scripts/seed_data.py
```

7. Acesse:

- API: http://localhost:8000/api/v1/
- Admin: http://localhost:8000/admin/
- Docs: http://localhost:8000/api/docs/

## 🧪 Testes

```bash
docker-compose exec web python manage.py test
```

## 📖 Documentação da API

Acesse: http://localhost:8000/api/docs/

## 👥 Equipe

- Andrey Victor - Gerente de Projeto
- Larissa Vieira - Analista de Sistemas
- Jhonata Vieira - Frontend Developer
- Matheus Cavalcante - Backend Developer
- Michel Júnior - QA / Tester

## 📄 Licença

Este projeto é privado e pertence ao IFCE Campus Boa Viagem.

