# AI Search Demo - Пользовательские чанки

Демо-приложение для демонстрации разницы между автоматическим чанкованием и использованием заранее подготовленных пользовательских чанков в формате JSON Lines в Yandex Cloud AI Studio.

## Что это?

Простое приложение, которое показывает разницу между:
- **Режим A**: Автоматическое чанкование (платформа сама разбивает документ)
- **Режим B**: Пользовательские чанки (вы контролируете структуру данных)

## Структура проекта

```
chunk_search/
├── backend/
│   ├── main.py              # FastAPI сервер
│   ├── requirements.txt     # Зависимости
│   ├── .env.example         # Пример конфигурации
│   └── .gitignore
├── frontend/
│   └── index.html           # Веб-интерфейс
├── data/
│   ├── faq.txt              # FAQ для режима A
│   └── faq_chunks.jsonl     # FAQ для режима B
└── README.md
```

## Быстрый старт

### 1. Установка зависимостей

```bash
cd backend

# Создать виртуальное окружение с uv
uv venv

# Активировать окружение
source .venv/bin/activate

# Установить зависимости
uv pip install -r requirements.txt
```

> **Примечание**: Если у вас не установлен uv, установите его:
> ```bash
> curl -LsSf https://astral.sh/uv/install.sh | sh
> ```

### 2. Настройка

Создайте файл `.env` в директории `backend/`:

```bash
cd backend
cp .env.example .env
```

Отредактируйте `.env` и добавьте свои credentials:

```bash
YANDEX_API_KEY=your_api_key_here
YANDEX_FOLDER_ID=your_folder_id_here
YANDEX_CLOUD_MODEL=qwen3-235b-a22b-fp8/latest
```

### 3. Запуск

#### Вариант 1: Локальный запуск

```bash
# Из корня проекта
uv run uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

Приложение будет доступно по адресу: **http://localhost:8000**

#### Вариант 2: Запуск через Docker Compose (рекомендуется)

```bash
# Создать .env файл в корне проекта
cp backend/.env.example .env
# Отредактировать .env с вашими credentials

# Запустить приложение
docker compose up -d

# Просмотр логов
docker compose logs -f
```

Приложение будет доступно по адресу: **http://localhost:8000**

Для остановки:
```bash
docker compose down
```

## Использование

### Веб-интерфейс

1. **Откройте** http://localhost:8000 в браузере
2. **Нажмите кнопку** "Загрузить данные и создать индексы"
3. **Дождитесь** создания индексов (1-2 минуты)
4. **Выберите режим** (A или B)
5. **Введите вопрос**, например: "Как создать виртуальную машину?"
6. **Нажмите** "Найти"
7. **Сравните** результаты между режимами

**Совет**: Используйте кнопку "Удалить индексы" для удаления индексов из Vector Store и загруженных файлов. 

### API

#### Инициализация индексов

```bash
curl -X POST http://localhost:8000/api/initialize
```

#### Сброс индексов

```bash
curl -X POST http://localhost:8000/api/reset
```

#### Поиск

```bash
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Как создать виртуальную машину?",
    "mode": "chunks"
  }'
```

Параметры:
- `query` - текст запроса
- `mode` - режим поиска: `"auto"` или `"chunks"`

## Демо сценарий

### Режим A: Автоматическое чанкование

1. Выберите "Режим A"
2. Введите: "Можно ли работать без интернета?"
3. Результат: ответ модели, используемые фрагменты со score, полный ответ в JSON.

### Режим B: Пользовательские чанки

1. Выберите "Режим B"
2. Введите тот же вопрос
3. Результат: более точный ответ, фрагменты с высоким score (0.85-0.95), полный ответ в JSON. Вопрос и ответ в одном чанке.

### Вывод

Пользовательские чанки обеспечивают:
- Сохранение логической целостности (вопрос + ответ вместе)
- Более высокий score релевантности
- Более точные ответы модели
- Меньший расход токенов за счет отсутствия дублирования контекста и более точного попадания в релевантные фрагменты

## Как это работает

### Ключевое отличие в коде

**Режим A** (автоматическое чанкование):
```python
file = client.files.create(
    file=(filename, content, "text/plain"),
    purpose="assistants"
)
```

**Режим B** (пользовательские чанки):
```python
file = client.files.create(
    file=(filename, content, "application/jsonlines"),
    purpose="assistants",
    extra_body={"format": "chunks"}  # ← Ключевое!
)
```

### Формат JSONL

Файл `data/faq_chunks.jsonl`:
```jsonl
{"body": "Вопрос: ...\nОтвет: ..."}
{"body": "Вопрос: ...\nОтвет: ..."}
```

Каждая строка - отдельный чанк с полем `body`.

## Данные

В `data/` используется простой FAQ

## Разработка

### Структура backend

- `main.py` - весь код в одном файле
- Индексы создаются по запросу через кнопку в UI или API
- Endpoints:
  - `GET /` - веб-интерфейс
  - `GET /api/stores` - ID Vector Stores
  - `POST /api/initialize` - создание индексов
  - `POST /api/reset` - удаление индексов
  - `POST /api/search` - поиск

## Документация

- [Yandex Cloud AI Studio](https://yandex.cloud/ru/docs/ai-studio/)
- [Vector Store API](https://yandex.cloud/ru/docs/ai-studio/concepts/search/vectorstore)
- [Создание агента с чанками](https://yandex.cloud/ru/docs/ai-studio/operations/agents/create-prechunked-search-agent)

## Дополнительные материалы

Для детальной информации о проекте см. [`BLUEPRINT.md`](BLUEPRINT.md) - полный blueprint проекта с архитектурой, сценариями использования и инструкциями по развертыванию.