# Импульс: Тестовое задание на стажировку Applied AI web-сервисов 

## Описание

Сервис представляет из себя REST API (без UI), и осуществляет создание таких URL, их менеджмент (деактивация, устаревание), а также перенаправление на оригинальный ресурс при обращении к коротким URL, и сбор статистики по переходам.

## Развернутый сервис для тестирования
- Тестовый сервис развернут и доступен по адресу: https://api.nevermorevpn.ru/
- Документация openAPI доступна по адресу: https://api.nevermorevpn.ru/docs
- Аккаунт для тестирования обычного пользователя: `user` / `userpassword`
- Аккаунт для тестирования администратора: `admin` / `GSjI9gDJ`


# Инструкция по развертыванию backend сервиса с помощью Docker Compose

## Оглавление
1. [Структура проекта](#структура-проекта)
2. [Развертывание сервиса](#развертывание-сервиса)
3. [Проверка работоспособности](#проверка-работоспособности)
4. [Управление сервисом](#управление-сервисом)
5. [Решение проблем](#решение-проблем)

## Структура проекта

Проект имеет следующую структуру:
```
YADRO_Applied_AI/
├── alembic.ini                                 # Конфигурационный файл Alembic для миграций БД
├── api/                                        # API эндпоинты и маршруты
│   ├── __init__.py                             # Инициализация пакета API
│   ├── admin.py                                # Административные эндпоинты
│   ├── auth.py                                 # Эндпоинты аутентификации и авторизации
│   ├── dependencies.py                         # Зависимости FastAPI (middleware, проверки)
│   ├── exceptions_handlers.py                  # Обработчики исключений API
│   ├── private.py                              # Приватные эндпоинты (требуют авторизации)
│   └── public.py                               # Публичные эндпоинты (доступны всем)
├── database/                                   # Модели и настройки базы данных
│   ├── __init__.py                             # Инициализация пакета БД
│   ├── db.py                                   # Конфигурация подключения к БД
│   ├── migrations/                             # Директория миграций Alembic
│   │   ├── env.py                              # Конфигурация окружения миграций
│   │   ├── README                              # Документация по миграциям
│   │   ├── script.py.mako                      # Шаблон для генерации миграций
│   │   └── versions/                           # Версии миграций
│   │       ├── 1cd22e2e2d66_base_commit.py     # Базовая миграция
│   │       └── 2715138ab76b_update_fields.py   # Обновление полей БД
│   └── models.py                               # SQLAlchemy модели данных
├── schemas/                                    # Pydantic схемы для валидации данных
│   ├── __init__.py                             # Инициализация пакета схем
│   ├── link.py                                 # Схемы для работы с ссылками
│   └── user.py                                 # Схемы для работы с пользователями
├── utils/                                      # Утилиты и вспомогательные функции
│   ├── __init__.py                             # Инициализация пакета утилит
│   ├── links.py                                # Утилиты для работы с короткими ссылками
│   ├── passwording.py                          # Утилиты для хеширования паролей
│   └── settings.py                             # Настройки приложения и конфигурация
├── compose.yaml                                # Docker Compose конфигурация
├── Dockerfile                                  # Инструкции для сборки Docker образа
├── pyproject.toml                              # Конфигурация проекта и зависимости
├── uv.lock                                     # Файл блокировки зависимостей
├── LICENSE                                     # Лицензия проекта
├── README.md                                   # Документация проекта
└── main.py                                     # Точка входа FastAPI приложения
```

## Развертывание сервиса

### Шаг 1: Клонирование и подготовка
```bash
# Клонирование репозитория
git clone https://github.com/seb-sish/YADRO_Applied_AI
# Перейдите в директорию проекта
cd YADRO_Applied_AI/
```

### Шаг 2: Создание файла .env
1. Скопируйте пример файла конфигурации:
```bash
cp .env.example .env
```

2. Отредактируйте файл `.env`, установив безопасные значения:
```env
# PostgreSQL конфигурация
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5432

POSTGRES_DB=app
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres

# Переменные для инициализации PostgreSQL контейнера
PGDATA=/var/lib/postgresql/data/pgdata

# Дэбаг SQL запросов
POSTGRES_DEBUG_SQL=false
```
**⚠️ Важно**: Измените пароль для подключения к базе данных!

### Шаг 3: Сборка и запуск
```bash
# Сборка образов (первый запуск)
docker-compose build

# Запуск сервисов в фоновом режиме
docker-compose up -d

# Или запуск с отображением логов
docker-compose up
```

### Шаг 4: Проверка статуса сервисов
```bash
# Проверка статуса всех сервисов
docker-compose ps

# Проверка логов
docker-compose logs -f
```

### Шаг 5: Применение миграций базы данных
Миграции применяются автоматически при сборке образа, но если нужно применить их вручную:
```bash
# Выполнение миграций
docker-compose exec api alembic upgrade head
```

## Проверка работоспособности

### Проверка API
1. **Проверка доступности API**:
```bash
curl http://localhost/docs
```
Откройте браузер и перейдите по адресу: http://localhost/docs



### Проверка базы данных
```bash
# Подключение к PostgreSQL
docker-compose exec postgres psql -U postgres -d app

# Проверка таблиц
\dt

# Выход из psql
\q
```

## Управление сервисом

### Основные команды
```bash
# Запуск сервисов
docker-compose up -d

# Остановка сервисов
docker-compose down

# Перезапуск сервисов
docker-compose restart

# Остановка с удалением volumes (ОСТОРОЖНО!)
docker-compose down -v

# Пересборка образов
docker-compose build --no-cache

# Обновление и перезапуск
docker-compose pull && docker-compose up -d
```

### Обновление приложения
```bash
# 1. Остановка сервисов
docker-compose down

# 2. Обновление кода
git pull origin main

# 3. Пересборка образов
docker-compose build

# 4. Запуск обновленных сервисов
docker-compose up -d
```

## Решение проблем

### Частые проблемы и решения

#### 1. Порт уже используется
**Ошибка**: `Error starting userland proxy: listen tcp 0.0.0.0:80: bind: address already in use`

**Решение**:
```bash
# Проверить, что использует порт
netstat -tulpn | grep :80

# Изменить порт в compose.yaml
ports:
  - "8080:8000"  # Вместо "80:8000"
```

#### 2. Проблемы с правами доступа
**Ошибка**: Проблемы с доступом к файлам в Linux

**Решение**:
```bash
# Добавить пользователя в группу docker
sudo usermod -aG docker $USER

# Перезайти в систему или выполнить
newgrp docker
```

#### 3. База данных недоступна
**Ошибка**: `Connection refused` при подключении к PostgreSQL

**Решение**:
```bash
# Проверить статус контейнера PostgreSQL
docker-compose ps postgres

# Проверить логи PostgreSQL
docker-compose logs postgres

# Перезапустить PostgreSQL
docker-compose restart postgres
```

#### 4. Ошибки миграций
**Решение**:
```bash
# Проверить состояние миграций
docker-compose exec api alembic current

# Применить миграции вручную
docker-compose exec api alembic upgrade head

# Откатить последнюю миграцию
docker-compose exec api alembic downgrade -1
```