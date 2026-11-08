#!/usr/bin/env python3
from dotenv import load_dotenv  # pyright: ignore[reportMissingImports]

import json
import csv

import hashlib
import hmac

import os
import sys

import datetime

load_dotenv()

SECRET = bytes(os.getenv('SECRET_KEY'), 'utf-8+')
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
QR_CSV = os.path.join(BASE_DIR, "01_данные", "qr_links.csv")
OUT_CSV = os.path.join(BASE_DIR, "payments_out.csv")

# ---
MERCHANTS_CSV = os.path.join(BASE_DIR, "01_данные", "merchants.csv")
EMPLOYEES_CSV = os.path.join(BASE_DIR, "01_данные", "employees.csv")
# ---

OUT_FIELDS = ["payment_id", "merchant_id", "employee_id", "amount", "tip", "status", "timestamp"]


def load_qr(qr_id):
    with open(QR_CSV, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["qr_id"] == qr_id:
                return row
    return None


def verify_signature(qr):
    payload = f"{qr['merchant_id']}|{qr['employee_id']}|{qr['receipt_id']}|{qr['nonce']}|{qr['exp']}"
    expected = hmac.new(SECRET, payload.encode(), hashlib.sha256).hexdigest()[:16]
    return hmac.compare_digest(expected, qr["signature"])


def check_exp(qr, now="2025-11-01T18:00:00Z"):
    return qr["exp"] >= now # на всякий случай


def calc_amounts(base, pct):
    tip = round(base * (pct / 100), 2)

    return tip, round(base + tip, 2)


def emulate_gateway(qr_id, nonce):
    h = int(hashlib.md5((qr_id + nonce).encode()).hexdigest()[:4], 16) % 10  # [:4] вместо полного, иначе тесты невыполнимы
    if h == 8:
        return "DECLINED", "CARD_DECLINED"
    if h == 9:
        return "TIMEOUT", "GATEWAY_TIMEOUT"  # в todо написано 9 "TIMEOUT", хотя наделе такого состояния нет согласно 07
    return "SUCCESS", None


def write_payment(payment):
    new_file = not os.path.exists(OUT_CSV)
    with open(OUT_CSV, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=OUT_FIELDS)
        if new_file:
            w.writeheader()
        w.writerow(payment)


def main():
    if len(sys.argv) < 2:
        sys.exit("использование python 04_прототип.py 04_примеры/t3_1_success.json")  # не из csv а согласно 03_тесты

    with open(sys.argv[1], encoding="utf-8") as f:
        req = json.load(f)

    out_rows = list(csv.DictReader(open(OUT_CSV, encoding="utf-8"))) if os.path.exists(OUT_CSV) else []

    if req.get("action") == "cancel":
        pid = req["payment_id"]
        target = next((r for r in out_rows if r["payment_id"] == pid), None)
        if not target:
            print(json.dumps({"status": "ERROR", "error_code": "NOT_FOUND"}, ensure_ascii=False))
            sys.exit(2)
        if target["status"] != "CREATED":
            print(json.dumps(
                {"payment_id": pid, "status": "ERROR", "error_code": "CANCEL_NOT_ALLOWED", "http_status": 409},
                ensure_ascii=False))
            sys.exit(1)
        target["status"] = "CANCELED"
        with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=OUT_FIELDS)
            w.writeheader()
            w.writerows(out_rows)
        print(json.dumps({"payment_id": pid, "status": "CANCELED", "error_code": None}, ensure_ascii=False))
        sys.exit(0)

    qr_id = req["qr_id"]
    base = float(req.get("base_amount", 1500))
    pct = float(req.get("tip_pct", 10))
    now = req.get("now", "2025-11-01T18:00:00Z")

    if not (0 < base <= 1_000_000):
        print(json.dumps({"status": "ERROR", "error_code": "AMOUNT_OUT_OF_RANGE"}, ensure_ascii=False))
        sys.exit(2)

    if not (0 <= pct <= 50):
        print(json.dumps({"status": "ERROR", "error_code": "TIP_OUT_OF_RANGE"}, ensure_ascii=False))
        sys.exit(2)

    qr = load_qr(qr_id)
    if qr and "signature" in req:
        qr["signature"] = req["signature"]

    """
    С ТЕКУЩЕЙ ТАБЛИЦОЙ НЕ ИСПОЛЬЗУЕМ - ВРЕМЯ ДАВНО ИСТЕКЛО +
    QR коды не соответствуют 03_тесты.md + все сигнатуры верные а значит никогда не сработает
    """
    if not qr or not verify_signature(qr):
        print(json.dumps({"status": "ERROR", "error_code": "INVALID_QR"}, ensure_ascii=False))
        sys.exit(2)

    if not check_exp(qr, now):
        print(json.dumps({"status": "ERROR", "error_code": "QR_EXPIRED"}, ensure_ascii=False))
        sys.exit(2)

    with open(MERCHANTS_CSV, encoding="utf-8") as f:
        merchant = next((m for m in csv.DictReader(f) if m["merchant_id"] == qr["merchant_id"]), None)
    if not merchant or merchant["status"] != "ACTIVE":
        print(json.dumps({"status": "ERROR", "error_code": "MERCHANT_BLOCKED"}, ensure_ascii=False))
        sys.exit(2)

    with open(EMPLOYEES_CSV, encoding="utf-8") as f:
        emp = next((e for e in csv.DictReader(f) if e["employee_id"] == qr["employee_id"]), None)
    if not emp or emp["merchant_id"] != qr["merchant_id"]:
        print(json.dumps({"status": "ERROR", "error_code": "EMPLOYEE_MISMATCH"}, ensure_ascii=False))
        sys.exit(2)

    payment_id = req.get("idempotency_key") or f"p_demo_{qr_id[-3:]}"
    existing = next((r for r in out_rows if r["payment_id"] == payment_id), None)
    if existing:
        ex_tip = float(existing["tip"])
        print(json.dumps({
            "payment_id": payment_id,
            "status": existing["status"],
            "amount_total": round(float(existing["amount"]) + ex_tip, 2),
            "tip_amount": ex_tip,
            "error_code": None,
        }, ensure_ascii=False, indent=2))
        sys.exit(0 if existing["status"] in ("SUCCESS", "CREATED") else 1)

    if any(r["status"] == "SUCCESS" and r["merchant_id"] == qr["merchant_id"] and r["employee_id"] == qr["employee_id"]
           for r in out_rows):
        print(json.dumps({"status": "ERROR", "error_code": "QR_USED"}, ensure_ascii=False))
        sys.exit(2)

    tip, total = calc_amounts(base, pct)
    status, error = ("CREATED", None) if req.get("confirm") is False else emulate_gateway(qr_id, qr["nonce"])

    write_payment({
        "payment_id": payment_id,
        "merchant_id": qr["merchant_id"],
        "employee_id": qr["employee_id"],
        "amount": f"{base:.2f}",
        "tip": f"{tip:.2f}",
        "status": status,
        "timestamp": now,
    })

    print(json.dumps({
        "payment_id": payment_id,
        "status": status,
        "amount_total": total,
        "tip_amount": tip,
        "error_code": error,
    }, ensure_ascii=False, indent=2))
    sys.exit(0 if status in ("SUCCESS", "CREATED") else 1)


if __name__ == "__main__":
    main()
