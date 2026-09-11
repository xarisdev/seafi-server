## API Docs (v1)
Базовый URL: `https://seafi.xaris.space/api`
Версия API: `/v1`

### Работа с пользователями
<details>
<summary><code>POST /user</code> - регистрация</summary>

**Параметры JSON:**
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