#!/usr/bin/env python3
from dotenv import load_dotenv # pyright: ignore[reportMissingImports]

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


def check_exp(qr):
    exp = qr["exp"].strip()
    if exp.endswith("Z"):
        exp = exp[:-1] + "+00:00"
    
    try:
        exp_dt = datetime.datetime.fromisoformat(exp)
    except ValueError:
        return False
    
    if exp_dt.tzinfo is None:
        exp_dt = exp_dt.replace(tzinfo=datetime.timezone.utc)
    return exp_dt >= datetime.datetime.now(datetime.timezone.utc)


def calc_amounts(base, pct):
    tip = round(base * (pct / 100), 2)

    return tip, round(base + tip, 2)


def emulate_gateway(qr_id, nonce):
    h = int(hashlib.md5((qr_id + nonce).encode()).hexdigest(), 16) % 10
    print(h)
    if h <= 7:
        return "SUCCESS", None
    if h == 8:
        return "DECLINED", "CARD_DECLINED"
    if h == 9:
        return "TIMEOUT", "GATEWAY_TIMEOUT"
    return "UNKNOWN", "NOT_IMPLEMENTED"


def write_payment(payment):
    new_file = not os.path.exists(OUT_CSV)
    with open(OUT_CSV, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=OUT_FIELDS)
        if new_file:
            w.writeheader()
        w.writerow(payment)


def main():
    if len(sys.argv) < 2:
        print("Использование: python 04_прототип.py 04_примеры/qr.json")
        sys.exit(1)

    with open(sys.argv[1], encoding="utf-8") as f:
        req = json.load(f)

    qr_id = req["qr_id"]
    base = float(req.get("base_amount", 1500))
    pct = float(req.get("tip_pct", 10))

    qr = load_qr(qr_id)
    if not qr:
        print(json.dumps({"status": "ERROR", "error_code": "INVALID_QR"}, ensure_ascii=False))
        sys.exit(2)

    if not verify_signature(qr):
        print(json.dumps({"status": "ERROR", "error_code": "INVALID_QR"}, ensure_ascii=False))
        sys.exit(2)

    """
    С ТЕКУЩЕЙ ТАБЛИЦОЙ НЕ ИСПОЛЬЗУЕМ - ВРЕМЯ ДАВНО ИСТЕКЛО
    if not check_exp(qr):
        print(json.dumps({"status": "ERROR", "error_code": "QR_EXPIRED"}, ensure_ascii=False))
        sys.exit(2)
    """

    tip, total = calc_amounts(base, pct)
    status, error = emulate_gateway(qr_id, qr["nonce"])

    if not(0 < base <= 100000):
        print(json.dumps({"status": "ERROR", "error_code": "AMOUNT_OUT_OF_RANGE"}, ensure_ascii=False))
        sys.exit(2)

    if not(0 <= pct <= 50):
        print(json.dumps({"status": "ERROR", "error_code": "TIP_OUT_OF_RANGE"}, ensure_ascii=False))
        sys.exit(2)

    if not(0 <= total <= 2000000):
            print(json.dumps({"status": "ERROR", "error_code": "AMOUNT_OUT_OF_RANGE"}, ensure_ascii=False))
            sys.exit(2)
    
        
    payment = {
        "payment_id": f"p_demo_{qr_id[-3:]}",
        "merchant_id": qr["merchant_id"],
        "employee_id": qr["employee_id"],
        "amount": f"{base:.2f}",
        "tip": f"{tip:.2f}",
        "status": status,
        "timestamp": "2025-11-01T18:00:00Z",
    }
    write_payment(payment)

    print(json.dumps({
        "payment_id": payment["payment_id"],
        "status": status,
        "amount_total": total,
        "tip_amount": tip,
        "error_code": error,
    }, ensure_ascii=False, indent=2))

    sys.exit(0 if status == "SUCCESS" else 1)


if __name__ == "__main__":
    main()