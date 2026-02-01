# Руководство по установке и запуску

## Предварительные требования

- Python 3.10+
- [uv](https://github.com/astral-sh/uv) - современный менеджер пакетов Python
- Yandex Cloud аккаунт с доступом к AI Studio
- API ключ Yandex Cloud

## Установка uv

### macOS/Linux
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Windows
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Проверка установки
```bash
uv --version
```

## Быстрый старт

### 1. Клонирование репозитория

```bash
git clone <repository_url>
cd chunk_search
```

### 2. Настройка backend

```bash
cd backend

# Создать виртуальное окружение с помощью uv
uv venv

# Активировать виртуальное окружение
# macOS/Linux:
source .venv/bin/activate
# Windows:
.venv\Scripts\activate

# Установить зависимости
uv pip install -r requirements.txt
```

### 3. Настройка переменных окружения

```bash
# Скопировать пример конфигурации
cp .env.example .env

# Отредактировать .env файл
nano .env  # или любой другой редактор
```

Пример `.env`:
```bash
# Yandex Cloud Credentials
YC_API_KEY=your_api_key_here
YC_FOLDER_ID=your_folder_id_here

# AI Studio Configuration
YC_AI_STUDIO_BASE_URL=https://api.yandex-cloud.ru/ai-studio/v1
YC_MODEL_URI=gpt://your_folder_id/qwen3-235b-a22b-fp8/latest

# Application Settings
APP_HOST=0.0.0.0
APP_PORT=8000
DEBUG=true

# Search Settings
DEFAULT_TOP_K=5
MAX_CHUNK_SIZE=2000
SEARCH_TIMEOUT=30

# CORS Settings
CORS_ORIGINS=http://localhost:8080,http://localhost:3000
```

### 4. Запуск backend

```bash
# Из директории backend с активированным venv
uvicorn app.main:app --reload --port 8000
```

Backend будет доступен по адресу: `http://localhost:8000`

API документация:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### 5. Запуск frontend

Frontend - это простые статические файлы (HTML/CSS/JS), поэтому не требует Node.js.

```bash
# В новом терминале, из корневой директории проекта
cd frontend

# Запустить простой HTTP сервер на Python
python -m http.server 8080
```

Frontend будет доступен по адресу: `http://localhost:8080`

## Альтернативные способы запуска frontend

### Вариант 1: Python http.server (рекомендуется)
```bash
cd frontend
python -m http.server 8080
```

### Вариант 2: Использовать любой другой статический сервер
```bash
# Если установлен PHP
cd frontend
php -S localhost:8080

# Если установлен Ruby
cd frontend
ruby -run -ehttpd . -p8080
```

### Вариант 3: Открыть напрямую в браузере
Можно открыть `frontend/index.html` напрямую в браузере, но могут быть проблемы с CORS.

## Проверка работоспособности

### 1. Проверить backend
```bash
curl http://localhost:8000/api/health
```

Ожидаемый ответ:
```json
{
  "status": "healthy",
  "timestamp": "2026-01-26T11:00:00Z",
  "services": {
    "ai_studio": "up",
    "api": "up"
  }
}
```

### 2. Проверить frontend
Откройте в браузере: `http://localhost:8080`

Вы должны увидеть интерфейс с двумя режимами работы.

## Использование uv для разработки

### Установка зависимостей для разработки
```bash
cd backend
uv pip install -r requirements-dev.txt
```

### Добавление новой зависимости
```bash
# Установить пакет
uv pip install package-name

# Обновить requirements.txt
uv pip freeze > requirements.txt
```

### Обновление зависимостей
```bash
# Обновить все пакеты
uv pip install --upgrade -r requirements.txt

# Обновить конкретный пакет
uv pip install --upgrade package-name
```

### Синхронизация окружения
```bash
# Синхронизировать окружение с requirements.txt
uv pip sync requirements.txt
```

## Разработка

### Запуск с hot-reload
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

### Запуск тестов
```bash
cd backend
pytest tests/ -v
```

### Запуск тестов с покрытием
```bash
cd backend
pytest tests/ --cov=app --cov-report=html
```

### Линтинг и форматирование
```bash
cd backend

# Форматирование кода
black app/

# Проверка типов
mypy app/

# Линтинг
flake8 app/
```

## Структура проекта

```
chunk_search/
├── backend/
│   ├── .venv/              # Виртуальное окружение (создается uv)
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── models.py
│   │   └── services/
│   ├── tests/
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   ├── .env
│   └── .env.example
├── frontend/
│   ├── index.html
│   ├── css/
│   │   └── styles.css
│   └── js/
│       ├── app.js
│       ├── api.js
│       └── ui.js
├── data/
│   ├── faq_full.txt
│   └── faq_chunks.jsonl
└── docs/
```

## Troubleshooting

### Проблема: uv не найден
**Решение**: Убедитесь, что uv установлен и добавлен в PATH:
```bash
# Проверить установку
which uv  # macOS/Linux
where uv  # Windows

# Переустановить если нужно
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Проблема: Ошибка импорта модулей
**Решение**: Убедитесь, что виртуальное окружение активировано:
```bash
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows
```

### Проблема: CORS ошибки в браузере
**Решение**: 
1. Убедитесь, что frontend запущен через HTTP сервер, а не открыт как файл
2. Проверьте настройки CORS в `.env`:
```bash
CORS_ORIGINS=http://localhost:8080
```

### Проблема: Ошибка подключения к Yandex Cloud
**Решение**: Проверьте credentials в `.env`:
```bash
# Убедитесь, что API ключ и folder ID корректны
YC_API_KEY=your_actual_api_key
YC_FOLDER_ID=your_actual_folder_id
```

### Проблема: Порт уже занят
**Решение**: Используйте другой порт:
```bash
# Backend
uvicorn app.main:app --reload --port 8001

# Frontend
python -m http.server 8081

# Не забудьте обновить CORS_ORIGINS в .env
```

## Полезные команды

### Backend

```bash
# Запуск с логированием
uvicorn app.main:app --reload --log-level debug

# Запуск на всех интерфейсах
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Запуск с несколькими воркерами (production)
uvicorn app.main:app --workers 4 --host 0.0.0.0 --port 8000
```

### Работа с зависимостями

```bash
# Показать установленные пакеты
uv pip list

# Показать устаревшие пакеты
uv pip list --outdated

# Удалить пакет
uv pip uninstall package-name

# Очистить кэш
uv cache clean
```

### Тестирование

```bash
# Запустить конкретный тест
pytest tests/test_vectorstore.py -v

# Запустить с маркерами
pytest -m "not slow" -v

# Запустить с выводом print
pytest tests/ -v -s
```

## Production deployment

### Использование Gunicorn

```bash
# Установить gunicorn
uv pip install gunicorn

# Запустить с gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Docker (опционально)

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Установить uv
RUN pip install uv

# Копировать зависимости
COPY requirements.txt .
RUN uv pip install --system -r requirements.txt

# Копировать код
COPY app/ ./app/

# Запустить
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Следующие шаги

1. ✅ Backend запущен на `http://localhost:8000`
2. ✅ Frontend запущен на `http://localhost:8080`
3. 📝 Загрузите тестовые данные из `data/`
4. 🧪 Протестируйте оба режима работы
5. 📊 Сравните результаты поиска

## Дополнительные ресурсы

- [uv документация](https://github.com/astral-sh/uv)
- [FastAPI документация](https://fastapi.tiangolo.com/)
- [Yandex Cloud AI Studio](https://yandex.cloud/ru/docs/ai-studio/)
- [OpenAI SDK](https://github.com/openai/openai-python)