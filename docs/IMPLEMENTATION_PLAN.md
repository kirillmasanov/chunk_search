
# План реализации AI Search Demo

## Текущий статус

✅ Архитектура проекта создана  
✅ Blueprint документация готова  
✅ API документация готова  
✅ README создан  

## Следующие шаги

### 1. Структура проекта и зависимости

#### Backend структура

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── models.py
│   └── services/
│       ├── __init__.py
│       ├── vectorstore.py
│       ├── search.py
│       └── file_handler.py
├── tests/
│   ├── __init__.py
│   ├── test_vectorstore.py
│   ├── test_search.py
│   └── test_file_handler.py
├── requirements.txt
├── requirements-dev.txt
├── .env.example
├── .gitignore
└── pytest.ini
```

#### Backend requirements.txt

```
fastapi==0.109.0
uvicorn[standard]==0.27.0
openai==1.10.0
python-dotenv==1.0.0
pydantic==2.5.3
pydantic-settings==2.1.0
python-multipart==0.0.6
aiofiles==23.2.1
```

#### Backend requirements-dev.txt

```
pytest==7.4.4
pytest-asyncio==0.23.3
pytest-cov==4.1.0
black==24.1.1
flake8==7.0.0
mypy==1.8.0
httpx==0.26.0
```

#### Backend .env.example

```bash
# Yandex Cloud Credentials
YC_API_KEY=your_api_key_here
YC_FOLDER_ID=your_folder_id_here

# AI Studio Configuration
YC_AI_STUDIO_BASE_URL=https://api.yandex-cloud.ru/ai-studio/v1
YC_MODEL_URI=gpt://{folder_id}/qwen3-235b-a22b-fp8/latest

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

#### Frontend структура

```
frontend/
├── index.html
├── css/
│   └── styles.css
└── js/
    ├── app.js
    ├── api.js
    └── ui.js
```

#### Data структура

```
data/
├── faq_full.txt
└── faq_chunks.jsonl
```

### 2. Синтетические данные FAQ

#### faq_full.txt (для автоматического чанкования)

```
Вопрос: Можно ли работать с Yandex Cloud AI без интернета?
Ответ: Нет, для работы с Yandex Cloud AI Studio требуется постоянное подключение к интернету, так как все вычисления происходят в облаке. Модели и данные хранятся на серверах Yandex Cloud, и для выполнения запросов необходим доступ к API.

Вопрос: Какие модели доступны в AI Studio?
Ответ: В Yandex Cloud AI Studio доступны следующие модели: YandexGPT (различные версии), YandexGPT-Lite для быстрых ответов, qwen3-235b для сложных задач, и специализированные модели для embeddings. Каждая модель оптимизирована под определенные задачи.

Вопрос: Как создать Vector Store?
Ответ: Для создания Vector Store используйте метод create() через OpenAI SDK. Укажите имя хранилища и дождитесь его создания. После этого можно загружать файлы и создавать индекс для поиска.

Вопрос: Что такое чанкование документов?
Ответ: Чанкование - это процесс разбиения больших документов на меньшие фрагменты (чанки) для эффективного поиска и обработки. Можно использовать автоматическое чанкование или загрузить предварительно подготовленные чанки в формате JSONL.

Вопрос: Какой формат данных поддерживается для пользовательских чанков?
Ответ: Для загрузки пользовательских чанков используется формат JSONL (JSON Lines). Каждая строка файла должна содержать JSON объект с обязательными полями: id (уникальный идентификатор) и body (текстовое содержимое чанка).

Вопрос: Как долго строится индекс?
Ответ: Время построения индекса зависит от количества и размера чанков. Обычно для 100 чанков индекс строится менее 2 минут. Статус построения можно отслеживать через API, проверяя поле status.

Вопрос: Какие ограничения на размер файлов?
Ответ: Максимальный размер одного файла - 512 МБ. Рекомендуется разбивать большие документы на несколько файлов. Для чанков рекомендуемый размер - до 2000 токенов (~1500 слов) для оптимальной работы модели.

Вопрос: Как работает поиск с RAG?
Ответ: RAG (Retrieval-Augmented Generation) сначала находит релевантные чанки в Vector Store по вашему запросу, затем использует их как контекст для генерации ответа моделью. Это позволяет получать точные ответы на основе ваших данных.

Вопрос: Можно ли обновить данные в индексе?
Ответ: Да, вы можете удалить старые файлы и загрузить новые. Индекс автоматически обновится. Также можно создать новый Vector Store для новой версии данных и переключаться между ними.

Вопрос: Как оценить качество поиска?
Ответ: Качество поиска оценивается по метрикам Precision@K и Recall@K, а также по score релевантности чанков. Высокий score (близкий к 1.0) означает высокую релевантность найденного чанка запросу.

Вопрос: Поддерживается ли мультиязычность?
Ответ: Да, модели Yandex Cloud AI Studio поддерживают множество языков, включая русский, английский и другие. Поиск работает на любом языке, на котором обучена модель.

Вопрос: Как защитить API ключи?
Ответ: API ключи должны храниться в переменных окружения или в защищенном хранилище секретов. Никогда не коммитьте ключи в git. Используйте .env файлы для локальной разработки и secrets management для production.

Вопрос: Какая стоимость использования AI Studio?
Ответ: Стоимость зависит от используемой модели и объема запросов. Подробную информацию о ценах можно найти на странице Yandex Cloud AI Studio в разделе тарификации. Доступен калькулятор для расчета стоимости.

Вопрос: Можно ли использовать свои модели?
Ответ: В настоящее время AI Studio предоставляет предобученные модели Yandex. Возможность использования собственных моделей планируется в будущих версиях платформы.

Вопрос: Как получить техподдержку?
Ответ: Техническая поддержка доступна через support@yandex-cloud.ru, документацию на yandex.cloud/docs/ai-studio, и сообщество в Telegram канале @yandex_cloud_ai. Также можно создавать issues в GitHub репозитории проекта.
```

#### faq_chunks.jsonl (пользовательские чанки)

```jsonl
{"id": "faq_offline_mode", "body": "Вопрос: Можно ли работать с Yandex Cloud AI без интернета?\n\nОтвет: Нет, для работы с Yandex Cloud AI Studio требуется постоянное подключение к интернету, так как все вычисления происходят в облаке. Модели и данные хранятся на серверах Yandex Cloud, и для выполнения запросов необходим доступ к API."}
{"id": "faq_available_models", "body": "Вопрос: Какие модели доступны в AI Studio?\n\nОтвет: В Yandex Cloud AI Studio доступны следующие модели: YandexGPT (различные версии), YandexGPT-Lite для быстрых ответов, qwen3-235b для сложных задач, и специализированные модели для embeddings. Каждая модель оптимизирована под определенные задачи."}
{"id": "faq_create_vectorstore", "body": "Вопрос: Как создать Vector Store?\n\nОтвет: Для создания Vector Store используйте метод create() через OpenAI SDK. Укажите имя хранилища и дождитесь его создания. После этого можно загружать файлы и создавать индекс для поиска."}
{"id": "faq_chunking", "body": "Вопрос: Что такое чанкование документов?\n\nОтвет: Чанкование - это процесс разбиения больших документов на меньшие фрагменты (чанки) для эффективного поиска и обработки. Можно использовать автоматическое чанкование или загрузить предварительно подготовленные чанки в формате JSONL."}
{"id": "faq_jsonl_format", "body": "Вопрос: Какой формат данных поддерживается для пользовательских чанков?\n\nОтвет: Для загрузки пользовательских чанков используется формат JSONL (JSON Lines). Каждая строка файла должна содержать JSON объект с обязательными полями: id (уникальный идентификатор) и body (текстовое содержимое чанка)."}
{"id": "faq_index_build_time", "body": "Вопрос: Как долго строится индекс?\n\nОтвет: Время построения индекса зависит от количества и размера чанков. Обычно для 100 чанков индекс строится менее 2 минут. Статус построения можно отслеживать через API, проверяя поле status."}
{"id": "faq_file_size_limits", "body": "Вопрос: Какие ограничения на размер файлов?\n\nОтвет: Максимальный размер одного файла - 512 МБ. Рекомендуется разбивать большие документы на несколько файлов. Для чанков рекомендуемый размер - до 2000 токенов (~1500 слов) для оптимальной работы модели."}
{"id": "faq_rag_how_it_works", "body": "Вопрос: Как работает поиск с RAG?\n\nОтвет: RAG (Retrieval-Augmented Generation) сначала находит релевантные чанки в Vector Store по вашему запросу, затем использует их как контекст для генерации ответа моделью. Это позволяет получать точные ответы на основе ваших данных."}
{"id": "faq_update_data", "body": "Вопрос: Можно ли обновить данные в индексе?\n\nОтвет: Да, вы можете удалить старые файлы и загрузить новые. Индекс автоматически обновится. Также можно создать новый Vector Store для новой версии данных и переключаться между ними."}
{"id": "faq_search_quality", "body": "Вопрос: Как оценить качество поиска?\n\nОтвет: Качество поиска оценивается по метрикам Precision@K и Recall@K, а также по score релевантности чанков. Высокий score (близкий к 1.0) означает высокую релевантность найденного чанка запросу."}
{"id": "faq_multilingual", "body": "Вопрос: Поддерживается ли мультиязычность?\n\nОтвет: Да, модели Yandex Cloud AI Studio поддерживают множество языков, включая русский, английский и другие. Поиск работает на любом языке, на котором обучена модель."}
{"id": "faq_api_keys_security", "body": "Вопрос: Как защитить API ключи?\n\nОтвет: API ключи должны храниться в переменных окружения или в защищенном хранилище секретов. Никогда не коммитьте ключи в git. Используйте .env файлы для локальной разработки и secrets management для production."}
{"id": "faq_pricing", "body": "Вопрос: Какая стоимость использования AI Studio?\n\nОтвет: Стоимость зависит от используемой модели и объема запросов. Подробную информацию о ценах можно найти на странице Yandex Cloud AI Studio в разделе тарификации. Доступен калькулятор для расчета стоимости."}
{"id": "faq_custom_models", "body": "Вопрос: Можно ли использовать свои модели?\n\nОтвет: В настоящее время AI Studio предоставляет предобученные модели Yandex. Возможность использования собственных моделей планируется в будущих версиях платформы."}
{"id": "faq_support", "body": "Вопрос: Как получить техподдержку?\n\nОтвет: Техническая поддержка доступна через support@yandex-cloud.ru, документацию на yandex.cloud/docs/ai-studio, и сообщество в Telegram канале @yandex_cloud_ai. Также можно создавать issues в GitHub репозитории проекта."}
```

### 3. Backend реализация

#### app/config.py

```python
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # Yandex Cloud
    yc_api_key: str
    yc_folder_id: str
    yc_ai_studio_base_url: str = "https://api.yandex-cloud.ru/ai-studio/v1"
    yc_model_uri: str
    
    # Application
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    debug: bool = False
    
    # Search
    default_top_k: int = 5
    max_chunk_size: int = 2000
    search_timeout: int = 30
    
    # CORS
    cors_origins: list[str] = ["http://localhost:8080"]
    
    class Config:
        env_file = ".env"
        env_prefix = ""

@lru_cache()
def get_settings() -> Settings:
    return Settings()
```

#### app/models.py

```python
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime

class VectorStoreCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)

class VectorStoreResponse(BaseModel):
    store_id: str
    name: str
    status: str
    created_at: datetime
    file_counts: Optional[dict] = None

class FileUploadResponse(BaseModel):
    file_id: str
    filename: str
    size: int
    status: str
    store_id: str
    chunks_count: Optional[int] = None

class SearchRequest(BaseModel):
    query: str = Field(..., min_length=3, max_length=1000)
    store_id: str
    top_k: int = Field(default=5, ge=1, le=20)

class ChunkResponse(BaseModel):
    id: str
    body: str
    score: float

class SearchResponse(BaseModel):
    query: str
    answer: str
    chunks: List[ChunkResponse]
    metadata: dict

class CompareRequest(BaseModel):
    query: str
    store_id_a: str
    store_id_b: str
    top_k: int = Field(default=5, ge=1, le=20)

class StatusResponse(BaseModel):
    store_id: str
    status: str
    progress: int
    message: str
    estimated_time_remaining: int
```

#### app/services/vectorstore.py

```python
from openai import OpenAI
import time
import asyncio
from typing import Optional

class VectorStoreService:
    def __init__(self, client: OpenAI):
        self.client = client
    
    async def create_store(self, name: str) -> str:
        """Создать новый Vector Store"""
        response = self.client.beta.vector_stores.create(name=name)
        return response.id
    
    async def get_store(self, store_id: str) -> dict:
        """Получить информацию о Vector Store"""
        store = self.client.beta.vector_stores.retrieve(store_id)
        return {
            "store_id": store.id,
            "name": store.name,
            "status": store.status,
            "file_counts": store.file_counts.model_dump() if store.file_counts else None,
            "created_at": store.created_at
        }
    
    async def delete_store(self, store_id: str) -> bool:
        """Удалить Vector Store"""
        self.client.beta.vector_stores.delete(store_id)
        return True
    
    async def list_stores(self, limit: int = 20) -> list:
        """Список всех Vector Stores"""
        stores = self.client.beta.vector_stores.list(limit=limit)
        return [
            {
                "store_id": store.id,
                "name": store.name,
                "status": store.status,
                "created_at": store.created_at
            }
            for store in stores.data
        ]
    
    async def wait_for_ready(self, store_id: str, timeout: int = 300) -> bool:
        """Ожидать готовности индекса"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            store = await self.get_store(store_id)
            
            if store["status"] == "completed":
                return True
            elif store["status"] == "failed":
                raise Exception("Index building failed")
            
            await asyncio.sleep(5)
        
        raise TimeoutError("Index building timeout")
```

#### app/services/file_handler.py

```python
from openai import OpenAI
import json
from typing import Optional

class FileHandler:
    def __init__(self, client: OpenAI):
        self.client = client
    
    async def upload_file(
        self, 
        file_path: str, 
        store_id: str,
        format: Optional[str] = None
    ) -> dict:
        """Загрузить файл в Vector Store"""
        extra_body = {}
        if format:
            extra_body["format"] = format
        
        with open(file_path, "rb") as f:
            file_response = self.client.files.create(
                file=f,
                purpose="assistants",
                extra_body=extra_body if extra_body else None
            )
        
        # Прикрепить файл к Vector Store
        self.client.beta.vector_stores.files.create(
            vector_store_id=store_id,
            file_id=file_response.id
        )
        
        return {
            "file_id": file_response.id,
            "filename": file_response.filename,
            "size": file_response.bytes,
            "status": file_response.status
        }
    
    def validate_jsonl(self, content: str) -> tuple[bool, Optional[str]]:
        """Валидация JSONL формата"""
        lines = content.strip().split('\n')
        
        for i, line in enumerate(lines, 1):
            if not line.strip():
                continue
            
            try:
                obj = json.loads(line)
                
                if "id" not in obj:
                    return False, f"Line {i}: Missing required field 'id'"
                if "body" not in obj:
                    return False, f"Line {i}: Missing required field 'body'"
                
            except json.JSONDecodeError as e:
                return False, f"Line {i}: Invalid JSON - {str(e)}"
        
        return True, None
    
    def parse_chunks(self, jsonl_content: str) -> list:
        """Парсинг чанков из JSONL"""
        chunks = []
        for line in jsonl_content.strip().split('\n'):
            if line.strip():
                chunks.append(json.loads(line))
        return chunks
```

#### app/services/search.py

```python
from openai import OpenAI
from typing import List, Dict

class SearchService:
    def __init__(self, client: OpenAI, model_uri: str):
        self.client = client
        self.model_uri = model_uri
    
    async def search(
        self, 
        query: str, 
        store_id: str,
        top_k: int = 5
    ) -> dict:
        """Выполнить поиск и получить ответ"""
        import time
        start_time = time.time()
        
        # Получить релевантные чанки
        chunks = await self._get_chunks(query, store_id, top_k)
        
        # Сформировать контекст
        context = "\n\n".join([
            f"[Чанк {i+1}, релевантность: {c['score']:.3f}]\n{c['body']}"
            for i, c in enumerate(chunks)
        ])
        
        # Сгенерировать ответ
        answer = await self._generate_answer(query, context)
        
        search_time = int((time.time() - start_time) * 1000)
        
        return {
            "query": query,
            "answer": answer,
            "chunks": chunks,
            "metadata": {
                "store_id": store_id,
                "model": self.model_uri,
                "search_time_ms": search_time
            }
        }
    
    async def _get_chunks(
        self, 
        query: str, 
        store_id: str,
        top_k: int
    ) -> List[Dict]:
        """Получить релевантные чанки через Vector Store search"""
        # Примечание: API может отличаться, нужно проверить документацию
        # Это примерная реализация
        
        # Создаем временного ассистента для поиска
        assistant = self.client.beta.assistants.create(
            model=self.model_uri,
            tools=[{"type": "file_search"}],
            tool_resources={"file_search": {"vector_store_ids": [store_id]}}
        )
        
        # Создаем thread и отправляем запрос
        thread = self.client.beta.threads.create()
        
        message = self.client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=query
        )
        
        # Запускаем ассистента
        run = self.client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant.id
        )
        
        # Ждем завершения
        import time
        while run.status in ["queued", "in_progress"]:
            time.sleep(1)
            run = self.client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )
        
        # Получаем сообщения
        messages = self.client.beta.threads.messages.list(thread_id=thread.id)
        
        # Извлекаем чанки из annotations
        chunks = []
        for msg in messages.data:
            if msg.role == "assistant":
                for content in msg.content:
                    if hasattr(content, 'text') and hasattr(content.text, 'annotations'):
                        for annotation in content.text.annotations:
                            if hasattr(annotation, 'file_citation'):
                                # Извлекаем информацию о чанке
                                chunks.append({
                                    "id": annotation.file_citation.file_id,
                                    "body": annotation.text,
                                    "score": 0.9  # Placeholder, нужно получить реальный score
                                })
        
        # Очистка
        self.client.beta.assistants.delete(assistant.id)
        self.client.beta.threads.delete(thread.id)
        
        return chunks[:top_k]
    
    async def _generate_answer(self, query: str, context: str) -> str:
        """Сгенерировать ответ на основе контекста"""
        prompt = f"""На основе предоставленного контекста ответь на вопрос пользователя.
Используй только информацию из контекста. Если в контексте нет ответа, скажи об этом.

Контекст:
{context}

Вопрос: {query}

Ответ:"""
        
        response = self.client.chat.completions.create(
            model=self.model_uri,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        
        return response.choices[0].message.content
```

#### app/main.py

```python
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
import tempfile
import os

from .config import get_settings, Settings
from .models import *
from .services.vectorstore import VectorStoreService
from .services.file_handler import FileHandler
from .services.search import SearchService

app = FastAPI(
    title="AI Search Demo API",
    description="Demo API for Yandex Cloud AI Studio Search with custom chunks",
    version="1.0.0"
)

# CORS
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenAI client
def get_client():
    return OpenAI(
        api_key=settings.yc_api_key,
        base_url=settings.yc_ai_studio_base_url
    )

# Services
def get_vectorstore_service(client: OpenAI = Depends(get_client)):
    return VectorStoreService(client)

def get_file_handler(client: OpenAI = Depends(get_client)):
    return FileHandler(client)

def get_search_service(client: OpenAI = Depends(get_client)):
    return SearchService(client, settings.yc_model_uri)

# Endpoints
@app.post("/api/vectorstore/create", response_model=VectorStoreResponse)
async def create_vectorstore(
    request: VectorStoreCreate,
    service: VectorStoreService = Depends(get_vectorstore_service)
):
    """Создать новый Vector Store"""
    try:
        store_id = await service.create_store(request.name)
        store = await service.get_store(store_id)
        return store
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/vectorstore/{store_id}", response_model=VectorStoreResponse)
async def get_vectorstore(
    store_id: str,
    service: VectorStoreService = Depends(get_vectorstore_service)
):
    """Получить информацию о Vector Store"""
    try:
        return await service.get_store(store_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.delete("/api/vectorstore/{store_id}")
async def delete_vectorstore(
    store_id: str,
    service: VectorStoreService = Depends(get_vectorstore_service)
):
    """Удалить Vector Store"""
    try:
        await service.delete_store(store_id)
        return {"success": True, "message": "Vector store deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/vectorstore/list")
async def list_vectorstores(
    limit: int = 20,
    service: VectorStoreService = Depends(get_vectorstore_service)
):
    """Список всех Vector Stores"""
    try:
        stores = await service.list_stores(limit)
        return {"data": stores, "has_more": len(stores) == limit}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/files/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    store_id: str = Form(...),
    handler: FileHandler = Depends(get_file_handler)
):
    """Загрузить файл с автоматическим чанкованием"""
    try:
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        result = await handler.upload_file(tmp_path, store_id)
        os.unlink