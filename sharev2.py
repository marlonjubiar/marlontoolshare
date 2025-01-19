import asyncio
import aiohttp
import sys
import os
from typing import List, Optional, Dict
import json
from datetime import datetime, timedelta
from rich.console import Console
from rich import print
from rich.columns import Columns
from rich.panel import Panel
import re
import requests
import pytz
from typing import Union
import hashlib
import secrets

console = Console()
os.system('clear')

# File paths
TOKEN_PATH = 'token.txt'  # Changed to local path for Termux compatibility
GLOBAL_SHARE_COUNT_FILE = 'global_share_count.json'
KEYS_FILE = 'auth_keys.json'

# Default admin password hash (password: "password")
ADMIN_HASH = "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8"

config = {
    'post_id': '',
    'tokens': [],
    'total_shares': 0,
    'target_shares': 0
}

class KeyManager:
    def __init__(self, keys_file=KEYS_FILE):
        self.keys_file = keys_file
        self.keys = self._load_keys()
        self.ph_tz = pytz.timezone('Asia/Manila')

    def _load_keys(self):
        if os.path.exists(self.keys_file):
            try:
                with open(self.keys_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def _save_keys(self):
        with open(self.keys_file, 'w') as f:
            json.dump(self.keys, f, indent=4)

    def generate_key(self) -> str:
        key = secrets.token_hex(8)  # Shorter 16-character key
        timestamp = datetime.now(self.ph_tz).strftime('%Y%m%d%H%M%S')
        full_key = f"{key}-{timestamp}"
        
        expiry = (datetime.now(self.ph_tz) + timedelta(days=3)).strftime('%Y-%m-%d %H:%M:%S')
        self.keys[full_key] = {
            'expiry': expiry,
            'active': False,
            'created_at': datetime.now(self.ph_tz).strftime('%Y-%m-%d %H:%M:%S')
        }
        self._save_keys()
        return full_key

    def get_key_info(self, key: str) -> Dict:
        if key not in self.keys:
            return {}
            
        key_data = self.keys[key]
        now = datetime.now(self.ph_tz)
        expiry = datetime.strptime(key_data['expiry'], '%Y-%m-%d %H:%M:%S')
        expiry = self.ph_tz.localize(expiry)
        
        remaining = expiry - now
        days = remaining.days
        hours = remaining.seconds // 3600
        minutes = (remaining.seconds % 3600) // 60
        
        return {
            'active': key_data['active'],
            'created_at': key_data['created_at'],
            'expiry': key_data['expiry'],
            'remaining': f"{days}d {hours}h {minutes}m",
            'status': "Active" if key_data['active'] else "Pending Approval",
            'is_expired': now > expiry
        }

    def list_keys(self) -> List[Dict]:
        now = datetime.now(self.ph_tz)
        keys_info = []
        for key, data in self.keys.items():
            expiry = datetime.strptime(data['expiry'], '%Y-%m-%d %H:%M:%S')
            expiry = self.ph_tz.localize(expiry)
            
            if now <= expiry:  # Only show non-expired keys
                keys_info.append({
                    'key': key,
                    'status': "Active" if data['active'] else "Pending",
                    'expiry': data['expiry']
                })
        return keys_info

    def approve_key(self, key: str) -> bool:
        if key in self.keys:
            self.keys[key]['active'] = True
            self._save_keys()
            return True
        return False

    def validate_key(self, key: str) -> tuple[bool, str]:
        if key not in self.keys:
            return False, "Invalid key"
        
        key_data = self.keys[key]
        now = datetime.now(self.ph_tz)
        
        if not key_data['active']:
            return False, "Key not approved by admin"
            
        expiry = datetime.strptime(key_data['expiry'], '%Y-%m-%d %H:%M:%S')
        expiry = self.ph_tz.localize(expiry)
        
        if now > expiry:
            return False, "Key has expired"
            
        return True, "Key is valid"

def validate_post_id(post_id: str) -> bool:
    if not post_id:
        return False
    post_id_pattern = r'^[0-9]+$'
    return bool(re.match(post_id_pattern, post_id))

def validate_share_count(count: str) -> bool:
    try:
        count = int(count)
        return 0 < count <= 1000
    except ValueError:
        return False

def get_system_info() -> Dict[str, str]:
    try:
        ip_info = requests.get('https://ipapi.co/json/', timeout=5).json()
        ph_tz = pytz.timezone('Asia/Manila')
        ph_time = datetime.now(ph_tz)
        return {
            'ip': ip_info.get('ip', 'Unknown'),
            'region': ip_info.get('region', 'Unknown'),
            'city': ip_info.get('city', 'Unknown'),
            'time': ph_time.strftime("%I:%M:%S %p"),
            'date': ph_time.strftime("%B %d, %Y")
        }
    except:
        return {
            'ip': 'Unknown',
            'region': 'Unknown',
            'city': 'Unknown',
            'time': datetime.now().strftime("%I:%M:%S %p"),
            'date': datetime.now().strftime("%B %d, %Y")
        }

def banner():
    os.system('clear')
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
[yellow]⚡[cyan] Status   : [red]Admin Access[/]""",
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

def setup_token_file():
    print(Panel("[white]No token file found. Let's set it up!", 
        title="[bright_white]>> [Setup] <<",
        width=65,
        style="bold bright_white"
    ))
    
    tokens = []
    while True:
        print(Panel(f"""[yellow]⚡[cyan] Current Tokens : [green]{len(tokens)}[/]
[yellow]⚡[cyan] Options       :
   [1] Add token
   [2] Save and continue
   [3] Exit""",
            title="[white on red] TOKEN SETUP [/]",
            width=65,
            style="bold bright_white"
        ))
        
        choice = console.input("[bright_white]Enter choice (1-3): ")
        
        if choice == "1":
            print(Panel("[white]Enter Facebook Token", 
                title="[bright_white]>> [Input] <<",
                width=65,
                style="bold bright_white",
                subtitle="╭─────",
                subtitle_align="left"
            ))
            token = console.input("[bright_white]   ╰─> ")
            if token.strip():
                tokens.append(token.strip())
                print(Panel(f"[green]Token added successfully! Total tokens: {len(tokens)}", 
                    title="[bright_white]>> [Success] <<",
                    width=65,
                    style="bold bright_white"
                ))
        elif choice == "2":
            if tokens:
                try:
                    with open('token.txt', 'w') as f:
                        f.write('\n'.join(tokens))
                    print(Panel(f"[green]Successfully saved {len(tokens)} tokens to token.txt", 
                        title="[bright_white]>> [Success] <<",
                        width=65,
                        style="bold bright_white"
                    ))
                    return True
                except Exception as e:
                    print(Panel(f"[red]Error saving tokens: {str(e)}", 
                        title="[bright_white]>> [Error] <<",
                        width=65,
                        style="bold bright_white"
                    ))
            else:
                print(Panel("[red]No tokens to save!", 
                    title="[bright_white]>> [Error] <<",
                    width=65,
                    style="bold bright_white"
                ))
        elif choice == "3":
            return False

def load_tokens() -> List[str]:
    try:
        if not os.path.exists('token.txt'):
            if setup_token_file():
                with open('token.txt', 'r') as f:
                    return [line.strip() for line in f if line.strip()]
            return []
            
        with open('token.txt', 'r') as f:
            return [line.strip() for line in f if line.strip()]
    except Exception as e:
        console.print(Panel(f"[red]Error loading tokens: {str(e)}", 
            title="[bright_white]>> [Error] <<",
            width=65,
            style="bold bright_white"
        ))
        return []

def load_global_share_count() -> int:
    try:
        if os.path.exists(GLOBAL_SHARE_COUNT_FILE):
            with open(GLOBAL_SHARE_COUNT_FILE, 'r') as f:
                data = json.load(f)
                return int(data.get('count', 0))
        return 0
    except Exception as e:
        console.print(Panel(f"[red]Error loading share count: {str(e)}", 
            title="[bright_white]>> [Error] <<",
            width=65,
            style="bold bright_white"
        ))
        return 0

def save_global_share_count(count: int):
    try:
        with open(GLOBAL_SHARE_COUNT_FILE, 'w') as f:
            json.dump({'count': count}, f)
    except Exception as e:
        console.print(Panel(f"[red]Error saving share count: {str(e)}", 
            title="[bright_white]>> [Error] <<",
            width=65,
            style="bold bright_white"
        ))

def check_auth() -> bool:
    key_manager = KeyManager()
    
    print(Panel("""[1] Enter key
[2] Generate new key
[3] Admin: Approve key""",
        title="[bright_white]>> [Authentication] <<",
        width=65,
        style="bold bright_white"
    ))
    
    choice = console.input("[bright_white]Enter choice (1-3): ")
    
    if choice == "1":
        print(Panel("[white]Enter Your Key", 
            title="[bright_white]>> [Key Authentication] <<",
            width=65,
            style="bold bright_white",
            subtitle="╭─────",
            subtitle_align="left"
        ))
        key = console.input("[bright_white]   ╰─> ")
        is_valid, message = key_manager.validate_key(key)
        
        if not is_valid:
            print(Panel(f"[red]{message}", 
                title="[bright_white]>> [Error] <<",
                width=65,
                style="bold bright_white"
            ))
            return False
            
        key_info = key_manager.get_key_info(key)
        print(Panel(f"""[yellow]⚡[cyan] Status   : [green]{key_info['status']}[/]
[yellow]⚡[cyan] Created  : [cyan]{key_info['created_at']}[/]
[yellow]⚡[cyan] Expires  : [cyan]{key_info['expiry']}[/]
[yellow]⚡[cyan] Remaining: [yellow]{key_info['remaining']}[/]""",
            title="[white on red] KEY INFORMATION [/]",
            width=65,
            style="bold bright_white"
        ))
        print(Panel("[green]Authentication successful!", 
            title="[bright_white]>> [Success] <<",
            width=65,
            style="bold bright_white"
        ))
        return True
        
    elif choice == "2":
        key = key_manager.generate_key()
        print(Panel(f"""[yellow]⚡[cyan] Key      : [green]{key}[/]
[yellow]⚡[cyan] Status   : [yellow]Pending Approval[/]
[yellow]⚡[cyan] Price    : [green]P50[/]
[yellow]⚡[cyan] Duration : [green]3 Days[/]""",
            title="[white on red] KEY INFORMATION [/]",
            width=65,
            style="bold bright_white"
        ))
        return False
        
    elif choice == "3":
        print(Panel("[white]Enter Admin Password", 
            title="[bright_white]>> [Admin Authentication] <<",
            width=65,
            style="bold bright_white",
            subtitle="╭─────",
            subtitle_align="left"
        ))
        admin_pass = console.input("[bright_white]   ╰─> ")
        
        if hashlib.sha256(admin_pass.encode()).hexdigest() != ADMIN_HASH:
            print(Panel("[red]Invalid admin password", 
                title="[bright_white]>> [Error] <<",
                width=65,
                style="bold bright_white"
            ))
            return False

        # Show list of pending keys
        pending_keys = [k for k, v in key_manager.keys.items() if not v['active']]
        if not pending_keys:
            print(Panel("[yellow]⚡[cyan] Status : [yellow]No pending keys found[/]", 
                title="[white on red] PENDING KEYS [/]",
                width=65,
                style="bold bright_white"
            ))
            return False
            
        # Display keys with numbers for easier selection
        print(Panel("\n".join(
            f"[yellow]⚡[cyan] Key {i}   : [white]{key}[/]" for i, key in enumerate(pending_keys, 1)
        ), title="[white on red] PENDING KEYS [/]",
            width=65,
            style="bold bright_white"
        ))
        
        print(Panel("[white]Enter Key Number to Approve (1, 2, 3, etc.)", 
            title="[bright_white]>> [Key Approval] <<",
            width=65,
            style="bold bright_white",
            subtitle="╭─────",
            subtitle_align="left"
        ))
        key_num = console.input("[bright_white]   ╰─> ")
        
        try:
            key_index = int(key_num) - 1
            if 0 <= key_index < len(pending_keys):
                key_to_approve = pending_keys[key_index]
                if key_manager.approve_key(key_to_approve):
                    print(Panel("[green]Key approved successfully!", 
                        title="[bright_white]>> [Success] <<",
                        width=65,
                        style="bold bright_white"
                    ))
                else:
                    print(Panel("[red]Error approving key", 
                        title="[bright_white]>> [Error] <<",
                        width=65,
                        style="bold bright_white"
                    ))
            else:
                print(Panel("[red]Invalid key number", 
                    title="[bright_white]>> [Error] <<",
                    width=65,
                    style="bold bright_white"
                ))
        except ValueError:
            print(Panel("[red]Please enter a valid number", 
                title="[bright_white]>> [Error] <<",
                width=65,
                style="bold bright_white"
            ))
            
        return False
    
    return False

class ShareManager:
    def __init__(self):
        self.global_share_count = load_global_share_count()
        self.error_count = 0
        self.success_count = 0
        
    async def share(self, session: aiohttp.ClientSession, token: str, share_count: int):
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Google Chrome";v="107", "Chromium";v="107", "Not=A?Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': "Windows",
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'accept-encoding': 'gzip, deflate',
            'host': 'graph.facebook.com'
        }
        
        retries = 3
        while config['total_shares'] < config['target_shares'] and retries > 0:
            try:
                async with session.post(
                    'https://graph.facebook.com/me/feed',
                    params={
                        'link': f'https://facebook.com/{config["post_id"]}',
                        'published': '0',
                        'access_token': token
                    },
                    headers=headers,
                    timeout=30
                ) as response:
                    data = await response.json()
                    if 'id' in data:
                        config['total_shares'] += 1
                        self.global_share_count += 1
                        self.success_count += 1
                        save_global_share_count(self.global_share_count)
                        
                        timestamp = datetime.now().strftime("%H:%M:%S")
                        console.print(f"[cyan][{timestamp}][/cyan][green] Share Completed [yellow]{config['post_id']} [red]{config['total_shares']}/{config['target_shares']}")
                    else:
                        self.error_count += 1
                        retries -= 1
                        if 'error' in data:
                            console.print(f"[red]Error: {data['error'].get('message', 'Unknown error')}")
            except Exception as e:
                self.error_count += 1
                retries -= 1
                console.print(f"[red]Share failed: {str(e)}")
                await asyncio.sleep(1)

async def get_user_input(prompt: str, validator_func, error_message: str) -> Optional[str]:
    while True:
        print(Panel(prompt, 
            title="[bright_white]>> [Input] <<",
            width=65,
            style="bold bright_white",
            subtitle="╭─────",
            subtitle_align="left"
        ))
        user_input = console.input("[bright_white]   ╰─> ")
        
        if user_input.lower() == 'exit':
            return None
            
        if validator_func(user_input):
            return user_input
        else:
            print(Panel(f"[red]{error_message}", 
                title="[bright_white]>> [Error] <<",
                width=65,
                style="bold bright_white"
            ))

async def main():
    try:
        banner()
        
        # Add authentication check
        if not check_auth():
            return
        
        config['tokens'] = load_tokens()
        print(Panel(f"[white]Loaded [green]{len(config['tokens'])}[white] tokens", 
            title="[bright_white]>> [Information] <<",
            width=65,
            style="bold bright_white"
        ))
        
        if not config['tokens']:
            print(Panel("[red]No tokens available! Please add tokens to the token file first.", 
                title="[bright_white]>> [Error] <<",
                width=65,
                style="bold bright_white"
            ))
            return
            
        config['post_id'] = await get_user_input(
            "[white]Enter Post ID",
            validate_post_id,
            "Invalid Post ID format. Please enter a valid numeric Post ID."
        )
        
        if not config['post_id']:
            return
            
        share_count_input = await get_user_input(
            "[white]Enter shares per token (1-1000)",
            validate_share_count,
            "Invalid share count. Please enter a number between 1 and 1000."
        )
        
        if not share_count_input:
            return
            
        share_count = int(share_count_input)
        config['target_shares'] = share_count * len(config['tokens'])
        
        print(Panel(
            f"[white]Starting share process...\nTarget: [green]{config['target_shares']}[white] shares", 
            title="[bright_white]>> [Process Started] <<",
            width=65,
            style="bold bright_white"
        ))
        
        share_manager = ShareManager()
        
        async with aiohttp.ClientSession() as session:
            tasks = []
            for token in config['tokens']:
                task = asyncio.create_task(share_manager.share(session, token, share_count))
                tasks.append(task)
            await asyncio.gather(*tasks)
        
        print(Panel(
            f"""[green]Process completed!
[white]Total shares: [green]{share_manager.global_share_count}
[white]Successful: [green]{share_manager.success_count}
[white]Failed: [red]{share_manager.error_count}""", 
            title="[bright_white]>> [Completed] <<",
            width=65,
            style="bold bright_white"
        ))

    except KeyboardInterrupt:
        print(Panel("[white]Script terminated by user", 
            title="[bright_white]>> [Terminated] <<",
            width=65,
            style="bold bright_white"
        ))
    except Exception as e:
        print(Panel(f"[red]{str(e)}", 
            title="[bright_white]>> [Error] <<",
            width=65,
            style="bold bright_white"
        ))
    finally:
        print(Panel("[white]Press Enter to exit...", 
            title="[bright_white]>> [Exit] <<",
            width=65,
            style="bold bright_white",
            subtitle="╭─────",
            subtitle_align="left"
        ))
        console.input("[bright_white]   ╰─> ")

if __name__ == "__main__":
    asyncio.run(main())
