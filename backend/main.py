"""
AI Search Demo - Минимальный backend
Демонстрация разницы между автоматическим и пользовательским чанкованием
"""

import os
import time
import json
import pathlib
import asyncio
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
from openai import OpenAI, AsyncOpenAI
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Конфигурация
YANDEX_API_KEY = os.getenv("YANDEX_API_KEY")
YANDEX_FOLDER_ID = os.getenv("YANDEX_FOLDER_ID")
YANDEX_CLOUD_MODEL = os.getenv("YANDEX_CLOUD_MODEL", "qwen3-235b-a22b-fp8/latest")

if not YANDEX_API_KEY or not YANDEX_FOLDER_ID:
    raise ValueError("YANDEX_API_KEY и YANDEX_FOLDER_ID должны быть установлены в .env файле")

# Инициализация синхронного клиента для Yandex Cloud
client = OpenAI(
    api_key=YANDEX_API_KEY,
    base_url="https://rest-assistant.api.cloud.yandex.net/v1",
    project=YANDEX_FOLDER_ID
)

# Инициализация асинхронного клиента для Yandex Cloud
async_client = AsyncOpenAI(
    api_key=YANDEX_API_KEY,
    base_url="https://rest-assistant.api.cloud.yandex.net/v1",
    project=YANDEX_FOLDER_ID
)

# FastAPI приложение
app = FastAPI(
    title="AI Search Demo",
    description="Демонстрация пользовательских чанков в Yandex Cloud AI Studio",
    version="1.0.0"
)

# CORS для локальной разработки
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Хранилище для Vector Store ID и File ID
vector_stores = {
    "auto": None,  # Для автоматического чанкования
    "chunks": None  # Для пользовательских чанков
}

# Хранилище для File ID
uploaded_files = {
    "auto": None,
    "chunks": None
}

# Pydantic модели
class SearchRequest(BaseModel):
    query: str
    mode: str  # "auto" или "chunks"

class SearchResponse(BaseModel):
    answer: str
    chunks: list
    mode: str
    store_id: str
    raw_response: dict


def get_data_path(filename: str) -> pathlib.Path:
    """Получить путь к файлу данных"""
    return pathlib.Path(__file__).parent.parent / "data" / filename


async def upload_file_async(filename: str, content_type: str, extra_body: Optional[dict] = None) -> str:
    """Асинхронно загрузить файл в Yandex Cloud AI Studio"""
    file_path = get_data_path(filename)
    
    if not file_path.exists():
        raise FileNotFoundError(f"Файл {filename} не найден в директории data/")
    
    print(f"Загружаем файл {filename}...")
    
    # Используем нативный асинхронный клиент
    with open(file_path, "rb") as f:
        file_response = await async_client.files.create(
            file=(filename, f, content_type),
            purpose="assistants",
            extra_body=extra_body
        )
    
    print(f"Файл {filename} загружен с ID: {file_response.id}")
    return file_response.id


async def create_vector_store_async(name: str, file_id: str) -> str:
    """Асинхронно создать Vector Store с файлом"""
    print(f"Создаем Vector Store '{name}'...")
    
    # Используем нативный асинхронный клиент
    vector_store = await async_client.vector_stores.create(
        name=name,
        file_ids=[file_id],
        expires_after={"anchor": "last_active_at", "days": 1}
    )
    
    store_id = vector_store.id
    print(f"Vector Store создан с ID: {store_id}")
    
    # Ожидание готовности индекса
    print(f"Ожидаем готовности индекса {name}...")
    max_attempts = 60  # 2 минуты максимум
    attempt = 0
    
    while attempt < max_attempts:
        store = await async_client.vector_stores.retrieve(store_id)
        status = store.status
        
        if status == "completed":
            print(f"Vector Store '{name}' готов!")
            return store_id
        elif status == "failed":
            raise Exception(f"Ошибка при создании индекса '{name}'")
        
        await asyncio.sleep(2)
        attempt += 1
    
    raise TimeoutError(f"Превышено время ожидания готовности индекса '{name}'")


def search_in_store(query: str, store_id: str) -> dict:
    """Выполнить поиск в Vector Store"""
    print(f"Выполняем поиск: '{query}' в store {store_id}")
    
    model_uri = f"gpt://{YANDEX_FOLDER_ID}/{YANDEX_CLOUD_MODEL}"
    print(f"Model URI: {model_uri}")
    
    try:
        response = client.responses.create(
            model=model_uri,
            instructions="""Ты — умный ассистент для работы с базой знаний.

ВАЖНО: Отвечай ТОЛЬКО на основе информации из подключенного поискового индекса.

Правила:
1. Используй ТОЛЬКО информацию из найденных фрагментов документов
2. Если информации нет в индексе - четко скажи: "В базе знаний нет информации по этому вопросу"
3. НЕ придумывай информацию и НЕ используй общие знания
4. Давай точные ответы на основе найденных фрагментов
5. Если ответ неполный - укажи это

Формат ответа:
- Краткий и точный ответ на вопрос
- Основан только на данных из индекса""",
            tools=[{
                "type": "file_search",
                "vector_store_ids": [store_id],
                "max_num_results": 3
            }],
            input=query
        )
        
        print(f"Response received")
        
        # Сохраняем сырой ответ
        raw_response = response.model_dump()
        print(json.dumps(raw_response, indent=2, ensure_ascii=False))
        
        # Извлекаем ответ и чанки из структуры response
        answer = ""
        chunks = []
        
        if hasattr(response, 'output') and response.output:
            for item in response.output:
                # Извлекаем результаты поиска
                if hasattr(item, 'type') and item.type == "file_search_call":
                    if hasattr(item, 'results') and item.results:
                        for result in item.results:
                            chunks.append({
                                "text": result.text if hasattr(result, 'text') else "",
                                "score": result.score if hasattr(result, 'score') else 0.0,
                                "file_id": result.file_id if hasattr(result, 'file_id') else "",
                                "filename": result.filename if hasattr(result, 'filename') else ""
                            })
                
                # Извлекаем текст ответа из message
                elif hasattr(item, 'type') and item.type == "message":
                    if hasattr(item, 'content') and item.content:
                        for content_item in item.content:
                            if hasattr(content_item, 'type') and content_item.type == "output_text":
                                if hasattr(content_item, 'text'):
                                    answer = content_item.text
                                    break
        
        print(f"Extracted answer: {answer}")
        print(f"Found {len(chunks)} chunks")
        
        return {
            "answer": answer,
            "chunks": chunks,
            "raw_response": raw_response
        }
    except Exception as e:
        print(f"Ошибка при поиске: {e}")
        import traceback
        traceback.print_exc()
        raise


@app.post("/api/initialize")
async def initialize_stores():
    """Инициализация Vector Stores - создание индексов (асинхронно)"""
    print("\n" + "="*50)
    print("Инициализация AI Search Demo (асинхронно)")
    print("="*50 + "\n")
    
    try:
        results = {
            "auto": {"status": "skipped", "store_id": None},
            "chunks": {"status": "skipped", "store_id": None}
        }
        
        # Создаем задачи для параллельного выполнения
        tasks = []
        
        # Режим A: Автоматическое чанкование
        if not vector_stores["auto"]:
            async def create_auto_store():
                print("Режим A: Автоматическое чанкование")
                file_id = await upload_file_async("faq.txt", "text/plain")
                uploaded_files["auto"] = file_id
                store_id = await create_vector_store_async("FAQ Auto Chunking", file_id)
                vector_stores["auto"] = store_id
                print(f"✓ Режим A готов: {store_id}")
                return {"status": "created", "store_id": store_id}
            
            tasks.append(("auto", create_auto_store()))
        else:
            results["auto"] = {"status": "already_exists", "store_id": vector_stores["auto"]}
        
        # Режим B: Пользовательские чанки
        if not vector_stores["chunks"]:
            async def create_chunks_store():
                print("Режим B: Пользовательские чанки")
                file_id = await upload_file_async(
                    "faq_chunks.jsonl",
                    "application/jsonlines",
                    extra_body={"format": "chunks"}
                )
                uploaded_files["chunks"] = file_id
                store_id = await create_vector_store_async("FAQ Custom Chunks", file_id)
                vector_stores["chunks"] = store_id
                print(f"✓ Режим B готов: {store_id}")
                return {"status": "created", "store_id": store_id}
            
            tasks.append(("chunks", create_chunks_store()))
        else:
            results["chunks"] = {"status": "already_exists", "store_id": vector_stores["chunks"]}
        
        # Выполняем задачи параллельно
        if tasks:
            print(f"\nЗапускаем {len(tasks)} задач параллельно...")
            task_results = await asyncio.gather(*[task for _, task in tasks], return_exceptions=True)
            
            # Обрабатываем результаты
            for (mode, _), result in zip(tasks, task_results):
                if isinstance(result, Exception):
                    print(f"✗ Ошибка в режиме {mode}: {result}")
                    raise result
                results[mode] = result
        
        print("\n" + "="*50)
        print("✓ Инициализация завершена успешно!")
        print("="*50 + "\n")
        
        return {
            "success": True,
            "message": "Индексы успешно созданы",
            "stores": results
        }
        
    except Exception as e:
        print(f"\n✗ Ошибка при инициализации: {e}\n")
        raise HTTPException(status_code=500, detail=f"Ошибка при инициализации: {str(e)}")


@app.get("/")
async def root():
    """Главная страница - отдаем frontend"""
    frontend_path = pathlib.Path(__file__).parent.parent / "frontend" / "index.html"
    if frontend_path.exists():
        return FileResponse(frontend_path)
    return {"message": "AI Search Demo API", "docs": "/docs"}


@app.get("/api/health")
async def health_check():
    """Проверка работоспособности"""
    return {
        "status": "healthy",
        "vector_stores": {
            "auto": vector_stores["auto"] is not None,
            "chunks": vector_stores["chunks"] is not None
        }
    }


@app.get("/api/stores")
async def get_stores():
    """Получить ID Vector Stores"""
    return {
        "auto": vector_stores["auto"],
        "chunks": vector_stores["chunks"]
    }


@app.post("/api/reset")
async def reset_stores():
    """Сбросить Vector Stores и удалить загруженные файлы"""
    try:
        print("\n" + "="*50)
        print("Удаление индексов и файлов")
        print("="*50)
        
        deleted = {
            "stores": {"auto": False, "chunks": False},
            "files": {"auto": False, "chunks": False}
        }
        
        # Получить список файлов из Vector Stores перед удалением
        files_to_delete = {"auto": [], "chunks": []}
        
        # Получить файлы из автоматического индекса
        if vector_stores["auto"]:
            try:
                files_list = client.vector_stores.files.list(vector_stores["auto"])
                if hasattr(files_list, 'data'):
                    for file_obj in files_list.data:
                        files_to_delete["auto"].append(file_obj.id)
            except Exception as e:
                print(f"Ошибка при получении файлов auto store: {e}")
        
        # Получить файлы из индекса с чанками
        if vector_stores["chunks"]:
            try:
                files_list = client.vector_stores.files.list(vector_stores["chunks"])
                if hasattr(files_list, 'data'):
                    for file_obj in files_list.data:
                        files_to_delete["chunks"].append(file_obj.id)
            except Exception as e:
                print(f"Ошибка при получении файлов chunks store: {e}")
        
        # Удалить автоматический индекс
        if vector_stores["auto"]:
            try:
                client.vector_stores.delete(vector_stores["auto"])
                deleted["stores"]["auto"] = True
                print(f"Удален Vector Store: {vector_stores['auto']}")
            except Exception as e:
                print(f"Ошибка при удалении auto store: {e}")
            vector_stores["auto"] = None
        
        # Удалить файлы для автоматического режима
        for file_id in files_to_delete["auto"]:
            try:
                client.files.delete(file_id)
                deleted["files"]["auto"] = True
                print(f"Удален файл: {file_id}")
            except Exception as e:
                print(f"Ошибка при удалении файла {file_id}: {e}")
        
        uploaded_files["auto"] = None
        
        # Удалить индекс с чанками
        if vector_stores["chunks"]:
            try:
                client.vector_stores.delete(vector_stores["chunks"])
                deleted["stores"]["chunks"] = True
                print(f"Удален Vector Store: {vector_stores['chunks']}")
            except Exception as e:
                print(f"Ошибка при удалении chunks store: {e}")
            vector_stores["chunks"] = None
        
        # Удалить файлы для режима с чанками
        for file_id in files_to_delete["chunks"]:
            try:
                client.files.delete(file_id)
                deleted["files"]["chunks"] = True
                print(f"Удален файл: {file_id}")
            except Exception as e:
                print(f"Ошибка при удалении файла {file_id}: {e}")
        
        uploaded_files["chunks"] = None
        
        print(f"Удалено файлов: auto={len(files_to_delete['auto'])}, chunks={len(files_to_delete['chunks'])}")
        print("="*50 + "\n")
        
        return {
            "success": True,
            "message": "Индексы и файлы удалены",
            "deleted": deleted,
            "files_deleted_count": {
                "auto": len(files_to_delete["auto"]),
                "chunks": len(files_to_delete["chunks"])
            }
        }
    except Exception as e:
        print(f"Ошибка при сбросе: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка при сбросе: {str(e)}")


@app.post("/api/search", response_model=SearchResponse)
async def search(request: SearchRequest):
    """Выполнить поиск"""
    if request.mode not in ["auto", "chunks"]:
        raise HTTPException(status_code=400, detail="mode должен быть 'auto' или 'chunks'")
    
    store_id = vector_stores[request.mode]
    if not store_id:
        raise HTTPException(
            status_code=503,
            detail=f"Vector Store для режима '{request.mode}' еще не готов"
        )
    
    try:
        result = search_in_store(request.query, store_id)
        return SearchResponse(
            answer=result["answer"],
            chunks=result["chunks"],
            mode=request.mode,
            store_id=store_id,
            raw_response=result["raw_response"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при поиске: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)