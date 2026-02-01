# API Documentation

## Базовая информация

- **Base URL**: `http://localhost:8000`
- **Content-Type**: `application/json`
- **Authentication**: API Key в заголовке (опционально для локальной разработки)

## Endpoints

### Vector Store Management

#### Создать Vector Store

```http
POST /api/vectorstore/create
```

**Request Body:**
```json
{
  "name": "my_faq_store"
}
```

**Response:**
```json
{
  "store_id": "vs_abc123xyz",
  "name": "my_faq_store",
  "status": "in_progress",
  "created_at": "2026-01-26T11:00:00Z"
}
```

**Status Codes:**
- `201` - Created
- `400` - Bad Request
- `500` - Internal Server Error

---

#### Получить информацию о Vector Store

```http
GET /api/vectorstore/{store_id}
```

**Response:**
```json
{
  "store_id": "vs_abc123xyz",
  "name": "my_faq_store",
  "status": "completed",
  "file_counts": {
    "total": 1,
    "completed": 1,
    "in_progress": 0,
    "failed": 0
  },
  "created_at": "2026-01-26T11:00:00Z",
  "updated_at": "2026-01-26T11:02:00Z"
}
```

**Status Codes:**
- `200` - OK
- `404` - Not Found
- `500` - Internal Server Error

---

#### Удалить Vector Store

```http
DELETE /api/vectorstore/{store_id}
```

**Response:**
```json
{
  "success": true,
  "message": "Vector store deleted successfully"
}
```

**Status Codes:**
- `200` - OK
- `404` - Not Found
- `500` - Internal Server Error

---

#### Список всех Vector Stores

```http
GET /api/vectorstore/list
```

**Query Parameters:**
- `limit` (optional, default: 20) - количество результатов
- `order` (optional, default: "desc") - порядок сортировки

**Response:**
```json
{
  "data": [
    {
      "store_id": "vs_abc123xyz",
      "name": "my_faq_store",
      "status": "completed",
      "created_at": "2026-01-26T11:00:00Z"
    }
  ],
  "has_more": false
}
```

**Status Codes:**
- `200` - OK
- `500` - Internal Server Error

---

### File Management

#### Загрузить файл (автоматическое чанкование)

```http
POST /api/files/upload
```

**Request (multipart/form-data):**
- `file` - файл для загрузки
- `store_id` - ID Vector Store

**Response:**
```json
{
  "file_id": "file_xyz789",
  "filename": "faq_full.txt",
  "size": 15234,
  "status": "processing",
  "store_id": "vs_abc123xyz"
}
```

**Status Codes:**
- `201` - Created
- `400` - Bad Request (invalid file format)
- `413` - Payload Too Large
- `500` - Internal Server Error

---

#### Загрузить чанки (JSONL)

```http
POST /api/files/upload-chunks
```

**Request (multipart/form-data):**
- `file` - JSONL файл с чанками
- `store_id` - ID Vector Store

**JSONL Format:**
```jsonl
{"id": "chunk_1", "body": "Текст первого чанка"}
{"id": "chunk_2", "body": "Текст второго чанка"}
```

**Response:**
```json
{
  "file_id": "file_xyz789",
  "filename": "faq_chunks.jsonl",
  "chunks_count": 15,
  "status": "processing",
  "store_id": "vs_abc123xyz"
}
```

**Status Codes:**
- `201` - Created
- `400` - Bad Request (invalid JSONL format)
- `413` - Payload Too Large
- `500` - Internal Server Error

**Validation Errors:**
```json
{
  "error": "Invalid JSONL format",
  "details": {
    "line": 5,
    "message": "Missing required field: body"
  }
}
```

---

#### Получить информацию о файле

```http
GET /api/files/{file_id}
```

**Response:**
```json
{
  "file_id": "file_xyz789",
  "filename": "faq_chunks.jsonl",
  "size": 15234,
  "status": "completed",
  "chunks_count": 15,
  "created_at": "2026-01-26T11:00:00Z"
}
```

**Status Codes:**
- `200` - OK
- `404` - Not Found
- `500` - Internal Server Error

---

#### Удалить файл

```http
DELETE /api/files/{file_id}
```

**Response:**
```json
{
  "success": true,
  "message": "File deleted successfully"
}
```

**Status Codes:**
- `200` - OK
- `404` - Not Found
- `500` - Internal Server Error

---

### Search

#### Выполнить поиск

```http
POST /api/search
```

**Request Body:**
```json
{
  "query": "Можно ли работать без интернета?",
  "store_id": "vs_abc123xyz",
  "top_k": 5
}
```

**Parameters:**
- `query` (required) - поисковый запрос (3-1000 символов)
- `store_id` (required) - ID Vector Store
- `top_k` (optional, default: 5) - количество чанков (1-20)

**Response:**
```json
{
  "query": "Можно ли работать без интернета?",
  "answer": "Нет, для работы с Yandex Cloud AI Studio требуется постоянное подключение к интернету, так как все вычисления происходят в облаке.",
  "chunks": [
    {
      "id": "faq_offline_mode",
      "body": "Вопрос: Можно ли работать с Yandex Cloud AI без интернета?\n\nОтвет: Нет, для работы с Yandex Cloud AI Studio требуется постоянное подключение к интернету...",
      "score": 0.923
    },
    {
      "id": "faq_connectivity",
      "body": "Вопрос: Какие требования к интернет-соединению?...",
      "score": 0.756
    }
  ],
  "metadata": {
    "store_id": "vs_abc123xyz",
    "model": "gpt://folder_id/qwen3-235b-a22b-fp8/latest",
    "search_time_ms": 1234
  }
}
```

**Status Codes:**
- `200` - OK
- `400` - Bad Request (invalid query)
- `404` - Not Found (store not found)
- `500` - Internal Server Error

---

#### Сравнить результаты поиска

```http
POST /api/search/compare
```

**Request Body:**
```json
{
  "query": "Можно ли работать без интернета?",
  "store_id_a": "vs_auto_chunks",
  "store_id_b": "vs_custom_chunks",
  "top_k": 5
}
```

**Response:**
```json
{
  "query": "Можно ли работать без интернета?",
  "mode_a": {
    "name": "Автоматическое чанкование",
    "store_id": "vs_auto_chunks",
    "answer": "...",
    "chunks": [...],
    "avg_score": 0.678
  },
  "mode_b": {
    "name": "Пользовательские чанки",
    "store_id": "vs_custom_chunks",
    "answer": "...",
    "chunks": [...],
    "avg_score": 0.892
  },
  "comparison": {
    "score_difference": 0.214,
    "winner": "mode_b",
    "recommendation": "Пользовательские чанки показали лучший результат"
  }
}
```

**Status Codes:**
- `200` - OK
- `400` - Bad Request
- `404` - Not Found
- `500` - Internal Server Error

---

### System

#### Health Check

```http
GET /api/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-01-26T11:00:00Z",
  "services": {
    "ai_studio": "up",
    "api": "up"
  },
  "version": "1.0.0"
}
```

**Status Codes:**
- `200` - OK
- `503` - Service Unavailable

---

#### Статус индекса

```http
GET /api/status/{store_id}
```

**Response:**
```json
{
  "store_id": "vs_abc123xyz",
  "status": "completed",
  "progress": 100,
  "message": "Index is ready",
  "estimated_time_remaining": 0
}
```

**Possible Statuses:**
- `in_progress` - индекс строится
- `completed` - индекс готов
- `failed` - ошибка при построении
- `cancelled` - построение отменено

**Status Codes:**
- `200` - OK
- `404` - Not Found
- `500` - Internal Server Error

---

## Error Responses

Все ошибки возвращаются в следующем формате:

```json
{
  "error": "Error message",
  "details": {
    "field": "Additional information"
  },
  "timestamp": "2026-01-26T11:00:00Z"
}
```

### Common Error Codes

| Code | Description |
|------|-------------|
| 400 | Bad Request - неверные параметры запроса |
| 401 | Unauthorized - отсутствует или неверный API ключ |
| 403 | Forbidden - недостаточно прав |
| 404 | Not Found - ресурс не найден |
| 413 | Payload Too Large - файл слишком большой |
| 429 | Too Many Requests - превышен лимит запросов |
| 500 | Internal Server Error - внутренняя ошибка сервера |
| 503 | Service Unavailable - сервис недоступен |

---

## Rate Limits

| Endpoint | Limit |
|----------|-------|
| POST /api/search | 10 запросов/минуту |
| POST /api/files/upload | 5 запросов/минуту |
| POST /api/vectorstore/create | 3 запроса/минуту |
| GET endpoints | 60 запросов/минуту |

При превышении лимита возвращается:
```json
{
  "error": "Rate limit exceeded",
  "retry_after": 30
}
```

---

## Examples

### cURL Examples

#### Создать Vector Store и загрузить чанки

```bash
# 1. Создать Vector Store
curl -X POST http://localhost:8000/api/vectorstore/create \
  -H "Content-Type: application/json" \
  -d '{"name": "my_faq_store"}'

# Response: {"store_id": "vs_abc123xyz", ...}

# 2. Загрузить чанки
curl -X POST http://localhost:8000/api/files/upload-chunks \
  -F "file=@faq_chunks.jsonl" \
  -F "store_id=vs_abc123xyz"

# Response: {"file_id": "file_xyz789", ...}

# 3. Проверить статус
curl http://localhost:8000/api/status/vs_abc123xyz

# Response: {"status": "completed", ...}

# 4. Выполнить поиск
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Можно ли работать без интернета?",
    "store_id": "vs_abc123xyz",
    "top_k": 5
  }'
```

### Python Examples

```python
import requests

BASE_URL = "http://localhost:8000"

# Создать Vector Store
response = requests.post(
    f"{BASE_URL}/api/vectorstore/create",
    json={"name": "my_faq_store"}
)
store_id = response.json()["store_id"]

# Загрузить чанки
with open("faq_chunks.jsonl", "rb") as f:
    response = requests.post(
        f"{BASE_URL}/api/files/upload-chunks",
        files={"file": f},
        data={"store_id": store_id}
    )

# Дождаться готовности индекса
import time
while True:
    response = requests.get(f"{BASE_URL}/api/status/{store_id}")
    status = response.json()["status"]
    if status == "completed":
        break
    time.sleep(5)

# Выполнить поиск
response = requests.post(
    f"{BASE_URL}/api/search",
    json={
        "query": "Можно ли работать без интернета?",
        "store_id": store_id,
        "top_k": 5
    }
)
result = response.json()
print(f"Answer: {result['answer']}")
for chunk in result['chunks']:
    print(f"- [{chunk['score']:.3f}] {chunk['id']}")
```

### JavaScript Examples

```javascript
const BASE_URL = 'http://localhost:8000';

// Создать Vector Store
const createStore = async (name) => {
    const response = await fetch(`${BASE_URL}/api/vectorstore/create`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({name})
    });
    return await response.json();
};

// Загрузить чанки
const uploadChunks = async (file, storeId) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('store_id', storeId);
    
    const response = await fetch(`${BASE_URL}/api/files/upload-chunks`, {
        method: 'POST',
        body: formData
    });
    return await response.json();
};

// Дождаться готовности
const waitForReady = async (storeId) => {
    while (true) {
        const response = await fetch(`${BASE_URL}/api/status/${storeId}`);
        const data = await response.json();
        if (data.status === 'completed') break;
        await new Promise(resolve => setTimeout(resolve, 5000));
    }
};

// Выполнить поиск
const search = async (query, storeId) => {
    const response = await fetch(`${BASE_URL}/api/search`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({query, store_id: storeId, top_k: 5})
    });
    return await response.json();
};

// Использование
(async () => {
    const store = await createStore('my_faq_store');
    const file = document.getElementById('fileInput').files[0];
    await uploadChunks(file, store.store_id);
    await waitForReady(store.store_id);
    const result = await search('Можно ли работать без интернета?', store.store_id);
    console.log('Answer:', result.answer);
})();
```

---

## WebSocket API (Future)

Планируется добавить WebSocket API для real-time обновлений статуса индекса:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/status/{store_id}');

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Status update:', data.status, data.progress);
};
```

---

## Changelog

### v1.0.0 (2026-01-26)
- Initial release
- Vector Store management
- File upload (auto-chunking and custom chunks)
- Search with RAG
- Comparison mode

### Planned for v1.1.0
- Batch file upload
- Search history
- Export results
- WebSocket support