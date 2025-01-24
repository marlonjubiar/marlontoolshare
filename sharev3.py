#!/usr/bin/env python3
import threading
import requests
import sys
import os
import time
import subprocess
from typing import List, Optional, Dict
import json
from datetime import datetime, timedelta
from rich.console import Console
from rich import print
from rich.panel import Panel
import re
import pytz
from pathlib import Path

console = Console()
os.system('clear' if os.name == 'posix' else 'cls')

# File paths
COOKIE_PATH = '/storage/emulated/0/a/cookie.txt'
GLOBAL_SHARE_COUNT_FILE = 'global_share_count.json'
KEYS_FILE = 'auth_keys.json'
LAST_KEY_FILE = 'last_key.txt'

# Default admin password hash (password: "password")
ADMIN_HASH = "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8"

config = {
    'post': '',
    'cookies': [],
    'total_shares': 0,
    'target_shares': 0
}

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

def get_system_info() -> Dict[str, str]:
    try:
        apis = [
            'https://ipapi.co/json/',
            'https://api.ipify.org?format=json',
            'https://api.myip.com'
        ]
        
        for api in apis:
            try:
                response = requests.get(api, timeout=3)
                if response.status_code == 200:
                    ip_info = response.json()
                    break
            except:
                continue
                
        if 'ip' not in ip_info:
            backup_response = requests.get('https://api64.ipify.org?format=json', timeout=3)
            ip_info = backup_response.json()
            
            location_response = requests.get(f'https://ipapi.co/{ip_info["ip"]}/json/', timeout=3)
            location_info = location_response.json()
            ip_info.update(location_info)
        
        ph_tz = pytz.timezone('Asia/Manila')
        ph_time = datetime.now(ph_tz)
        
        return {
            'ip': ip_info.get('ip', 'Checking...'),
            'region': ip_info.get('region', 'Checking...'),
            'city': ip_info.get('city', 'Checking...'),
            'time': ph_time.strftime("%I:%M:%S %p"),
            'date': ph_time.strftime("%B %d, %Y")
        }
    except:
        return {
            'ip': 'Checking...',
            'region': 'Checking...',
            'city': 'Checking...',
            'time': datetime.now().strftime("%I:%M:%S %p"),
            'date': datetime.now().strftime("%B %d, %Y")
        }

def banner():
    os.system('clear' if os.name == 'posix' else 'cls')
    sys_info = get_system_info()
    
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
        """[yellow]⚡[cyan] Tool     : [green]SpamShare[/]
[yellow]⚡[cyan] Version  : [green]1.0.0[/]
[yellow]⚡[cyan] Dev      : [green]Ryo Evisu[/]
[yellow]⚡[cyan] Status   : [red]Cookie Mode[/]""",
        title="[white on red] INFORMATION [/]",
        width=65,
        style="bold bright_white",
    ))
    
    print(Panel(
        f"""[yellow]⚡[cyan] IP       : [cyan]{sys_info['ip']}[/]
[yellow]⚡[cyan] Region   : [cyan]{sys_info['region']}[/]
[yellow]⚡[cyan] City     : [cyan]{sys_info['city']}[/]
[yellow]⚡[cyan] Time     : [cyan]{sys_info['time']}[/]
[yellow]⚡[cyan] Date     : [cyan]{sys_info['date']}[/]""",
        title="[white on red] SYSTEM INFO [/]",
        width=65,
        style="bold bright_white",
    ))

def show_main_menu():
    print(Panel("""[1] Start Share Process
[2] Update Tool
[3] Exit""",
        title="[bright_white]>> [Main Menu] <<",
        width=65,
        style="bold bright_white"
    ))
    
    choice = console.input("[bright_white]Enter choice (1-3): ")
    
    if choice == "2":
        update_tool()
        return True
    elif choice == "3":
        return False
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
            'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Mobile Safari/537.36',
            'sec-ch-ua': '"Google Chrome";v="107", "Chromium";v="107", "Not=A?Brand";v="24"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': "Android",
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'cookie': self.cookie
        }
        self.session.headers.update(self.headers)

    def get_token(self):
        try:
            response = self.session.get('https://business.facebook.com/content_management')
            token_match = re.search('EAAG(.*?)","', response.text)
            if token_match:
                return 'EAAG' + token_match.group(1)
            return None
        except Exception as e:
            print(f"Error getting token for cookie {self.cookie_index + 1}: {str(e)}")
            return None

    def share_post(self):
        token = self.get_token()
        if not token:
            self.stats.update_failed(self.cookie_index)
            return

        self.session.headers.update({
            'accept-encoding': 'gzip, deflate',
            'host': 'b-graph.facebook.com'
        })

        count = 0
        while count < self.share_count:
            try:
                response = self.session.post(
                    f'https://b-graph.facebook.com/me/feed?link=https://mbasic.facebook.com/{self.post_link}&published=0&access_token={token}'
                )
                data = response.json()
                
                if 'id' in data:
                    count += 1
                    self.stats.update_success(self.cookie_index)
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    print(f"[cyan][{timestamp}][/cyan][green] Share {count}/{self.share_count} completed for Cookie {self.cookie_index + 1}")
                else:
                    print(f"Cookie {self.cookie_index + 1} is blocked or invalid!")
                    self.stats.update_failed(self.cookie_index)
                    break
                    
            except Exception as e:
                print(f"Error sharing post with cookie {self.cookie_index + 1}: {str(e)}")
                self.stats.update_failed(self.cookie_index)
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
        cookie_file = Path(COOKIE_PATH)
        if cookie_file.exists():
            with open(cookie_file, 'r') as f:
                cookies = [line.strip() for line in f if line.strip()]
            console.print(f"[green]Successfully loaded {len(cookies)} cookies from {COOKIE_PATH}")
            return cookies
        else:
            console.print(f"[red]Cookie file not found at {COOKIE_PATH}")
            console.print("[yellow]Creating directory structure...")
            os.makedirs(os.path.dirname(COOKIE_PATH), exist_ok=True)
            with open(cookie_file, 'w') as f:
                f.write("")
            console.print(f"[green]Created empty cookie file at {COOKIE_PATH}")
            console.print("[yellow]Please add your cookies to the file and run the script again")
            return None
    except Exception as e:
        console.print(f"[red]Error loading cookies: {str(e)}")
        return None

def main():
    try:
        banner()
        
        config['cookies'] = load_cookies()
        if not config['cookies']:
            return

        print(Panel("[white]Loading cookies...", 
            title="[bright_white]>> [Process] <<",
            width=65,
            style="bold bright_white"
        ))
        loading_animation(2, "Processing cookies...")
        print(Panel(f"""[green]Cookies loaded successfully!
[yellow]⚡[white] Total cookies: [cyan]{len(config['cookies'])}""",
            title="[bright_white]>> [Success] <<",
            width=65,
            style="bold bright_white"
        ))
        time.sleep(1)
        banner()

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
    while True:
        banner()
        if not show_main_menu():
            print(Panel("[yellow]Thanks for using SpamShare!", 
                title="[bright_white]>> [Goodbye] <<",
                width=65,
                style="bold bright_white"
            ))
            break
            
        main()
        if not restart_script():
            print(Panel("[yellow]Thanks for using SpamShare!", 
                title="[bright_white]>> [Goodbye] <<",
                width=65,
                style="bold bright_white"
            ))
            break
        os.system('clear' if os.name == 'posix' else 'cls')
