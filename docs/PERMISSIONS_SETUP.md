# Настройка прав доступа для AI Search Demo

## Проблема

При запуске приложения возникает ошибка:
```
Permission CREATE denied to folder. 
You need the ai.assistants.editor, editor, or admin role
```

## Решение

### Вариант 1: Через веб-консоль Yandex Cloud

1. Откройте [консоль Yandex Cloud](https://console.cloud.yandex.ru/)
2. Выберите ваш каталог
3. Перейдите в раздел "Управление доступом" (Access Management)
4. Найдите ваш сервисный аккаунт
5. Нажмите "Назначить роли"
6. Добавьте роль `ai.assistants.editor`
7. Сохраните изменения

### Вариант 2: Через YC CLI

```bash
# Получить ID сервисного аккаунта
yc iam service-account list

# Назначить роль ai.assistants.editor
yc resource-manager folder add-access-binding <FOLDER_ID> \
  --role ai.assistants.editor \
  --service-account-id <SERVICE_ACCOUNT_ID>
```

### Вариант 3: Создать новый API ключ с нужными правами

```bash
# 1. Создать новый сервисный аккаунт
yc iam service-account create --name ai-search-demo

# 2. Назначить роль
yc resource-manager folder add-access-binding <FOLDER_ID> \
  --role ai.assistants.editor \
  --service-account-name ai-search-demo

# 3. Создать API ключ
yc iam api-key create \
  --service-account-name ai-search-demo \
  --description "AI Search Demo"

# 4. Скопировать secret и обновить .env файл
```

## Необходимые роли

Для работы приложения нужна одна из ролей:
- `ai.assistants.editor` (рекомендуется) - доступ к AI Assistants API
- `editor` - полный доступ к каталогу
- `admin` - административный доступ

## Проверка прав

После назначения роли подождите 1-2 минуты и перезапустите приложение:

```bash
cd backend
pkill -f uvicorn
source .venv/bin/activate
python -m uvicorn main:app --reload
```

## Дополнительная информация

- [Управление доступом в Yandex Cloud](https://yandex.cloud/ru/docs/iam/concepts/access-control/)
- [Роли для AI Studio](https://yandex.cloud/ru/docs/ai-studio/security/)