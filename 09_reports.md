## Отчётность — кейс 3
## 1. Отчёт по мерчанту (ОБРАЗЕЦ)
**Endpoint:** `GET /api/v1/reports/tips?merchant_id=m_001&from=2025-11-01&to=2025-11-30`

**Метрики:**

|Метрика|Формула|Пример|
|-|-|-|
|tips_total|sum(`tip`)|550.00|
|payments_count|count(`payments`)|4|
|avg_tip_pct|avg(`tip` / `amount` * 100)|10.0|
|success_rate|count(`SUCCESS`) / count(*)|0.75|

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
**Endpoint:** `GET /api/v1/reports/tips?employee_id=e_001&from=2025-11-01&to=2025-11-30`

**Метрики (заполни формулы):**

|Метрика|Формула|Пример|
|-|-|-|
|tips_total|sum(`tip`) выбранного официанта за период|83.60|
|payments_count|count(`payments`) выбранного официанта за период|2|
|avg_tip_amount|sum(`tip`) / count(`payments`) выбранного официанта за период|41.80|
|top_day|день с максимальным sum(`tip`) выбранного официанта за период|2025-11-03|

**Пример ответа (заполни):**

```json
{
  "employee_id": "e_001",
  "period": "2025-11",
  "tips_total": 83.60,
  "payments_count": 2,
  "avg_tip_amount": 41.80,
  "top_day": "2025-11-03"
}
```

## 3. Отчёт по дням (заполни)
**Endpoint:** `GET /api/v1/reports/tips/daily?merchant_id=m_001&from=2025-11-01&to=2025-11-30`

**Метрики:**

|Метрика|Формула|Пример|
|-|-|-|
|date|—|2025-11-01|
|tips_total|sum(`tip`) выбранного мерчанта за день|245.90|
|payments_count|count(payments) выбранного мерчанта за день|3|
|avg_tip_pct|avg(`tip` / `amount` × 100) выбранного мерчанта за день|10.00|

**Пример ответа (заполни):**

```json
{
  "merchant_id": "m_001",
  "daily": [
    {"date": "2025-11-01", "tips_total": 245.90, "payments_count": 3, "avg_tip_pct": 10.00},
    {"date": "2025-11-03", "tips_total": 365.30, "payments_count": 3, "avg_tip_pct": 10.00}
  ]
}
```

## 4. Критерий приёмки
* [ ] Три разреза: мерчант, официант, по дням
* [ ] Метрики с формулами
* [ ] Примеры ответов в JSON
* [ ] Данные сходятся с `payments.csv`
* [ ] Указаны endpoint'ы
