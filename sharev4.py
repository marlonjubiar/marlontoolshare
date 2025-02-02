#!/usr/bin/env python3
import os
import sys
import time

def install_packages():
    required_packages = [
        'requests',
        'rich',
        'pytz',
        'pathlib'
    ]
    
    print("\n[!] Checking and installing required packages...")
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            print(f"[!] Installing {package}...")
            os.system(f"pip install {package}")
            print(f"[✓] {package} installed successfully!")
    
    print("[✓] All required packages installed!\n")
    time.sleep(1)
    os.system('clear' if os.name == 'posix' else 'cls')

# Install required packages before importing
if __name__ == "__main__":
    install_packages()

import threading
import requests
import json
from datetime import datetime, timedelta
from rich.console import Console
from rich import print
from rich.panel import Panel
import re
import pytz
from pathlib import Path
import uuid
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
import subprocess

console = Console()
os.system('clear' if os.name == 'posix' else 'cls')

# File paths
COOKIE_PATH = '/storage/emulated/0/cookie.txt'
ACCOUNTS_PATH = '/storage/emulated/0/accounts.txt'

config = {
    'post': '',
    'cookies': [],
    'total_shares': 0,
    'target_shares': 0
}

#-----------------------------[APPROVAL KEY]-----------------------------------#
def get_key():
    a = str(os.geteuid())
    b = str(os.geteuid())
    try:
        build = subprocess.check_output('getprop ro.build.id',shell=True).decode('utf-8').replace('\n','')
    except:
        build = "UNKNOWN"
    x = (a+build+b).upper().replace(".","")
    return "X".join(x)[15:]

def check_approval(key):
    try:
        resp = requests.get("https://pastebin.com/raw/3ntzWKg4").text
        if key in resp:
            return True
        else:
            return False
    except:
        return False

#-----------------------------[COOKIE CHECKER]-----------------------------------#
def get_cookie_info(cookie):
    try:
        session = requests.Session()
        headers = {
            'cookie': cookie,
            'user-agent': generate_user_agent()
        }
        session.headers.update(headers)
        
        # First check if token can be retrieved
        try:
            response = session.get('https://business.facebook.com/content_management')
            if 'EAAG' not in response.text:
                return None
        except:
            return None
            
        # Then check profile access
        try:
            response = session.get('https://www.facebook.com/me', allow_redirects=False)
            if response.status_code != 302:
                return None
                
            profile_url = response.headers.get('location')
            if not profile_url or 'checkpoint' in profile_url:
                return None
                
            user_id = profile_url.split('/')[-1] if profile_url else None
            if not user_id or user_id == 'login':
                return None
                
            response = session.get(f'https://www.facebook.com/{user_id}')
            if 'checkpoint' in response.text or 'login' in response.url:
                return None
                
            username = re.search(r'<title>(.*?)</title>', response.text)
            username = username.group(1).replace(' | Facebook', '') if username else None
            
            if username:
                # Final validation - try to get access token
                try:
                    token_response = session.get('https://business.facebook.com/content_management')
                    if 'EAAG' in token_response.text:
                        return {
                            'uid': user_id,
                            'name': username,
                            'status': 'Active'
                        }
                except:
                    return None
    except:
        pass
    return None

def validate_cookies():
    valid_cookies = []
    dead_cookies = []
    
    try:
        if os.path.exists(COOKIE_PATH):
            with open(COOKIE_PATH, 'r') as f:
                cookies = [line.strip() for line in f if line.strip()]
                
            print(Panel("[white]Validating cookies...", 
                title="[bright_white]>> [Validation] <<",
                width=65,
                style="bold bright_white"
            ))
                
            for i, cookie in enumerate(cookies, 1):
                print(f"[cyan]Checking cookie {i}...")
                info = get_cookie_info(cookie)
                
                if info:
                    print(f"[green]Cookie {i} is valid - {info['name']}")
                    valid_cookies.append(cookie)
                else:
                    print(f"[red]Cookie {i} is dead/blocked")
                    dead_cookies.append(cookie)
                
            if dead_cookies:
                print(Panel(f"""[yellow]⚡[white] Found dead/blocked cookies
[yellow]⚡[white] Valid: [green]{len(valid_cookies)}
[yellow]⚡[white] Dead: [red]{len(dead_cookies)}

[white]Removing dead cookies...""",
                    title="[bright_white]>> [Cleanup] <<",
                    width=65,
                    style="bold bright_white"
                ))
                
                with open(COOKIE_PATH, 'w') as f:
                    for cookie in valid_cookies:
                        f.write(cookie + '\n')
                        
            return valid_cookies
                    
    except Exception as e:
        print(f"[red]Error validating cookies: {str(e)}")
    
    return valid_cookies

#-----------------------------[CREATE REQUIRED FILES]-----------------------------------#
def create_required_files():
    os.makedirs(os.path.dirname(COOKIE_PATH), exist_ok=True)
    if not os.path.exists(COOKIE_PATH):
        with open(COOKIE_PATH, 'w') as f:
            f.write("")
            
    # Create accounts.txt with example if not exists
    if not os.path.exists(ACCOUNTS_PATH):
        with open(ACCOUNTS_PATH, 'w') as f:
            f.write("# Format your accounts like this:\n")
            f.write("e : email@example.com\n")
            f.write("p : password123\n")
            f.write("e : another@email.com\n")
            f.write("p : anotherpass\n")

#-----------------------------[COOKIE GETTER]-----------------------------------#
def generate_user_agent():
    amazon = ["E6653", "E6633", "E6853", "E6833", "F3111", "F3111 F3113", "F5122", 
              "F3111 F3113", "SO-04H", "F3212", "F3311", "F8331", "SO-02J", "G3116", "G8232"]
    
    return f"Mozilla/5.0 (Linux; Android {random.randint(4,13)}; {random.choice(amazon)}; Windows 10 Mobile) AppleWebKit/537.36 (KHTML, like Gecko) Kiwi Chrome/{random.randint(84,106)}.0.{random.randint(4200,4900)}.{random.randint(40,140)} Mobile Safari/537.36"

def get_lsd_token(session):
    try:
        git_fb = session.get("https://touch.facebook.com/pages/create/?ref_type=registration_form", timeout=30).text
        return re.search(r'"lsd":"(.*?)"', str(git_fb)).group(1)
    except Exception as e:
        return None

def get_cookie(uid, pww, ua=None):
    try:
        if not ua:
            ua = generate_user_agent()
        
        session = requests.Session()
        lsd = get_lsd_token(session)
        
        if not lsd:
            return None
            
        _data = {
            'lsd': lsd,
            'email': uid,
            'encpass': '#PWD_BROWSER:0:' + str(int(time.time())) + ':' + pww
        }
        
        _header = {
            'authority': 'touch.facebook.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'cache-control': 'max-age=0',
            'content-type': 'application/x-www-form-urlencoded',
            'dpr': '1.8937500715255737',
            'origin': 'https://touch.facebook.com',
            'referer': 'https://touch.facebook.com/',
            'sec-ch-prefers-color-scheme': 'dark',
            'sec-ch-ua': '"Not-A.Brand";v="99", "Chromium";v="124"',
            'sec-ch-ua-full-version-list': '"Not-A.Brand";v="99.0.0.0", "Chromium";v="124.0.6327.4"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-model': '""',
            'sec-ch-ua-platform': '"Android"',
            'sec-ch-ua-platform-version': '""',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': ua,
            'viewport-width': '980'
        }
        
        url = 'https://touch.facebook.com/login/device-based/regular/login/?login_attempt=1&lwv=110'
        response = session.post(url, data=_data, headers=_header, allow_redirects=False, timeout=30)
        
        login_cookies = session.cookies.get_dict()
        
        if "c_user" in login_cookies:
            cookie = ";".join([f"{key}={value}" for key, value in login_cookies.items()])
            # Validate the cookie before returning
            if get_cookie_info(cookie):
                return cookie
        return None
            
    except:
        return None

def bulk_cookie_getter():
    try:
        banner()
        print(Panel("[white]Starting Bulk Cookie Getter...", 
            title="[bright_white]>> [Cookie Getter] <<",
            width=65,
            style="bold bright_white"
        ))

        if not os.path.exists(ACCOUNTS_PATH):
            print(Panel("[red]accounts.txt not found!\n[white]Creating example accounts.txt...", 
                title="[bright_white]>> [Error] <<",
                width=65,
                style="bold bright_white"
            ))
            create_required_files()
            return
            
        with open(ACCOUNTS_PATH, "r") as f:
            lines = f.readlines()
            
        # Process lines in pairs
        accounts = []
        current_email = None
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
                
            if line.startswith("e :"):
                current_email = line.split("e :")[1].strip()
            elif line.startswith("p :") and current_email:
                password = line.split("p :")[1].strip()
                accounts.append((current_email, password))
                current_email = None
            
        if not accounts:
            print(Panel("[red]No valid accounts found in accounts.txt!\n[white]Please use format:\n[cyan]e : email@example.com\np : password123", 
                title="[bright_white]>> [Error] <<",
                width=65,
                style="bold bright_white"
            ))
            return
            
        print(Panel(f"[green]Loaded {len(accounts)} accounts", 
            title="[bright_white]>> [Info] <<",
            width=65,
            style="bold bright_white"
        ))
        
        success = 0
        failed = 0
        valid_cookies = []
        
        # Process accounts
        with ThreadPoolExecutor(max_workers=25) as executor:
            futures = []
            for email, password in accounts:
                print(f"[cyan]Trying[/cyan] {email}")
                futures.append(
                    executor.submit(get_cookie, email, password)
                )
            
            for future in as_completed(futures):
                cookie = future.result()
                if cookie:
                    valid_cookies.append(cookie)
                    print(f"[green]Success - Cookie Retrieved")
                    success += 1
                else:
                    print(f"[red]Failed - Login Failed")
                    failed += 1
        
        # Write all successful cookies at once
        if valid_cookies:
            with open(COOKIE_PATH, "a") as f:
                for cookie in valid_cookies:
                    f.write(cookie + "\n")
                
        print(Panel(f"""[yellow]⚡[white] Total Accounts: [cyan]{len(accounts)}
[yellow]⚡[white] Success: [green]{success}
[yellow]⚡[white] Failed: [red]{failed}
[yellow]⚡[white] Cookies saved to: [cyan]{COOKIE_PATH}""",
            title="[bright_white]>> [Results] <<",
            width=65,
            style="bold bright_white"
        ))
                
    except Exception as e:
        print(Panel(f"[red]Error: {str(e)}", 
            title="[bright_white]>> [Error] <<",
            width=65,
            style="bold bright_white"
        ))

def loading_animation(duration: int, message: str):
    frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    end_time = time.time() + duration
    i = 0
    while time.time() < end_time:
        print(f"\r{frames[i]} {message}", end="")
        time.sleep(0.1)
        i = (i + 1) % len(frames)
    print("\r" + " " * (len(message) + 2))

def update_tool():
    try:
        print(Panel("[white]Checking for updates...", 
            title="[bright_white]>> [Update Check] <<",
            width=65,
            style="bold bright_white"
        ))
        
        result = subprocess.run(['git', 'pull'], capture_output=True, text=True)
        
        if "Already up to date" in result.stdout:
            print(Panel("[green]Tool is already up to date!", 
                title="[bright_white]>> [Update Status] <<",
                width=65,
                style="bold bright_white"
            ))
            time.sleep(2)
        else:
            print(Panel("[green]Tool updated successfully!\n[yellow]Please restart the script.", 
                title="[bright_white]>> [Update Status] <<",
                width=65,
                style="bold bright_white"
            ))
            sys.exit(0)
    except Exception as e:
        print(Panel(f"[red]Update failed: {str(e)}", 
            title="[bright_white]>> [Error] <<",
            width=65,
            style="bold bright_white"
        ))
        time.sleep(2)

def banner():
    os.system('clear' if os.name == 'posix' else 'cls')
    key = get_key()
    cookie_count = 0
    active_cookies = 0
    
    try:
        if os.path.exists(COOKIE_PATH):
            with open(COOKIE_PATH, 'r') as f:
                cookies = [line.strip() for line in f if line.strip()]
                cookie_count = len(cookies)
                
                for cookie in cookies:
                    if get_cookie_info(cookie):
                        active_cookies += 1
    except:
        pass
    
    print(Panel(
        r"""[red]●[yellow] ●[green] ●
[cyan]██████╗░██╗░░░██╗░█████╗░
[cyan]██╔══██╗╚██╗░██╔╝██╔══██╗
[cyan]██████╔╝░╚████╔╝░██║░░██║
[cyan]██╔══██╗░░╚██╔╝░░██║░░██║
[cyan]██║░░██║░░░██║░░░╚█████╔╝
[cyan]╚═╝░░╚═╝░░░╚═╝░░░░╚════╝░""",
        title="[bright_white] SPAMSHARE [green]●[yellow] Active [/]",
        width=65,
        style="bold bright_white",
    ))
    
    print(Panel(
        f"""[yellow]⚡[cyan] Tool     : [green]SpamShare[/]
[yellow]⚡[cyan] Version  : [green]1.0.0[/]
[yellow]⚡[cyan] Dev      : [green]Ryo Evisu[/]
[yellow]⚡[cyan] Status   : [red]Premium[/]""",
        title="[white on red] INFORMATION [/]",
        width=65,
        style="bold bright_white",
    ))
    
    print(Panel(
        f"""[yellow]⚡[cyan] Key      : [cyan]{key}[/]
[yellow]⚡[cyan] Premium  : [green]True[/]
[yellow]⚡[cyan] Expired  : [red]Never[/]
[yellow]⚡[cyan] Version  : [green]Latest[/]""",
        title="[white on red] KEY INFO [/]",
        width=65,
        style="bold bright_white",
    ))

    print(Panel(
        f"""[yellow]⚡[cyan] Total Cookies : [green]{cookie_count}[/]
[yellow]⚡[cyan] Active Cookies: [green]{active_cookies}[/]
[yellow]⚡[cyan] Dead Cookies  : [red]{cookie_count - active_cookies}[/]
[yellow]⚡[cyan] Cookie Path   : [cyan]{COOKIE_PATH}[/]""",
        title="[white on red] COOKIE INFO [/]",
        width=65,
        style="bold bright_white",
    ))

def show_main_menu():
    print(Panel("""[1] Start Share Process
[2] Bulk Cookie Getter
[3] Update Tool
[4] Exit""",
        title="[bright_white]>> [Main Menu] <<",
        width=65,
        style="bold bright_white"
    ))
    
    choice = console.input("[bright_white]Enter choice (1-4): ")
    
    if choice == "2":
        bulk_cookie_getter()
        return True
    elif choice == "3":
        update_tool()
        return True
    elif choice == "4":
        return False
    elif choice == "1":
        main()
        return True
    return True

class FacebookShare:
    def __init__(self, cookie, post_link, share_count, cookie_index, stats):
        self.cookie = cookie
        self.post_link = post_link
        self.share_count = share_count
        self.cookie_index = cookie_index
        self.stats = stats
        self.session = requests.Session()
        self.headers = {
            'user-agent': generate_user_agent(),
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-User': '?1',
            'Sec-Fetch-Dest': 'document',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en-US,en;q=0.9',
            'cookie': self.cookie
        }
        self.session.headers.update(self.headers)

    def get_token(self):
        try:
            response = self.session.get('https://business.facebook.com/content_management', timeout=15)
            token_match = re.search('EAAG\w+', response.text)
            if token_match:
                return token_match.group()
            return None
        except Exception as e:
            print(f"Error getting token for cookie {self.cookie_index + 1}: {str(e)}")
            return None

    def remove_cookie(self):
        try:
            with open(COOKIE_PATH, 'r') as f:
                cookies = f.readlines()
            
            with open(COOKIE_PATH, 'w') as f:
                for cookie in cookies:
                    if cookie.strip() != self.cookie:
                        f.write(cookie)
            
            print(f"[red]Removed blocked/failed cookie {self.cookie_index + 1}")
        except:
            pass

    def share_post(self):
        token = self.get_token()
        if not token:
            self.stats.update_failed(self.cookie_index)
            self.remove_cookie()
            return

        self.session.headers.update({
            'accept-encoding': 'gzip, deflate',
            'host': 'graph.facebook.com'
        })

        count = 0
        while count < self.share_count:
            try:
                post_data = {
                    'privacy': '{"value":"EVERYONE"}',
                    'message': '',
                    'link': f'https://m.facebook.com/{self.post_link}',
                    'access_token': token
                }
                response = self.session.post('https://graph.facebook.com/v18.0/me/feed', data=post_data, timeout=15)
                data = response.json()
                
                if 'id' in data:
                    count += 1
                    self.stats.update_success(self.cookie_index)
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    print(f"[cyan][{timestamp}][/cyan][green] Share {count}/{self.share_count} completed for Cookie {self.cookie_index + 1}")
                else:
                    print(f"Cookie {self.cookie_index + 1} is blocked or invalid!")
                    self.stats.update_failed(self.cookie_index)
                    self.remove_cookie()
                    break
                time.sleep(1)  # Add small delay between shares
                    
            except Exception as e:
                print(f"Error sharing post with cookie {self.cookie_index + 1}: {str(e)}")
                self.stats.update_failed(self.cookie_index)
                self.remove_cookie()
                break

class ShareStats:
    def __init__(self):
        self.success_count = 0
        self.failed_count = 0
        self.lock = threading.Lock()
        self.cookie_stats = {}

    def update_success(self, cookie_index):
        with self.lock:
            self.success_count += 1
            if cookie_index not in self.cookie_stats:
                self.cookie_stats[cookie_index] = {"success": 0, "failed": 0}
            self.cookie_stats[cookie_index]["success"] += 1

    def update_failed(self, cookie_index):
        with self.lock:
            self.failed_count += 1
            if cookie_index not in self.cookie_stats:
                self.cookie_stats[cookie_index] = {"success": 0, "failed": 0}
            self.cookie_stats[cookie_index]["failed"] += 1

def load_cookies():
    try:
        if not os.path.exists(COOKIE_PATH):
            os.makedirs(os.path.dirname(COOKIE_PATH), exist_ok=True)
            with open(COOKIE_PATH, 'w') as f:
                f.write("")
            console.print(f"[green]Created empty cookie file at {COOKIE_PATH}")
            console.print("[yellow]Please add your cookies to the file and run the script again")
            return None
            
        with open(COOKIE_PATH, 'r') as f:
            cookies = [line.strip() for line in f if line.strip()]
        
        if not cookies:
            console.print("[yellow]No cookies found in cookie.txt")
            console.print("[yellow]Use Bulk Cookie Getter or add cookies manually")
            return None
            
        console.print(f"[green]Successfully loaded {len(cookies)} cookies")
        return cookies
    except Exception as e:
        console.print(f"[red]Error loading cookies: {str(e)}")
        return None

def main():
    try:
        banner()
        
        # Validate cookies first
        valid_cookies = validate_cookies()
        if not valid_cookies:
            print(Panel("[red]No valid cookies found. Please add new cookies.", 
                title="[bright_white]>> [Error] <<",
                width=65,
                style="bold bright_white"
            ))
            return

        config['cookies'] = valid_cookies
        
        print(Panel("[white]Enter Post Link", 
            title="[bright_white]>> [Post Configuration] <<",
            width=65,
            style="bold bright_white",
            subtitle="╭─────",
            subtitle_align="left"
        ))
        config['post'] = console.input("[bright_white]   ╰─> ")
        banner()

        print(Panel("[white]Enter shares per cookie (1-1000)", 
            title="[bright_white]>> [Share Configuration] <<",
            width=65,
            style="bold bright_white",
            subtitle="╭─────",
            subtitle_align="left"
        ))
        share_count = int(console.input("[bright_white]   ╰─> "))
        banner()

        print(Panel(f"""[yellow]⚡[white] Post Link: [cyan]{config['post']}
[yellow]⚡[white] Cookies: [cyan]{len(config['cookies'])}
[yellow]⚡[white] Shares per cookie: [cyan]{share_count}
[yellow]⚡[white] Total target shares: [cyan]{share_count * len(config['cookies'])}

[white]Press Enter to start...""",
            title="[bright_white]>> [Configuration Summary] <<",
            width=65,
            style="bold bright_white",
            subtitle="╭─────",
            subtitle_align="left"
        ))
        console.input("[bright_white]   ╰─> ")
        banner()

        print(Panel("[green]Starting share process...", 
            title="[bright_white]>> [Process Started] <<",
            width=65,
            style="bold bright_white"
        ))
        
        stats = ShareStats()
        threads = []
        
        for i, cookie in enumerate(config['cookies']):
            share_thread = threading.Thread(
                target=FacebookShare(
                    cookie=cookie,
                    post_link=config['post'],
                    share_count=share_count,
                    cookie_index=i,
                    stats=stats
                ).share_post
            )
            threads.append(share_thread)
            share_thread.start()

        for thread in threads:
            thread.join()

        print(Panel(f"""[green]Process completed!
[yellow]⚡[white] Total shares attempted: [cyan]{stats.success_count + stats.failed_count}
[yellow]⚡[white] Successful: [green]{stats.success_count}
[yellow]⚡[white] Failed: [red]{stats.failed_count}

[white]Detailed Statistics:
{chr(10).join(f'[yellow]⚡[white] Cookie {idx + 1}: [green]{stat["success"]} success[white], [red]{stat["failed"]} failed' for idx, stat in stats.cookie_stats.items())}""",
            title="[bright_white]>> [Completed] <<",
            width=65,
            style="bold bright_white"
        ))

    except KeyboardInterrupt:
        print(Panel("[yellow]Process interrupted by user", 
            title="[bright_white]>> [Interrupted] <<",
            width=65,
            style="bold bright_white"
        ))
    except Exception as e:
        print(Panel(f"[red]Error: {str(e)}", 
            title="[bright_white]>> [Error] <<",
            width=65,
            style="bold bright_white"
        ))

def restart_script():
    print(Panel("[white]Press Enter to restart or type 'exit' to quit", 
        title="[bright_white]>> [Restart] <<",
        width=65,
        style="bold bright_white",
        subtitle="╭─────",
        subtitle_align="left"
    ))
    choice = console.input("[bright_white]   ╰─> ")
    return choice.lower() != 'exit'

if __name__ == "__main__":
    create_required_files()
    key = get_key()
    if check_approval(key):
        while True:
            banner()
            if not show_main_menu():
                print(Panel("[yellow]Thanks for using SpamShare!", 
                    title="[bright_white]>> [Goodbye] <<",
                    width=65,
                    style="bold bright_white"
                ))
                break
            if not restart_script():
                print(Panel("[yellow]Thanks for using SpamShare!", 
                    title="[bright_white]>> [Goodbye] <<",
                    width=65,
                    style="bold bright_white"
                ))
                break
            os.system('clear' if os.name == 'posix' else 'cls')
    else:
        print(Panel(f"""[red]Your key is not approved!
[yellow]⚡[white] Your Key: [cyan]{key}

[white]Contact admin for approval""", 
            title="[bright_white]>> [Key Error] <<",
            width=65,
            style="bold bright_white"
        ))
        os.system("xdg-open https://www.facebook.com/ryoevisu")
