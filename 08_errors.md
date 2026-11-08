# ER-модель — кейс 3 «Онлайн-чаевые»

## 1. Сущности 
| Сущность | Что хранит | Зачем |
|---|---|---|
| Merchant | merchant_id, name, status, description | справочник мерчантов |
| Employee | employee_id, merchant_id, name, payment_details | сотрудники ресторана и маски реквизитов выплат |
| QR | qr_id, merchant_id, employee_id, receipt_id, nonce, exp, signature | подписанная ссылка на конкретный чек |
| Payment | payment_id, qr_id, merchant_id, employee_id, amount, tip, status, timestamp, idempotency_key, client_session_id | попытка платежа и защита от повторного создания |
| Report | report_id, merchant_id, period, tips_total и расчётные показатели | отчёт по заведению за период |
| AuditEvent | event_id, payment_id, qr_id, action, from_status, to_status, amount_total, actor, at, error_code | история действий и ошибок |

## 2. Атрибуты
### 2.1. Merchant (ОБРАЗЕЦ — не трогать)
|Поле|Тип|PK/FK|Обяз.|Ограничение|
|-|-|-|-|-|
|merchant_id|string|**PK**|да|`m_NNN`|
|name|string|—|да|1–100|
|status|enum|—|да|ACTIVE/BLOCKED/PENDING|
|description|string|—|нет|0–200|

### 2.2. Employee 
| Поле | Тип | PK/FK | Обяз. | Ограничение |
|---|---|---|---|---|
| employee_id | string | PK | да | уникальный e_NNN |
| merchant_id | string | FK → Merchant.merchant_id | да | существующий m_NNN |
| name | string | — | да | 1–100 символов |
| payment_details | string | — | да | только ****NNNN; полные реквизиты не хранятся |

### 2.3. QR 
| Поле | Тип | PK/FK | Обяз. | Ограничение |
|---|---|---|---|---|
| qr_id | string | PK | да | уникальный qr_NNN |
| merchant_id | string | FK → Merchant.merchant_id | да | при выпуске ресторан ACTIVE |
| employee_id | string | FK → Employee.employee_id | да | сотрудник принадлежит merchant_id QR |
| receipt_id | string | — | да | r_NNNN, уникален в паре с merchant_id |
| nonce | string | — | да | 6 hex; уникален среди выпущенных QR, при коллизии генерируется заново |
| exp | datetime UTC | — | да | ISO 8601, при выпуске now + 24 часа |
| signature | string | — | да | 16 hex, усечённый HMAC-SHA256 |

### 2.4. Payment 
| Поле | Тип | PK/FK | Обяз. | Ограничение |
|---|---|---|---|---|
| payment_id | string | PK | да | уникальный p_NNNN |
| qr_id | string | FK → QR.qr_id | да для новых платежей | отсутствует в историческом payments.csv; связь старых записей нельзя считать доказанной по номеру |
| amount | decimal(12,2) | — | да | 0 < amount ≤ 1 000 000 |
| tip | decimal(12,2) | — | да | 0 ≤ tip ≤ amount × 0.5 после округления до двух знаков |
| status | enum | — | да | CREATED/PENDING/SUCCESS/DECLINED/CANCELED |
| timestamp | datetime UTC | — | да | время создания, ISO 8601 |

### 2.5. Report 
| Поле | Тип | PK/FK | Обяз. | Ограничение |
|---|---|---|---|---|
| report_id | string | PK | да при сохранении | уникальный rep_NNNN |
| merchant_id | string | FK → Merchant.merchant_id | да | существующий ресторан |
| period | string | — | да | YYYY-MM, корректный месяц |
| tips_total | decimal(12,2) | — | да | сумма чаевых SUCCESS за период, ≥ 0 |

### 2.6. AuditEvent
| Поле | Тип | PK/FK | Обяз. | Ограничение |
|---|---|---|---|---|
| event_id | string | PK | да | уникальный evt_NNNN |
| payment_id | string/null | FK → Payment.payment_id | для событий платежа | null, если запрос отклонён до создания платежа |
| action | enum | — | да | payment_created / payment_confirmed / payment_succeeded / payment_declined / payment_canceled / gateway_timeout / request_rejected |
| from_status | enum/null | — | нет | состояние Payment до события; null при создании и отказе до создания |
| to_status | enum/null | — | для событий платежа | состояние после события; null у отказа до создания |
| actor | string | — | да | system / client:<session_id> / officer:<employee_id> / merchant:<merchant_id> / admin:<id>; без ФИО и секретов |
| at | datetime UTC | — | да | момент события, ISO 8601 |

## 3. Связи 
| Связь | Тип | Обоснование |
|---|---|---|
| Merchant → Employee | 1:N | В ресторане много сотрудников; каждый сотрудник связан с одним рестораном |
| Merchant → QR | 1:N | Ресторан выпускает много QR |
| Employee → QR | 1:N | Официант выпускает QR для разных чеков |
| QR → Payment | 1:N | Возможны последовательные попытки после отказа или отмены; успешная не более одной |
| Merchant → Report | 1:N | Много периодов отчётности; каждый отчёт относится к одному ресторану |
| Payment → AuditEvent | 1:N | У платежа много событий; у события до создания платежа FK может отсутствовать |

## 4. Диаграмма (draw.io)
Диаграмма создана: [er_model.drawio](output/diagrams/er_model.drawio), [PNG](output/diagrams/er_model.png).

## 5. Критерий приёмки
[ ] 6 сущностей описаны
[ ] Для каждой сущности указаны PK/FK, типы и ограничения
[ ] Связи описаны с типом (1:N, 1:1) и обоснованием
[ ] `payment_details` — только маска `****NNNN`
[ ] `signature` — HMAC-SHA256, не plain hash
[ ] Диаграмма в draw.io с PK/FK и связями
