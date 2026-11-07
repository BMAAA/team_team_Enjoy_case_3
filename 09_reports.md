## Отчётность — кейс 3

## 1. Отчёт по мерчанту (ОБРАЗЕЦ)

**Endpoint:** `GET /api/v1/reports/tips?merchant_id=m_001&from=2025-11-01&to=2025-11-30`

**Метрики:**

|Метрика|Формула|Пример|
|-|-|-|
|tips_total|sum(tip)|550.00|
|payments_count|count(payments)|4|
|avg_tip_pct|avg(tip / amount × 100)|10.0|
|success_rate|count(SUCCESS) / count(*)|0.75|

**Пример ответа:**

```json
{
  "merchant_id": "m_001",
  "period": "2025-11",
  "tips_total": 550.00,
  "payments_count": 4,
  "avg_tip_pct": 10.0,
  "success_rate": 0.75
}
```

## 2. Отчёт по официанту (заполни)

**Endpoint:** `GET /api/v1/reports/tips?employee_id=e_001&from=...&to=...`

**Метрики (заполни формулы):**

|Метрика|Формула|Пример|
|-|-|-|
|tips_total|?|?|
|payments_count|?|?|
|avg_tip_amount|?|?|
|top_day|?|?|

**Пример ответа (заполни):**

```json
{
  "employee_id": "?",
  "period": "?",
  "tips_total": ?,
  "payments_count": ?,
  "avg_tip_amount": ?,
  "top_day": "?"
}
```

## 3. Отчёт по дням (заполни)

**Endpoint:** `GET /api/v1/reports/tips/daily?merchant_id=m_001&from=...&to=...`

**Метрики:**

|Метрика|Формула|Пример|
|-|-|-|
|date|—|2025-11-01|
|tips_total|sum(tip) за день|200.00|
|payments_count|count за день|2|
|avg_tip_pct|avg(tip/amount) за день|8.5|

**Пример ответа (заполни):**

```json
{
  "merchant_id": "m_001",
  "daily": [
    {"date": "2025-11-01", "tips_total": 200.00, "payments_count": 2, "avg_tip_pct": 8.5},
    {"date": "2025-11-02", "tips_total": 150.00, "payments_count": 1, "avg_tip_pct": 10.0}
  ]
}
```

## 4. Критерий приёмки

* [ ] Три разреза: мерчант, официант, по дням
* [ ] Метрики с формулами
* [ ] Примеры ответов в JSON
* [ ] Данные сходятся с `payments.csv`
* [ ] Указаны endpoint'ы

```


