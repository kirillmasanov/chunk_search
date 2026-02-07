"""
AI Search Demo - Минимальный backend
Демонстрация разницы между автоматическим и пользовательским чанкованием
"""

import os
import json
import pathlib
import asyncio
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from openai import OpenAI, AsyncOpenAI
from dotenv import load_dotenv

# Загрузка переменных окружения из корня проекта
env_path = pathlib.Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

# Конфигурация
YANDEX_API_KEY = os.getenv("YANDEX_API_KEY")
YANDEX_FOLDER_ID = os.getenv("YANDEX_FOLDER_ID")
YANDEX_CLOUD_MODEL = os.getenv("YANDEX_CLOUD_MODEL", "qwen3-235b-a22b-fp8/latest")

# Файлы данных для каждого режима
AUTO_MODE_FILE = "faq.txt"  # Файл для автоматического чанкования
CHUNKS_MODE_FILE = "faq_chunks.jsonl"  # Файл с готовыми чанками

if not YANDEX_API_KEY or not YANDEX_FOLDER_ID:
    raise ValueError("YANDEX_API_KEY и YANDEX_FOLDER_ID должны быть установлены в .env файле")

# Инициализация синхронного клиента для Yandex Cloud (для поиска и удаления)
client = OpenAI(
    api_key=YANDEX_API_KEY,
    base_url="https://ai.api.cloud.yandex.net/v1",
    project=YANDEX_FOLDER_ID
)

# Инициализация асинхронного клиента для Yandex Cloud (для загрузки и создания индексов)
async_client = AsyncOpenAI(
    api_key=YANDEX_API_KEY,
    base_url="https://ai.api.cloud.yandex.net/v1",
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

# Хранилище для Vector Store ID
vector_stores = {
    "auto": None,  # Для автоматического чанкования
    "chunks": None  # Для пользовательских чанков
}

# Pydantic модели
class SearchRequest(BaseModel):
    query: str
    mode: str  # "auto" или "chunks"
    max_num_results: int = 3  # Максимальное количество результатов (по умолчанию 3)

class SearchResponse(BaseModel):
    answer: str
    chunks: list
    mode: str
    store_id: str
    raw_response: dict


def get_data_path(filename: str) -> pathlib.Path:
    """Получить путь к файлу данных"""
    return pathlib.Path(__file__).parent.parent / "data" / filename


async def upload_file(filename: str, content_type: str, extra_body: Optional[dict] = None) -> str:
    """Асинхронно загрузить файл в Yandex Cloud AI Studio"""
    file_path = get_data_path(filename)
    
    if not file_path.exists():
        raise FileNotFoundError(f"Файл {filename} не найден в директории data/")
    
    print(f"Загружаем файл {filename}...")
    
    # Используем асинхронный клиент
    with open(file_path, "rb") as f:
        file_response = await async_client.files.create(
            file=(filename, f, content_type),
            purpose="assistants",
            extra_body=extra_body
        )
    
    print(f"Файл {filename} загружен с ID: {file_response.id}")
    return file_response.id


async def wait_for_vector_store(store_id: str, name: str) -> str:
    """Асинхронное ожидание готовности Vector Store
    
    Args:
        store_id: ID Vector Store
        name: Название для логирования
    
    Returns:
        store_id если индекс готов
    """
    print(f"Ожидаем готовности индекса '{name}'...")
    max_attempts = 60  # 2 минуты максимум
    attempt = 0
    
    while attempt < max_attempts:
        store = await async_client.vector_stores.retrieve(store_id)
        status = store.status
        
        if status == "completed":
            print(f"✓ Vector Store '{name}' готов!")
            return store_id
        elif status == "failed":
            raise Exception(f"Ошибка при создании индекса '{name}'")
        
        await asyncio.sleep(2)
        attempt += 1
    
    raise TimeoutError(f"Превышено время ожидания готовности индекса '{name}'")


async def create_auto_chunking_store() -> str:
    """Асинхронно создать Vector Store с автоматическим чанкованием
    
    Загружает текстовый файл и создает индекс с автоматическим разбиением на чанки.
    
    Returns:
        ID созданного Vector Store
    """
    print("\n" + "-"*50)
    print("Режим A: Автоматическое чанкование")
    print("-"*50)
    
    # Загружаем текстовый файл
    file_id = await upload_file(AUTO_MODE_FILE, "text/plain")
    
    # Создаем Vector Store с автоматическим чанкованием
    print(f"Создаем Vector Store 'FAQ Auto Chunking'...")
    vector_store = await async_client.vector_stores.create(
        name="FAQ Auto Chunking",
        file_ids=[file_id],
        expires_after={"anchor": "last_active_at", "days": 1},
        chunking_strategy={
            "type": "static",
            "static": {
                "max_chunk_size_tokens": 200,
                "chunk_overlap_tokens": 10
            }
        }
    )
    
    store_id = vector_store.id
    print(f"Vector Store создан с ID: {store_id}")
    
    # Ожидаем готовности
    await wait_for_vector_store(store_id, "FAQ Auto Chunking")
    
    return store_id


async def create_custom_chunks_store() -> str:
    """Асинхронно создать Vector Store с пользовательскими чанками
    
    Загружает JSONL файл с готовыми чанками (format="chunks").
    Каждая строка JSONL содержит готовый чанк с метаданными.
    
    Returns:
        ID созданного Vector Store
    """
    print("\n" + "-"*50)
    print("Режим B: Пользовательские чанки")
    print("-"*50)
    
    # Загружаем JSONL файл с чанками
    file_id = await upload_file(
        CHUNKS_MODE_FILE,
        "application/jsonlines",
        extra_body={"format": "chunks"}
    )
    
    # Создаем Vector Store без автоматического чанкования
    # Для JSONL с format="chunks" параметр chunking_strategy не нужен
    print(f"Создаем Vector Store 'FAQ Custom Chunks'...")
    vector_store = await async_client.vector_stores.create(
        name="FAQ Custom Chunks",
        file_ids=[file_id],
        expires_after={"anchor": "last_active_at", "days": 1}
    )
    
    store_id = vector_store.id
    print(f"Vector Store создан с ID: {store_id}")
    
    # Ожидаем готовности
    await wait_for_vector_store(store_id, "FAQ Custom Chunks")
    
    return store_id


def search_in_store(query: str, store_id: str, max_num_results: int = 3) -> dict:
    """Выполнить поиск в Vector Store
    
    Args:
        query: Поисковый запрос
        store_id: ID Vector Store
        max_num_results: Максимальное количество результатов (по умолчанию 3)
    """
    print(f"Выполняем поиск: '{query}' (max_results={max_num_results})")
    
    model_uri = f"gpt://{YANDEX_FOLDER_ID}/{YANDEX_CLOUD_MODEL}"
    
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
5. Если ответ неполный - укажи это""",
            tools=[{
                "type": "file_search",
                "vector_store_ids": [store_id],
                "max_num_results": max_num_results
            }],
            input=query
        )
        
        # Сохраняем сырой ответ
        raw_response = response.model_dump()
        
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
        
        print(f"Найдено {len(chunks)} фрагментов")
        
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
    """Инициализация Vector Stores - параллельное создание индексов для обоих режимов"""
    print("\n" + "="*50)
    print("Инициализация AI Search Demo (параллельно)")
    print("="*50)
    
    try:
        results = {
            "auto": {"status": "skipped", "store_id": None},
            "chunks": {"status": "skipped", "store_id": None}
        }
        
        # Создаем список задач для параллельного выполнения
        tasks = []
        task_modes = []
        
        # Режим A: Автоматическое чанкование
        if not vector_stores["auto"]:
            tasks.append(create_auto_chunking_store())
            task_modes.append("auto")
        else:
            print(f"\nРежим A уже существует: {vector_stores['auto']}")
            results["auto"] = {"status": "already_exists", "store_id": vector_stores["auto"]}
        
        # Режим B: Пользовательские чанки
        if not vector_stores["chunks"]:
            tasks.append(create_custom_chunks_store())
            task_modes.append("chunks")
        else:
            print(f"\nРежим B уже существует: {vector_stores['chunks']}")
            results["chunks"] = {"status": "already_exists", "store_id": vector_stores["chunks"]}
        
        # Выполняем задачи параллельно
        if tasks:
            print(f"\n🚀 Запускаем {len(tasks)} задач параллельно...\n")
            store_ids = await asyncio.gather(*tasks)
            
            # Сохраняем результаты
            for mode, store_id in zip(task_modes, store_ids):
                vector_stores[mode] = store_id
                results[mode] = {"status": "created", "store_id": store_id}
        
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


@app.get("/api/stores")
async def get_stores():
    """Получить ID Vector Stores"""
    return {
        "auto": vector_stores["auto"],
        "chunks": vector_stores["chunks"]
    }


@app.get("/api/data/{mode}")
async def get_data_file(mode: str):
    """Получить содержимое файла данных для указанного режима"""
    if mode not in ["auto", "chunks"]:
        raise HTTPException(status_code=400, detail="mode должен быть 'auto' или 'chunks'")
    
    try:
        if mode == "auto":
            file_path = get_data_path(AUTO_MODE_FILE)
        else:
            file_path = get_data_path(CHUNKS_MODE_FILE)
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail=f"Файл не найден: {file_path.name}")
        
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        return {
            "mode": mode,
            "filename": file_path.name,
            "content": content,
            "size": len(content)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при чтении файла: {str(e)}")


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
        result = search_in_store(request.query, store_id, request.max_num_results)
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