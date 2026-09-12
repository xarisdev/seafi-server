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