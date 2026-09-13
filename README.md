## API Docs (v1)
Базовый URL: `https://seafi.xaris.space/api`
Версия API: `/v1`

### Работа с пользователями
<details>
<summary><code>POST /user</code> - Регистрация</summary>

**Параметры запроса:**
| Название | Тип | Описание |
|----------|-----|----------|

**Параметры Headers:**
```json
{
    "Authorization": "secret_key"
}
```
**Параметры Body:**
```json
{
    "username": "str",
    "telegram_id": "int",
    "secret_key": "str"
}
```
**Ответ JSON:**
```json
{
    "status": "success"
}
```
</details>

<details>
<summary><code>GET /user/{telegram_id}</code> - Информация о пользователе</summary>

**Параметры запроса:**
| Название | Тип | Описание |
|----------|-----|----------|
| `telegram_id` | `int` | ID пользователя в телеграме |

**Параметры Headers:**
```json
{
    "Authorization": "secret_key"
}
```
**Параметры Body:**
```json
{}
```
**Ответ JSON:**
```json
{
    "id": "user.id",
    "telegram_id": "user.telegram_id",
    "username": "user.username",
    "created_at": "user.created_at.isoformat()",
    "subscription_id": "user.subscription_id"
}
```
</details>

### Работа с фильтрами
<details>
<summary><code>POST /filter/new</code> - Создание фильтра</summary>

Параметры запроса:
| Название | Тип | Описание |
|----------|-----|----------|

Параметры Headers:
```json
{
    "Authorization": "secret_key"
}
```
Параметры Body:
```json
{
    "telegram_id": "int",
    "price_min": "int",
    "price_max": "int",
    "owner": "str"
}
```
Ответ JSON:
```json
{
    "status": "success"
}
```
</details>

### Lava.top
<details>
<summary><code>GET /payments/products?telegram_id=int</code> - Получение списка продуктов (администратор)</summary>

Параметры запроса:
| Название | Тип | Описание |
|----------|-----|----------|
| `telegram_id` | `int` | Идентификатор администратора |

Параметры Headers:
```json
{
    "Authorization": "secret_key"
}
```
Параметры Body:
```json
{

}
```
Ответ JSON:
```json
{
    "status": "success",
    "products": [
        {
            "id": "id",
            "title": "Title of the product",
            "offer_id": "offerId",
            "offer_name": "Name of the offer"
        }
    ]
}
```
</details>

<details>
<summary><code>POST /payments/create-link</code> - Создание ссылки на оплату</summary>

Параметры запроса:
| Название | Тип | Описание |
|----------|-----|----------|

Параметры Headers:
```json
{
    "Authorization": "secret_key"
}
```
Параметры Body:
```json
{
    "telegram_id": "int",
    "comment": "str"
}
```
Ответ JSON:
```json
{
    "status": "success",
    "invoice": {
        "id": "str",
        "status": "str",
        "amountTotal": {
            "currency": "str",
            "amount": "int"
        },
        "paymentUrl": "str"
    }
}
```
</details>