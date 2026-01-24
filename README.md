# MyPet Backend

Sistema de gestão de agendamentos para clínica veterinária desenvolvido com Django REST Framework.

## 📋 Descrição

O MyPet Backend é uma API RESTful desenvolvida em Django que fornece funcionalidades para gerenciamento de:
- Usuários (Clientes, Funcionários, Administradores)
- Clientes e seus pets
- Agendamentos de consultas
- Serviços oferecidos
- Pagamentos (preparado para integração com gateway)
- Notificações

## 🚀 Tecnologias

- **Django 5.0+**: Framework web Python
- **Django REST Framework**: Framework para construção de APIs REST
- **PostgreSQL 15**: Banco de dados relacional
- **Redis**: Cache e broker para Celery
- **Docker & Docker Compose**: Containerização
- **JWT**: Autenticação baseada em tokens
- **drf-spectacular**: Documentação OpenAPI/Swagger

## 📁 Estrutura do Projeto

```
mypet-backend/
├── config/              # Configurações do Django
│   ├── settings/        # Settings separados (base, dev, prod)
│   ├── urls.py         # URLs principais
│   └── api_urls.py     # URLs da API v1
├── apps/               # Aplicações Django
│   ├── users/          # Gerenciamento de usuários
│   ├── clients/        # Clientes
│   ├── pets/           # Pets
│   ├── appointments/   # Agendamentos
│   ├── services/       # Serviços
│   ├── payments/       # Pagamentos
│   └── notifications/ # Notificações
├── core/               # Utilitários e código compartilhado
│   ├── exceptions.py   # Exceções customizadas
│   ├── permissions.py  # Permissões customizadas
│   ├── pagination.py   # Paginação
│   └── utils.py        # Funções utilitárias
├── docker-compose.yml  # Orquestração de containers
├── Dockerfile          # Imagem Docker do backend
└── requirements.txt    # Dependências Python
```

## 🛠️ Como Rodar com Docker

### Pré-requisitos

- Docker e Docker Compose instalados
- Git

### Passos

1. **Clone o repositório** (se ainda não tiver):
```bash
git clone <url-do-repositorio>
cd mypet-backend
```

2. **Crie o arquivo `.env`** baseado no `.env.example`:
```bash
cp .env.example .env
```

3. **Edite o arquivo `.env`** e configure as variáveis necessárias:
```env
SECRET_KEY=sua-chave-secreta-aqui
DEBUG=True
DB_PASSWORD=postgres
# ... outras variáveis
```

4. **Construa e inicie os containers**:
```bash
docker-compose up --build
```

5. **Execute as migrações** (em outro terminal):
```bash
docker-compose exec backend python manage.py migrate
```

6. **Crie um superusuário** (opcional):
```bash
docker-compose exec backend python manage.py createsuperuser
```

7. **Acesse a aplicação**:
   - API: http://localhost:8000
   - Admin: http://localhost:8000/admin
   - Documentação Swagger: http://localhost:8000/api/docs/
   - Health Check: http://localhost:8000/health/

## 📝 Comandos Úteis

### Docker Compose

```bash
# Iniciar containers
docker-compose up

# Iniciar em background
docker-compose up -d

# Parar containers
docker-compose down

# Ver logs
docker-compose logs -f backend

# Executar comando no container
docker-compose exec backend python manage.py <comando>
```

### Django

```bash
# Criar migrações
docker-compose exec backend python manage.py makemigrations

# Aplicar migrações
docker-compose exec backend python manage.py migrate

# Criar superusuário
docker-compose exec backend python manage.py createsuperuser

# Coletar arquivos estáticos
docker-compose exec backend python manage.py collectstatic --noinput

# Shell do Django
docker-compose exec backend python manage.py shell
```

## 🔐 Autenticação

A API utiliza JWT (JSON Web Tokens) para autenticação.

### Obter Token

```bash
POST /api/v1/auth/token/
Content-Type: application/json

{
  "username": "usuario",
  "password": "senha"
}
```

### Usar Token

```bash
Authorization: Bearer <seu-token>
```

## 📚 Documentação da API

A documentação interativa está disponível em:
- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/docs/redoc/

## 🏗️ Arquitetura

O projeto segue princípios SOLID e Clean Architecture:

- **Models**: Definição dos modelos de dados
- **Serializers**: Validação e serialização de dados
- **Services**: Lógica de negócio
- **Selectors**: Queries otimizadas e reutilizáveis
- **Views/ViewSets**: Camada HTTP, apenas orquestração
- **Permissions**: Controle de acesso
- **Exceptions**: Tratamento de erros customizado

## 🔧 Configuração de Desenvolvimento vs Produção

O projeto possui settings separados:

- **Desenvolvimento**: `config.settings.development`
- **Produção**: `config.settings.production`

Configure via variável de ambiente `DJANGO_SETTINGS_MODULE`.

## 📦 Dependências Principais

- Django 5.0.1
- djangorestframework 3.14.0
- djangorestframework-simplejwt 5.3.1
- psycopg2-binary 2.9.9
- python-decouple 3.8
- drf-spectacular 0.27.0
- celery 5.3.4
- redis 5.0.1

## 🚧 Próximos Passos

- [ ] Implementar app de Clientes
- [ ] Implementar app de Pets
- [ ] Implementar app de Agendamentos
- [ ] Implementar app de Serviços
- [ ] Integrar gateway de pagamento (Stripe/Mercado Pago)
- [ ] Implementar sistema de notificações
- [ ] Adicionar testes automatizados
- [ ] Configurar CI/CD

## 📄 Licença

Este projeto é privado e proprietário.

## 👥 Contribuição

Este é um projeto interno. Para contribuições, entre em contato com a equipe de desenvolvimento.

