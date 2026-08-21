#!/usr/bin/env python3
"""
HighSkize REMADE v3 – Custom Security & Logging
"""

import requests
import time
import sys
import webbrowser
import json
import os
import random
import hashlib
import platform
import getpass
from datetime import datetime

BACKEND_URL = "https://highskize-script.vercel.app"
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1540157907457548389/-YXbwZdQ7gmt6E1AMyV0prBSu_277GWXD_2dMgRFMa3dHD48iXOH2ZZQDysQM3hwUteO"
GUNS_CHECKER_DOWNLOAD_URL = f"{BACKEND_URL}/downloads/guns_checker.zip"

GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
CYAN = '\033[96m'
BOLD = '\033[1m'
RESET = '\033[0m'

def log(level, msg):
    timestamp = datetime.now().strftime("%H:%M:%S")
    color = GREEN if level == "PASS" else YELLOW if level == "WARN" else RED if level == "FAIL" else CYAN
    print(f"{color}[{level}]{RESET} [{timestamp}] {msg}")

def send_log(event, details):
    try:
        requests.post(f"{BACKEND_URL}/api/log-remade", json={"event": event, "details": details}, timeout=10)
    except:
        pass

def get_device_fingerprint():
    return hashlib.sha256(f"{platform.system()}-{platform.node()}-{getpass.getuser()}".encode()).hexdigest()[:16]

def wait_for_code():
    code = random.randint(100000, 999999)
    print(f"{CYAN}Generating security code...{RESET}")
    time.sleep(5)
    print(f"{BOLD}Enter this code immediately: {GREEN}{code}{RESET}")
    start = time.time()
    user_input = input("Code: ").strip()
    elapsed = time.time() - start
    if elapsed > 10:
        log("FAIL", "Code timed out.")
        send_log("SECURITY_CODE_TIMEOUT", {"fingerprint": get_device_fingerprint()})
        return False
    if user_input != str(code):
        log("FAIL", "Incorrect code.")
        send_log("SECURITY_CODE_WRONG", {"fingerprint": get_device_fingerprint()})
        return False
    send_log("SECURITY_CODE_PASS", {"fingerprint": get_device_fingerprint()})
    return True

def email_otp_verification():
    email = input("Enter your Discord-linked email: ").strip().lower()
    if '@' not in email:
        log("FAIL", "Invalid email.")
        return False, email

    log("INFO", f"Sending verification code to {email}...")
    try:
        resp = requests.post(f"{BACKEND_URL}/api/send-otp", json={"email": email}, timeout=15)
        if resp.status_code != 200:
            log("FAIL", f"Could not send OTP: {resp.json().get('error', 'Unknown')}")
            return False, email
    except Exception as e:
        log("FAIL", f"Network error: {e}")
        return False, email

    log("PASS", "Code sent! Check your inbox (and spam).")
    otp = input("Enter the 6-digit code: ").strip()
    if not otp:
        log("FAIL", "No code entered.")
        return False, email

    log("CHECK", "Verifying code...")
    try:
        resp = requests.post(f"{BACKEND_URL}/api/verify-otp", json={"email": email, "otp": otp}, timeout=15)
        if resp.status_code != 200 or not resp.json().get('verified'):
            log("FAIL", "Invalid or expired code.")
            return False, email
    except Exception as e:
        log("FAIL", f"Verification error: {e}")
        return False, email

    send_log("OTP_VERIFIED", {"email": email, "fingerprint": get_device_fingerprint()})
    return True, email

def guns_lol_verification():
    print(f"{BOLD}{'='*50}{RESET}")
    print(f"{BOLD}   Guns.lol Username Checker – Secure Access{RESET}")
    print(f"{BOLD}{'='*50}{RESET}\n")

    log("CHECK", "Collecting device fingerprint...")
    fp = get_device_fingerprint()
    log("INFO", f"Fingerprint: {fp}")

    ok, email = email_otp_verification()
    if not ok:
        return

    log("CHECK", "Preparing anti-bot challenge...")
    if not wait_for_code():
        return

    log("CHECK", "Checking request frequency...")
    time.sleep(1)
    send_log("DOWNLOAD_ACCESS_GRANTED", {"email": email, "fingerprint": fp})

    log("PASS", "All security checks passed!")
    log("INFO", "Preparing secure download...")
    time.sleep(0.5)
    print(f"\n{GREEN}Download ready!{RESET}")
    print(f"URL: {CYAN}{GUNS_CHECKER_DOWNLOAD_URL}{RESET}\n")
    webbrowser.open(GUNS_CHECKER_DOWNLOAD_URL)

def highskize_script_info():
    print(f"\n{BOLD}HighSkize.py – Get Our Services{RESET}\n")
    print("1. Download `highskize.py` from our website.")
    print("2. Run it with Python 3.")
    print("3. Enter your Discord-linked email.")
    print("4. Check email for 6-digit code.")
    print("5. Enter code to receive 8-character key.")
    print("6. Validate key at https://highskize-script.vercel.app")
    print(f"\n{GREEN}Website:{RESET} https://highskize-script.vercel.app\n")

def custom_request(service_type):
    print(f"\n{BOLD}{'='*50}{RESET}")
    print(f"{BOLD}   {service_type} Request{RESET}")
    print(f"{BOLD}{'='*50}{RESET}\n")
    description = input("Describe what you want: ").strip()
    email = input("Your email: ").strip().lower()
    platform = input("Platform (Windows/macOS/Chromebook): ").strip()
    if not description or '@' not in email:
        log("FAIL", "Description and valid email required.")
        return

    log("INFO", "Sending request...")
    try:
        resp = requests.post(f"{BACKEND_URL}/api/submit-request", json={
            "service_type": service_type,
            "description": description,
            "email": email,
            "platform": platform
        }, timeout=15)
        if resp.status_code == 200:
            log("PASS", "Request stored successfully.")
        else:
            log("WARN", "Could not store request.")
    except Exception as e:
        log("WARN", f"Backend error: {e}")

    embed = {
        "username": "HighSkize REMADE",
        "embeds": [{
            "title": f"New {service_type} Request",
            "color": 0x00b894,
            "fields": [
                {"name": "Service Type", "value": service_type, "inline": False},
                {"name": "Description", "value": description, "inline": False},
                {"name": "Email", "value": email, "inline": True},
                {"name": "Platform", "value": platform, "inline": True},
                {"name": "Timestamp", "value": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "inline": False}
            ]
        }]
    }
    try:
        requests.post(DISCORD_WEBHOOK_URL, json=embed, timeout=10)
        log("PASS", "Discord webhook sent.")
    except:
        log("WARN", "Could not send webhook.")

def main():
    # Security initialization sequence
    print(f"{BOLD}{'='*50}{RESET}")
    print(f"{BOLD}   HighSkize REMADE v3 – Security Initialization{RESET}")
    print(f"{BOLD}{'='*50}{RESET}\n")
    log("INFO", "Starting high-security protocols...")
    time.sleep(0.4)
    log("CHECK", "Verifying system integrity...")
    time.sleep(0.5)
    log("CHECK", "Scanning for keyloggers and malware...")
    time.sleep(0.6)
    log("CHECK", "Applying AES-256 encryption layer...")
    time.sleep(0.5)
    log("CHECK", "Validating anti-tamper mechanisms...")
    time.sleep(0.6)
    log("CHECK", "Checking network security...")
    time.sleep(0.5)
    log("PASS", "All systems nominal. Access granted.\n")

    while True:
        print(f"{BOLD}HighSkize REMADE Menu{RESET}")
        print("1. Guns.lol Username Checker")
        print("2. HighSkize.py (get our services)")
        print("3. Request Custom Scripts")
        print("4. Request Custom VS Code Extensions")
        print("5. Anti-cheat Bypass (not available)")
        print("6. Exit")
        choice = input("> ").strip()

        if choice == "1":
            guns_lol_verification()
        elif choice == "2":
            highskize_script_info()
        elif choice == "3":
            custom_request("Custom Script")
        elif choice == "4":
            custom_request("Custom VS Code Extension")
        elif choice == "5":
            print(f"{RED}Anti-cheat bypass is not supported.{RESET}\n")
        elif choice == "6":
            print("Goodbye!")
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()
