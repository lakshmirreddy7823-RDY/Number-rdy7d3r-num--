#!/usr/bin/env python3
"""
============================================
  AADHAR INFOR AND NUM INFO  -  OSINT TOOL
============================================
Developer : @Rdy7d3r
Modules:
  1. Aadhar Info   -> leakinfo.pro aadhar.php
  2. Number Info   -> leakinfo.pro number.php

Usage:
  python3 Aadhar-number.py              (interactive menu)
  python3 Aadhar-number.py -a <aadhar>  (aadhaar lookup)
  python3 Aadhar-number.py -n <number>  (number lookup)
  python3 Aadhar-number.py -f <file> -m 1|2  (bulk mode)
"""

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime

try:
    import requests
except ImportError:
    print("[!] 'requests' not found. Install it:  pip install requests")
    sys.exit(1)


AADHAR_API = "https://leakinfo.pro/api/aadhar.php"
NUMBER_API = "https://leakinfo.pro/api/number.php"
AADHAR_KEY = "ak_81d2a92a3aa5d6fac24a85986cd735fe9648bf65"
NUMBER_KEY = "ak_7631a0a14df5441c1f9fede3f1851312446e48cd"
TIMEOUT = 25
OUTPUT_DIR = "results"



class C:
    RED     = "\033[1;31m"
    GREEN   = "\033[1;32m"
    YELLOW  = "\033[1;33m"
    CYAN    = "\033[1;36m"
    WHITE   = "\033[1;37m"
    MAGENTA = "\033[1;35m"
    RESET   = "\033[0m"

BANNER = f"""{C.RED}
███╗   ██╗██╗   ██╗███╗   ███╗██████╗ ███████╗██████╗ ██████╗ ██████╗
████╗  ██║██║   ██║████╗ ████║██╔══██╗██╔════╝██╔══██╗██╔══██╗██╔═══██╗
██╔██╗ ██║██║   ██║██╔████╔██║██████╔╝█████╗  ██████╔╝██████╔╝██║   ██║
██║╚██╗██║██║   ██║██║╚██╔╝██║██╔═══╝ ██╔══╝  ██╔═══╝ ██╔══██╗██║   ██║
██║ ╚████║╚██████╔╝██║ ╚═╝ ██║██║     ███████╗██║     ██████╔╝╚██████╔╝
╚═╝  ╚═══╝ ╚═════╝ ╚═╝     ╚═╝╚═╝     ╚══════╝╚═╝     ╚═════╝  ╚═════╝
{C.YELLOW}
  ╔══════════════════════════════════════════════════════╗
  ║{C.WHITE}          A A D H A R   I N F O   &   N U M           {C.YELLOW}║
  ║{C.WHITE}                 I N F O   T O O L                    {C.YELLOW}║
  ╠══════════════════════════════════════════════════════╣
  ║{C.MAGENTA}   [01] Aadhar Lookup      [03] Bulk Aadhar File     {C.YELLOW}║
  ║{C.MAGENTA}   [02] Number Lookup      [04] Bulk Number File     {C.YELLOW}║
  ╚══════════════════════════════════════════════════════╝{C.GREEN}
         Developer  :{C.WHITE} @Rdy7d3r{C.GREEN}   |   Version :{C.WHITE} 1.0{C.GREEN}
         Telegram   :{C.WHITE} http://t.me/Fuckkke{C.GREEN} | Termux/Windows/Linux
{C.RESET}"""

def clean(text):
    """Normalize nulls / addresses."""
    if text is None:
        return "-"
    if isinstance(text, str):
        text = text.replace("!", ", ").strip()
        return text if text else "-"
    return str(text)


def pretty_print(rec, idx=None):
    tag = f"[{idx}] " if idx is not None else ""
    line = "-" * 60
    print(f"\n{line}")
    for k, v in rec.items():
        print(f"  {tag}{k:<18}: {clean(v)}")
    print(line)


def save(filename, data):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    path = os.path.join(OUTPUT_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"\n[+] Results saved -> {path}")


def api_get(url, params, retries=3):
    """GET with automatic retry on server errors (502/503/504/429)."""
    headers = {"User-Agent": "Mozilla/5.0"}
    for attempt in range(1, retries + 1):
        try:
            r = requests.get(url, params=params, timeout=TIMEOUT, headers=headers)
            r.raise_for_status()
            return r.json()
        except requests.exceptions.HTTPError as e:
            code = e.response.status_code if e.response is not None else "?"
            if code in (502, 503, 504, 429) and attempt < retries:
                wait = 5 * attempt
                print(f"[!] Server error ({code}). Retry {attempt}/{retries} in {wait}s...")
                time.sleep(wait)
                continue
            print(f"[!] API error {code} — leakinfo.pro is down or rate-limiting you. Try again later.")
        except requests.exceptions.Timeout:
            print("[!] Request timed out.")
            if attempt < retries:
                time.sleep(5)
                continue
        except requests.exceptions.RequestException as e:
            print(f"[!] Request failed: {e}")
        except json.JSONDecodeError:
            print("[!] Invalid JSON received (API may be down or rate-limited).")
        break
    return None

def aadhar_lookup(aadhar):
    aadhar = aadhar.strip().replace(" ", "")
    if not re.fullmatch(r"\d{12}", aadhar):
        print("[!] Invalid Aadhaar number (must be 12 digits).")
        return None
    print(f"\n[*] Querying Aadhaar info for: {aadhar}")
    data = api_get(AADHAR_API, {"key": AADHAR_KEY, "aadhar": aadhar})
    if not data:
        return None

    if not data.get("success"):
        print("[!] API returned no success flag. Raw response:")
        print(json.dumps(data, indent=2))
        return None

    info = data.get("data", {}).get("aadhaar_info", {})
    records = info.get("records", [])
    total = info.get("total_records", len(records))

    if not records:
        print("[!] No records found for this Aadhaar.")
        return None

    print(f"[+] Found {total} record(s):\n")
    for i, rec in enumerate(records, 1):
        pretty_print({
            "Name":        rec.get("name"),
            "Father Name": rec.get("fname"),
            "Mobile":      rec.get("mobile"),
            "Alt Mobile":  rec.get("alt"),
            "Aadhaar":     rec.get("id"),
            "Address":     rec.get("address"),
        }, i)

    save(f"aadhar_{aadhar}_{datetime.now():%Y%m%d_%H%M%S}.json", data)
    return records

def number_lookup(number):
    number = number.strip().replace(" ", "")
    if not re.fullmatch(r"[6-9]\d{9}", number):
        print("[!] Invalid Indian mobile number (10 digits, starts 6-9).")
        return None
    print(f"\n[*] Querying number info for: {number}")
    data = api_get(NUMBER_API, {"key": NUMBER_KEY, "number": number})
    if not data:
        return None

    # Number API returns records keyed "0","1",...
    records = [v for k, v in sorted(data.items()) if isinstance(v, dict)]
    if not records:
        print("[!] No records found for this number. Raw response:")
        print(json.dumps(data, indent=2))
        return None

    print(f"[+] Found {len(records)} record(s):\n")
    for i, rec in enumerate(records, 1):
        pretty_print({
            "Name":          rec.get("name"),
            "Father Name":   rec.get("father name"),
            "Mobile":        rec.get("mobile"),
            "Alt Mobile":    rec.get("alternative mobile"),
            "Circle / SIM":  rec.get("circle/sim"),
            "ID Number":     rec.get("id number"),
            "Address":       rec.get("address"),
        }, i)

    save(f"number_{number}_{datetime.now():%Y%m%d_%H%M%S}.json", data)
    return records


def bulk_run(mode, filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            targets = [ln.strip() for ln in f if ln.strip()]
    except FileNotFoundError:
        print(f"[!] File not found: {filepath}")
        return
    print(f"[*] Bulk mode: {len(targets)} target(s)")
    ok = 0
    for i, t in enumerate(targets, 1):
        print(f"\n=== Target {i}/{len(targets)} ===")
        result = aadhar_lookup(t) if mode == "1" else number_lookup(t)
        if result:
            ok += 1
        time.sleep(2)  # be gentle with the API
    print(f"\n[*] Bulk finished. Success: {ok}/{len(targets)}")

def menu():
    while True:
        print(BANNER)
        print("  [1] Aadhar Info Lookup")
        print("  [2] Number Info Lookup")
        print("  [3] Bulk Aadhar Lookup (file)")
        print("  [4] Bulk Number Lookup (file)")
        print("  [0] Exit")
        choice = input("\n  choice > ").strip()
        if choice == "1":
            aadhar_lookup(input("  Enter Aadhaar number > "))
        elif choice == "2":
            number_lookup(input("  Enter mobile number > "))
        elif choice == "3":
            bulk_run("1", input("  File path > "))
        elif choice == "4":
            bulk_run("2", input("  File path > "))
        elif choice == "0":
            print("[*] Bye.")
            break
        else:
            print("[!] Invalid choice.")
        input("\n[press Enter to continue]")


def main():

    if os.name == "nt":
        os.system("")
    parser = argparse.ArgumentParser(description="Aadhar Infor and Num Info - OSINT Tool")
    parser.add_argument("-a", "--aadhar", help="Aadhaar number (12 digits)")
    parser.add_argument("-n", "--number", help="Mobile number (10 digits)")
    parser.add_argument("-f", "--file", help="Bulk file (use with -m)")
    parser.add_argument("-m", "--mode", choices=["1", "2"], help="Bulk mode: 1=aadhar 2=number")
    args = parser.parse_args()

    if args.file and args.mode:
        bulk_run(args.mode, args.file)
    elif args.aadhar:
        aadhar_lookup(args.aadhar)
    elif args.number:
        number_lookup(args.number)
    else:
        menu()

if __name__ == "__main__":
    main()
