# Фильтры

Модель фильтра используется как универсальный набор параметров для поиска объявлений и передаётся парсерам.

## Параметры фильтра поиска

| Параметр | Имя | Описание | Обязательный | Тип | Допустимые значения |
| --- | --- | --- | :---: | :---: | --- |
| `city` | Город | Город для поиска объявлений. На первое время — из ограниченного списка | Нет<br>*дефолт — bishkek* | `TEXT` | `"bishkek"`<br>`"osh"` |
| `ads_type` | Тип объявления | Формат объявления: аренда / продажа | Нет<br>*дефолт — Аренда* | `TEXT` | `"rent"`<br>`"sell"` |
| `ads_owner` | Тип владельца | Формат владельца объявления: риелтор / собственник / все | Нет<br>*дефолт — `None`* | `TEXT` | `NULL`<br>`"agent"`<br>`"owner"` |
| `min_price` | Минимальная цена | Не может быть ниже нуля | Нет<br>*дефолт — `None`* | `INT` | — |
| `max_price` | Максимальная цена | Ограничение — тип `BigInteger` в PostgreSQL | Нет<br>*дефолт — `None`* | `BIGINT` | — |

---

## Вспомогательные классы

```python
class EnumFilterAdsType(str, Enum):
    RENT = "rent"
    SELL = "sell"


class EnumFilterAdsOwner(str, Enum):
    AGENT = "agent"
    OWNER = "owner"
```

---

## Общая модель

```python
class Filter(Base):
    __tablename__ = "filters"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), unique=True)

    city: Mapped[str] = mapped_column(String, default="bishkek")
    
    ads_type: Mapped[Optional[EnumFilterAdsType]] = mapped_column(String, default=EnumFilterAdsType.RENT)
    ads_owner: Mapped[Optional[EnumFilterAdsOwner]] = mapped_column(String, nullable=True)

    min_price: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    max_price: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
```

---

## Общие методы

```python
class FilterCreate(BaseModel):
    user_id: int

class FilterUpdate(BaseModel):
    city: Optional[str] = None
    
    ads_type: Optional[EnumFilterAdsType] = None
    ads_owner: Optional[EnumFilterAdsOwner] = None

    min_price: Optional[int] = None
    max_price: Optional[int] = None

class FilterRead(BaseModel):
    id: int
    user_id: int

    city: str
    ads_type: EnumFilterAdsType
    ads_owner: EnumFilterAdsOwner | None
    min_price: int | None
    max_price: int | None
```

---

## Поведение, ИОФ

1. Парсер забирает информацию о фильтре.
2. Строит и отправляет запрос.
3. Получает ответ.
4. Отдаёт отдельному сервису `services.ads_handler` на обработку вместе с информацией о фильтре.

> **Связанные материалы**
>
> Отдельно об ИОФ, очередях и агентах:  
> [Очереди и агенты](../arc/queue%20and%20agents.md)

### Проверка срока действия подписки

Чтобы сервер не продолжал работу с фильтрами, у чьих подписок истёк срок действия, была добавлена связь с моделью `User`.

1. `TaskManager` берёт задачу из очереди.
2. Проверяет, не истёк ли срок подписки (`User → Subscription → expires_at`):
   - **Если подписка закончилась** — фильтр не возвращается в очередь, задача завершается.
   - **Если подписка активна** — фильтр передаётся агенту.

> Такая проверка не является основной и служит вспомогательным механизмом защиты от лишних срабатываний. В конечном счёте это дешевле, чем дать фильтру полностью отработать и отсеять его на этапе отправки результата. Однако последняя проверка также будет проводиться.

### Жизненный цикл фильтра

- Для каждого пользователя может существовать **только один фильтр**. Повторно создать или удалить его нельзя.
- Создание фильтра **напрямую не связано** с конкретной подпиской: связь устанавливается через пользователя, поэтому фильтру нет необходимости обновлять свои данные при истечении или замене подписки.
- Фильтр **не помещается в очередь автоматически** и не удаляется из неё — для этого используется отдельный запрос.

---

## Управление фильтром через API

> Доступ к API определяется посредством единственной доверенной клиентской машины с `X-Api-Key`.

### Создание фильтра

```http
POST /api/v1/filters?id={user_id}              -> Filter [200 OK] | NotFoundError [404 Not Found]
POST /api/v1/filters?telegram_id={telegram_id} -> Filter [200 OK] | NotFoundError [404 Not Found]
```

### Получение фильтра пользователя

```http
# С помощью Filter.id
GET /api/v1/filters/{id}                           -> Filter [200 OK] | NotFoundError [404 Not Found]

# Через пользователя
GET /api/v1/filters/user?id={user_id}              -> Filter [200 OK] | NotFoundError [404 Not Found]
GET /api/v1/filters/user?telegram_id={telegram_id} -> Filter [200 OK] | NotFoundError [404 Not Found]
```

### Изменение фильтра пользователя

> Модель для изменения указана выше в документации.

```http
PATCH /api/v1/filters/{id} -> [204 No Content] | NotFoundError [404 Not Found]
```

### Активация и отключение фильтра

```http
POST /api/v1/filters/{id}/activate   -> [204 No Content] | [409 Conflict] | NotFoundError [404 Not Found]
POST /api/v1/filters/{id}/deactivate -> [204 No Content] | [409 Conflict] | NotFoundError [404 Not Found]
```

**Поведение `activate`:**

| Ситуация | Ответ |
| --- | --- |
| Фильтр не был активен — активируется | `204 No Content` |
| Фильтр уже был активен | `409 Conflict` |
| Фильтра с таким идентификатором не существует | `404 Not Found` |

**Поведение `deactivate`:**

| Ситуация | Ответ |
| --- | --- |
| Фильтр был активен — отключается | `204 No Content` |
| Фильтр не был активен | `409 Conflict` |
| Фильтра с таким идентификатором не существует | `404 Not Found` |