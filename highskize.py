#!/usr/bin/env python3
"""
HighSkize Productions - Key Generator & Manager
Secured by SKIZE
"""

import requests
import webbrowser
import time
import os
import sys
import json
import argparse
from datetime import datetime, timedelta

BACKEND_URL = os.environ.get("HIGHSKIZE_BACKEND", "https://highskize-script.vercel.app")
SESSION_FILE = os.path.expanduser("~/.highskize_session")
MAX_SESSION_HOURS = 24
KEY_DISPLAY_SECONDS = 15

class C:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    RESET = '\033[0m'

def supports_color():
    return hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()

if not supports_color():
    C.GREEN = C.YELLOW = C.RED = C.CYAN = C.BOLD = C.DIM = C.RESET = ''

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_status(msg, status='info'):
    if status == 'success':
        prefix = f"{C.GREEN}[+]"
    elif status == 'error':
        prefix = f"{C.RED}[!]"
    elif status == 'warning':
        prefix = f"{C.YELLOW}[*]"
    else:
        prefix = f"{C.CYAN}[i]"
    print(f"{prefix}{C.RESET} {msg}")

def load_session():
    if os.path.exists(SESSION_FILE):
        try:
            with open(SESSION_FILE, 'r') as f:
                data = json.load(f)
            saved_at = datetime.fromisoformat(data.get('saved_at'))
            if datetime.now() - saved_at < timedelta(hours=MAX_SESSION_HOURS):
                return data
        except:
            pass
        try:
            os.remove(SESSION_FILE)
        except:
            pass
    return None

def save_session(email):
    data = {'email': email, 'saved_at': datetime.now().isoformat()}
    with open(SESSION_FILE, 'w') as f:
        json.dump(data, f)
    os.chmod(SESSION_FILE, 0o600)

def clear_session():
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)

def send_otp(email):
    try:
        resp = requests.post(f"{BACKEND_URL}/api/send-otp", json={"email": email}, timeout=15)
        if resp.status_code == 200:
            return True, None
        else:
            try:
                error = resp.json().get('error', 'Unknown error')
            except:
                error = f"HTTP {resp.status_code}"
            return False, error
    except requests.exceptions.RequestException as e:
        return False, f"Network error: {e}"

def generate_key(email, otp):
    try:
        resp = requests.post(f"{BACKEND_URL}/api/generate-key-email", json={"email": email, "otp": otp}, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            key = data.get('key')
            remaining = data.get('remaining_keys', 'unknown')
            return True, key, remaining
        else:
            try:
                error = resp.json().get('error', 'Unknown error')
            except:
                error = f"HTTP {resp.status_code}"
            return False, None, error
    except requests.exceptions.RequestException as e:
        return False, None, f"Network error: {e}"

def check_remaining_keys(email):
    try:
        resp = requests.post(f"{BACKEND_URL}/api/remaining-keys", json={"email": email}, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            return data.get('remaining_keys', 'unknown')
        else:
            return None
    except requests.exceptions.RequestException:
        return None

def check_key(key):
    try:
        resp = requests.post(f"{BACKEND_URL}/api/check-key", json={"key": key}, timeout=15)
        if resp.status_code == 200:
            return resp.json()
        else:
            return {"error": resp.json().get('error', 'Unknown')}
    except requests.exceptions.RequestException as e:
        return {"error": f"Network error: {e}"}

def show_status():
    try:
        resp = requests.get(f"{BACKEND_URL}/api/status", timeout=15)
        if resp.status_code == 200:
            return resp.json()
        else:
            return None
    except requests.exceptions.RequestException:
        return None

def copy_to_clipboard(text):
    try:
        import pyperclip
        pyperclip.copy(text)
        return True
    except ImportError:
        return False

def display_key(key):
    clear_screen()
    print(f"{C.BOLD}{'=' * 50}{C.RESET}")
    print(f"{C.BOLD}   YOUR TOKEN: {C.GREEN}{key}{C.RESET}")
    print(f"{C.BOLD}{'=' * 50}{C.RESET}")
    print(f"\n{C.DIM}This token is valid for 15 minutes.{C.RESET}")
    if copy_to_clipboard(key):
        print(f"{C.GREEN}✔ Token copied to clipboard!{C.RESET}")
    else:
        print(f"{C.YELLOW}Copy the token above.{C.RESET}")
    print(f"\n{C.DIM}Press Enter to open the website now, or wait {KEY_DISPLAY_SECONDS} seconds...{C.RESET}")
    # Wait for Enter or timeout
    import threading
    stop_flag = threading.Event()
    def wait_enter():
        input()
        stop_flag.set()
    t = threading.Thread(target=wait_enter, daemon=True)
    t.start()
    for remaining in range(KEY_DISPLAY_SECONDS, 0, -1):
        if stop_flag.is_set():
            break
        sys.stdout.write(f"\r{C.YELLOW}Time remaining: {remaining:2d} seconds{C.RESET} ")
        sys.stdout.flush()
        time.sleep(1)
    print()
    clear_screen()
    print_status("Token display cleared. Opening website...", "success")
    webbrowser.open(f"{BACKEND_URL}")

def interactive_mode():
    clear_screen()
    print(f"{C.BOLD}{'=' * 50}{C.RESET}")
    print(f"{C.BOLD}   HighSkize Productions - Key Generator{C.RESET}")
    print(f"{C.DIM}   Secured by SKIZE{C.RESET}")
    print(f"{C.BOLD}{'=' * 50}{C.RESET}\n")

    session = load_session()
    if session:
        email = session.get('email')
        print(f"{C.CYAN}Welcome back! Saved email: {email}{C.RESET}")
        print(f"{C.DIM}(Saved for 24 hours){C.RESET}")
        use_saved = input(f"Use saved email? (Y/n): ").strip().lower()
        if use_saved in ('', 'y', 'yes'):
            email = email
        else:
            clear_session()
            email = input(f"\n{C.CYAN}Enter your Discord-linked email: {C.RESET}").strip().lower()
    else:
        email = input(f"{C.CYAN}Enter your Discord-linked email: {C.RESET}").strip().lower()

    if not email or '@' not in email:
        print_status("Invalid email.", "error")
        return

    # Show remaining keys before sending OTP
    remaining = check_remaining_keys(email)
    if remaining is not None:
        if remaining == 'infinite':
            print(f"{C.GREEN}You have INFINITE lifetime keys left!{C.RESET}")
        else:
            print(f"{C.YELLOW}You have {remaining} lifetime keys left.{C.RESET}")
    # If None, we just skip silently (no error message)

    save_session(email)

    print(f"\n{C.CYAN}Sending verification code to {email}...{C.RESET}")
    ok, err = send_otp(email)
    if not ok:
        if "Daily email sending limit reached" in err or "Too many code requests" in err:
            print_status("You've reached the email sending limit for today. Please wait and try again later.", "error")
        else:
            print_status(f"Failed to send code: {err}", "error")
        return
    print_status("Code sent! Check your inbox (and spam folder).", "success")

    code = input(f"{C.CYAN}Enter the 6-digit code: {C.RESET}").strip()
    if not code:
        print_status("No code entered.", "error")
        return

    print(f"\n{C.CYAN}Verifying code...{C.RESET}")
    ok, key, remaining = generate_key(email, code)
    if not ok:
        print_status(f"Error: {remaining}", "error")
        return

    remaining_msg = "infinite" if remaining == 'infinite' else str(remaining)
    print_status(f"Key generated successfully. Lifetime keys remaining: {remaining_msg}", "success")

    display_key(key)

def main():
    parser = argparse.ArgumentParser(description="HighSkize Productions Key Manager (Secured by SKIZE)")
    parser.add_argument('--check', metavar='KEY', help='Check if a key is valid')
    parser.add_argument('--resend', metavar='EMAIL', help='Resend OTP to an email')
    parser.add_argument('--status', action='store_true', help='Show system status')
    args = parser.parse_args()

    if args.check:
        data = check_key(args.check)
        if 'error' in data:
            print_status(data['error'], 'error')
        else:
            if data.get('valid'):
                print_status("Key is valid!", "success")
                print(f"  Expires at: {data.get('expires_at')}")
                print(f"  Email: {data.get('email', 'N/A')}")
                print(f"  IP: {data.get('ip', 'N/A')}")
            else:
                print_status("Key is not valid.", "error")
                if data.get('used'):
                    print("  Reason: Already used.")
                else:
                    print("  Reason: Expired or not found.")
        return

    if args.resend:
        print(f"Sending OTP to {args.resend}...")
        ok, err = send_otp(args.resend)
        if ok:
            print_status("Code sent successfully.", "success")
        else:
            if "Daily email sending limit reached" in err or "Too many code requests" in err:
                print_status("You've reached the email sending limit for today. Please wait and try again later.", "error")
            else:
                print_status(f"Failed: {err}", "error")
        return

    if args.status:
        data = show_status()
        if data:
            print(f"{C.BOLD}System Status:{C.RESET}")
            print(f"  Active Chats: {data.get('active_chats', 0)}")
            print(f"  Total Keys Generated: {data.get('total_keys', 0)}")
        else:
            print_status("Could not fetch status.", "error")
        return

    interactive_mode()

if __name__ == "__main__":
    main()
