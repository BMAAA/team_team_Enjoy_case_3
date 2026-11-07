# Data dictionary — кейс 3
## Как заполнять
Четыре файла: merchants (4 колонки), employees (4), payments (7), qr_links (7).
Два образца — по merchants и payments. Остальные — заполни сам.



## Образец merchants (не трогать)
|Файл|Поле|Тип|Обяз.|Ограничение|Пример|Код ошибки|
|---|---|---|---|---|---|---|
|merchants|merchant_id|string|да|m_NNN|m_001|—|
|merchants|name|string|да|1–100 символов|Вкус-Сервис Тверская|—|
|merchants|status|enum|да|ACTIVE/BLOCKED/PENDING|ACTIVE|MERCHANT_BLOCKED|
|merchants|description|string|нет|0–200|Ресторан сети|—|

## Образец payments (не трогать)
|Файл|Поле|Тип|Обяз.|Ограничение|Пример|Код ошибки|
|---|---|---|---|---|---|---|
|payments|payment_id|string|да|p_NNNN|p_0001|—|
|payments|amount|decimal|да|> 0, ≤ 1 000 000|637.00|AMOUNT_OUT_OF_RANGE|
|payments|tip|decimal|да|≥ 0, ≤ amount × 0.5|63.70|TIP_OUT_OF_RANGE|
|payments|status|enum|да|CREATED/PENDING/SUCCESS/DECLINED/CANCELED|SUCCESS|—|

## Твоя таблица — employees
|Поле|Тип|Обяз.|Ограничение|Пример|Код ошибки|
|---|---|---|---|---|---|
|employee_id|string|да|`e_NNN`, уникальный|e_001|—|
|merchant_id|string|да|`m_NNN`(FK → `merchants`)|m_001|MERCHANT_BLOCKED|
|name|string|да|1-100 символов|Иванов И.|—|
|payment_details|string|да|`****NNNN`, уникальный|****1001|—|

## Твоя таблица — qr_links
|Поле|Тип|Обяз.|Ограничение|Пример|Код ошибки|
|---|---|---|---|---|---|
|qr_id|string|да|`qr_NNN`, уникальный|qr_001|INVALID_QR|
|merchant_id|string|да|`m_001` (FK→`merchants.merchant_id`)|m_001|MERCHANT_BLOCKED|
|employee_id|string|да|`e_001` (FK→`employees.employee_id`) , принадлежит `merchant_id`|e_001|INVALID_QR|
|receipt_id|string|да|`r_NNNN`, уникален в рамках мерчанта|r_1001|RECEIPT_MISMATCH|
|nonce|string|да|6 hex символов, криптостойкий одноразовый токен|c82561|QR_USED|
|exp|datetima (ISO 8601)|да|Формат `ISO 8601`|2025-11-01T23:59:00Z|QR_EXPIRED|
|signature|string|да|Первые 16 hex от `HMAC-SHA256`|68d0f361ac38c12b|INVALID_QR|

## Критерий приёмки
- [ ] Все 4 файла описаны (22 колонки)
- [ ] Для каждого поля указан тип и ограничение
- [ ] Для полей с валидацией — код ошибки из 08_errors.md
- [ ] Пример взят из реального CSV
- [ ] payment_details — только маска (****NNNN)

## Подсказки
- payment_details — это реквизиты для выплат, не для оплаты.
- nonce — одноразовый, 6 hex.
- exp — время, после которого QR недействителен (обычно 24 ч).
- signature — HMAC-SHA256, 16 hex.
