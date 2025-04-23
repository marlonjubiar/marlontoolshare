#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import threading
import requests
import sys
import os
import time
import subprocess
from typing import List, Optional, Dict
from datetime import datetime
from rich.console import Console
from rich import print
from rich.panel import Panel
import re
import pytz
from pathlib import Path

# Ensure the script works on Termux and Pydroid3
try:
    console = Console()
    # Try to clear screen multiple ways to ensure compatibility
    try:
        if os.name == 'posix':  # Linux/Android (Termux)
            os.system('clear')
        else:  # Windows
            os.system('cls')
    except:
        # Fallback method using ANSI escape codes
        print("\033[H\033[J", end="")
except Exception as e:
    # Fallback if rich library fails
    print(f"Warning: {str(e)}")
    print("Running in compatibility mode...")

# File paths
COOKIE_PATH = '/storage/emulated/0/a/cookie.txt'

# FREEMIUM limits
MAX_COOKIES = 5
MAX_SHARES_PER_COOKIE = 1000
MAX_TOTAL_SHARES = 5000

config = {
    'post': '',
    'post_id': '',
    'cookies': [],
    'total_shares': 0
}

class ShareStats:
    def __init__(self):
        self.success_count = 0
        self.failed_count = 0
        self.lock = threading.Lock()
        self.cookie_stats = {}
        self.start_time = time.time()
        self.total_target = 0  # Added total target attribute

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
            
    def get_elapsed_time(self):
        elapsed = int(time.time() - self.start_time)
        minutes, seconds = divmod(elapsed, 60)
        hours, minutes = divmod(minutes, 60)
        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"
            
    def get_speed(self):
        elapsed = time.time() - self.start_time
        if elapsed < 1 or self.success_count == 0:
            return "Calculating..."
        
        shares_per_second = self.success_count / elapsed
        shares_per_minute = shares_per_second * 60
        return f"{shares_per_minute:.1f}/min"

def banner():
    """Clear screen and show banner - works reliably on Termux and Pydroid3"""
    try:
        # Try multiple methods to ensure compatibility
        if os.name == 'posix':  # Linux/Android (Termux)
            os.system('clear')
        else:  # Windows
            os.system('cls')
    except:
        # Fallback method using ANSI escape codes
        print("\033[H\033[J", end="")
    
    # Get current time in Philippines timezone
    ph_tz = pytz.timezone('Asia/Manila')
    ph_time = datetime.now(ph_tz)
    
    # Single logo with simplified design (only one color)
    print(Panel(
        """[cyan]███████╗██████╗  █████╗ ███╗   ███╗
[cyan]██╔════╝██╔══██╗██╔══██╗████╗ ████║
[cyan]███████╗██████╔╝███████║██╔████╔██║
[cyan]╚════██║██╔═══╝ ██╔══██║██║╚██╔╝██║
[cyan]███████║██║     ██║  ██║██║ ╚═╝ ██║
[cyan]╚══════╝╚═╝     ╚═╝  ╚═╝╚═╝     ╚═╝""",
        title="[bright_magenta]★[/] [bold bright_yellow]KAI SPAMSHARE[/] [bright_magenta]★[/]",
        width=65,
        border_style="bold cyan",
    ))
    
    # Information panel with fixed colors for better readability
    print(Panel(
        f"""[yellow]⚡[white] Tool     : [bright_cyan]SpamShare v1.0[/]
[yellow]⚡[white] Dev      : [bright_cyan]Kai[/]
[yellow]⚡[white] Mode     : [bright_yellow]FREEMIUM[/]
[yellow]⚡[white] Status   : [bright_green]No Key Required[/]
[yellow]⚡[white] Limit    : [bright_red]{MAX_TOTAL_SHARES} shares[/]
[yellow]⚡[white] Time     : [bright_cyan]{ph_time.strftime("%I:%M:%S %p")}[/]
[yellow]⚡[white] Date     : [bright_cyan]{ph_time.strftime("%B %d, %Y")}[/]""",
        title="[white on magenta] INFORMATION [/]",
        width=65,
        border_style="bold magenta",
    ))

def auto_reset():
    """Clear screen and show banner - works reliably on Termux and Pydroid3"""
    try:
        # Try multiple methods to ensure compatibility
        if os.name == 'posix':  # Linux/Android (Termux)
            os.system('clear')
        else:  # Windows
            os.system('cls')
    except:
        # Fallback method using ANSI escape codes
        print("\033[H\033[J", end="")
    
    # Show banner
    banner()

def show_main_menu():
    print(Panel("""[1] [bold bright_green]Start Share Process[/]
[2] [bold bright_yellow]Update Tool[/]
[3] [bold bright_red]Exit[/]""",
        title="[bright_white]>> [Main Menu] <<",
        width=65,
        border_style="bold cyan"
    ))
    
    choice = console.input("[bright_white]Enter choice (1-3): ")
    
    if choice == "2":
        update_tool()
        return True
    elif choice == "3":
        return False
    return True

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

class FacebookShare:
    def __init__(self, cookie, post_id, cookie_index, stats):
        self.cookie = cookie
        self.post_id = post_id
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
        self.token = None

    def get_token(self):
        try:
            response = self.session.get('https://business.facebook.com/content_management')
            token_match = re.search('EAAG(.*?)","', response.text)
            if token_match:
                self.token = 'EAAG' + token_match.group(1)
                return True
            return False
        except Exception as e:
            print(f"[red]Error getting token for cookie {self.cookie_index + 1}: {str(e)}")
            return False

    def share_post(self):
        if not self.token and not self.get_token():
            self.stats.update_failed(self.cookie_index)
            return False

        try:
            self.session.headers.update({
                'accept-encoding': 'gzip, deflate',
                'host': 'b-graph.facebook.com'
            })
            
            response = self.session.post(
                f'https://b-graph.facebook.com/me/feed?link=https://mbasic.facebook.com/{self.post_id}&published=0&access_token={self.token}'
            )
            data = response.json()
            
            if 'id' in data:
                self.stats.update_success(self.cookie_index)
                timestamp = datetime.now().strftime("%H:%M:%S")
                current_count = self.stats.success_count
                print(f"[cyan][{timestamp}][/cyan] [green]SUCCESSFULLY SHARED[/green] {current_count}/{self.stats.total_target} [bright_yellow]POST ID: {self.post_id}[/bright_yellow]")
                return True
            else:
                self.stats.update_failed(self.cookie_index)
                return False
                
        except Exception as e:
            self.stats.update_failed(self.cookie_index)
            return False

def extract_post_id(url_or_id):
    """Extract post ID from Facebook URL or return the ID if already in correct format"""
    # If it's already just a numeric ID
    if re.match(r'^\d+$', url_or_id):
        return url_or_id
        
    # Try to extract from various Facebook URL formats
    patterns = [
        r'(?:\/posts\/|\.php\?story_fbid=|\.php\?fbid=|videos\/|photos\/)(\d+)',
        r'facebook\.com\/(?:photo\.php\?fbid=|video\.php\?v=|story\.php\?story_fbid=|permalink\.php\?story_fbid=)(\d+)',
        r'facebook\.com\/[^\/]+\/(?:posts|videos|photos)\/(\d+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url_or_id)
        if match:
            return match.group(1)
    
    # If no patterns match but it's a URL, try a more generic approach
    if "facebook.com" in url_or_id:
        # Extract any numeric sequence that could be an ID
        ids = re.findall(r'\/(\d{8,})\/?', url_or_id)
        if ids:
            return ids[0]
    
    # If all else fails, return the original input
    return url_or_id

def load_cookies():
    try:
        cookie_file = Path(COOKIE_PATH)
        if cookie_file.exists():
            with open(cookie_file, 'r') as f:
                cookies = [line.strip() for line in f if line.strip()]
            return cookies
        else:
            print(Panel(f"[red]Cookie file not found at {COOKIE_PATH}", 
                title="[bright_white]>> [Error] <<",
                width=65,
                style="bold bright_red"
            ))
            os.makedirs(os.path.dirname(COOKIE_PATH), exist_ok=True)
            with open(cookie_file, 'w') as f:
                f.write("")
            print(Panel(f"[green]Created empty cookie file at {COOKIE_PATH}\n[yellow]Please add your cookies to the file and run the script again", 
                title="[bright_white]>> [Info] <<",
                width=65,
                style="bold bright_yellow"
            ))
            return None
    except Exception as e:
        print(Panel(f"[red]Error loading cookies: {str(e)}", 
            title="[bright_white]>> [Error] <<",
            width=65,
            style="bold bright_red"
        ))
        return None

def process_cookies():
    width = 40
    print(Panel("[white]Loading and validating cookies...", 
        title="[bright_white]>> [Process] <<",
        width=65,
        style="bold bright_magenta"
    ))
    
    for i in range(width + 1):
        bar = "█" * i + "░" * (width - i)
        percent = i * 100 // width
        print(f"\r[cyan]|{bar}| {percent}%[/cyan]", end="")
    
    print("\r" + " " * 80)
    
    return config['cookies']

def main():
    try:
        banner()
        
        # Load cookies
        config['cookies'] = load_cookies()
        if not config['cookies']:
            return
            
        # Limit cookies to the maximum allowed for FREEMIUM
        cookie_count = len(config['cookies'])
        if cookie_count > MAX_COOKIES:
            config['cookies'] = config['cookies'][:MAX_COOKIES]
            print(Panel(f"[yellow]FREEMIUM mode is limited to {MAX_COOKIES} cookies.\n[white]Using only the first {MAX_COOKIES} cookies.", 
                title="[bright_white]>> [FREEMIUM Limit] <<",
                width=65,
                style="bold bright_yellow"
            ))
            cookie_count = MAX_COOKIES
        
        # Process cookies
        cookies = process_cookies()
        
        print(Panel(f"""[green]Successfully loaded {len(cookies)} cookies!""",
            title="[bright_white]>> [Success] <<",
            width=65,
            style="bold bright_green"
        ))
        
        auto_reset()

        # Get post URL/ID
        print(Panel("[white]Enter Post ID or URL", 
            title="[bright_white]>> [Post Configuration] <<",
            width=65,
            style="bold bright_cyan",
            subtitle="╭─────",
            subtitle_align="left"
        ))
        input_post = console.input("[bright_white]   ╰─> ")
        
        # Extract post ID
        post_id = extract_post_id(input_post)
        config['post'] = input_post
        config['post_id'] = post_id
        
        if post_id != input_post:
            print(f"[green]Extracted post ID: {post_id}")
                
        auto_reset()

        # Auto-adjust share count based on cookie count
        shares_per_cookie = MAX_SHARES_PER_COOKIE
        total_cookies = len(cookies)
        
        # Calculate total shares based on cookie count
        # 1 cookie = 1000 shares, 2 cookies = 2000 shares, etc. (max 5000)
        total_shares = min(total_cookies * MAX_SHARES_PER_COOKIE, MAX_TOTAL_SHARES)
        
        # Recalculate shares per cookie to distribute evenly
        shares_per_cookie = total_shares // total_cookies
        if shares_per_cookie < 1:
            shares_per_cookie = 1

        # Start process
        print(Panel(f"""[yellow]⚡[white] Post ID   : [bright_cyan]{post_id}[/]
[yellow]⚡[white] Cookies   : [bright_cyan]{len(cookies)}[/]
[yellow]⚡[white] Shares/cookie: [bright_cyan]{shares_per_cookie}[/]
[yellow]⚡[white] Total shares : [bright_cyan]{total_shares}[/]
[yellow]⚡[white] FREEMIUM limit: [bright_red]{MAX_TOTAL_SHARES} shares[/]

[white]Press Enter to start share process...""",
            title="[bright_white]>> [Configuration Summary] <<",
            width=65,
            style="bold bright_cyan",
            subtitle="╭─────",
            subtitle_align="left"
        ))
        console.input("[bright_white]   ╰─> ")
        auto_reset()

        # Initialize stats and cookie objects
        stats = ShareStats()
        stats.total_target = total_shares  # Set the total target
        fb_objects = []
        
        print(Panel("[green]Starting share process...", 
            title="[bright_white]>> [Process Started] <<",
            width=65,
            style="bold bright_magenta"
        ))
        
        # Initialize all Facebook objects
        for i, cookie in enumerate(cookies):
            fb = FacebookShare(
                cookie=cookie,
                post_id=post_id,
                cookie_index=i,
                stats=stats
            )
            fb_objects.append(fb)
        
        # Create thread pool for sharing
        threads = []
        stop_sharing = False
        
        # Distribute shares to cookies
        for i in range(shares_per_cookie):
            if stop_sharing:
                break
                
            for j, fb in enumerate(fb_objects):
                if stats.success_count + stats.failed_count >= total_shares:
                    stop_sharing = True
                    break
                    
                thread = threading.Thread(target=fb.share_post)
                thread.daemon = True
                threads.append(thread)
                thread.start()
                
                # Small delay to prevent rate limiting but not noticeable
                time.sleep(0.01)
            
            # Wait for all threads to complete
            for t in threads:
                t.join()
                
            threads = []
                
            # Check if we've reached the FREEMIUM limit
            if stats.success_count >= total_shares:
                print(f"\n[yellow]Share limit of {total_shares} reached.")
                break
                
        # Print final results
        print(Panel(f"""[green]Process completed in {stats.get_elapsed_time()}!
[yellow]⚡[white] Total successful shares: [bright_green]{stats.success_count}
[yellow]⚡[white] Failed attempts: [bright_red]{stats.failed_count}
[yellow]⚡[white] Average speed: [bright_cyan]{stats.get_speed()}

[white]Detailed Cookie Statistics:
{chr(10).join(f'[yellow]⚡[white] Cookie {idx + 1}: [green]{stat["success"]} success[white], [red]{stat["failed"]} failed' for idx, stat in stats.cookie_stats.items() if stat["success"] > 0 or stat["failed"] > 0)}""",
            title="[bright_white]>> [Completed] <<",
            width=65,
            style="bold bright_cyan"
        ))
        
        print("\n[yellow]Returning to main menu in 3 seconds...[/]")
        time.sleep(3)
        auto_reset()

    except Exception as e:
        print(Panel(f"[red]Error: {str(e)}", 
            title="[bright_white]>> [Error] <<",
            width=65,
            style="bold bright_red"
        ))
        print("\n[yellow]Returning to main menu in 3 seconds...[/]")
        time.sleep(3)
        auto_reset()

if __name__ == "__main__":
    # Clean up at exit to ensure proper terminal behavior
    import atexit
    def cleanup():
        """Ensure terminal is restored properly on exit"""
        try:
            # Reset terminal
            print("\033[0m")  # Reset all attributes
            print("\033[?25h") # Show cursor
        except:
            pass
    atexit.register(cleanup)
    
    while True:
        banner()
        if not show_main_menu():
            print(Panel("[yellow]Thanks for using [bright_cyan]KAI SpamShare v1.0[/]!", 
                title="[bright_white]>> [Goodbye] <<",
                width=65,
                style="bold bright_magenta"
            ))
            try:
                time.sleep(1)
                print("\033[H\033[J", end="") # Clear using ANSI escape sequence
            except:
                pass
            break
            
        main()
