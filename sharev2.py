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
TOKEN_PATH = '/storage/emulated/0/a/token.txt'
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

def load_tokens() -> List[str]:
    try:
        while True:
            print(Panel("""[1] Load from default path (/storage/emulated/0/a/token.txt)
[2] Import tokens from custom file
[3] Import multiple token files""",
                title="[bright_white]>> [Token Import] <<",
                width=65,
                style="bold bright_white",
                subtitle="╭─────",
                subtitle_align="left"
            ))
            choice = console.input("[bright_white]   ╰─> ")

            if choice == "1":
                if os.path.exists(TOKEN_PATH):
                    with open(TOKEN_PATH, 'r') as f:
                        tokens = [line.strip() for line in f if line.strip()]
                    print(Panel(f"[green]Successfully loaded {len(tokens)} tokens", 
                        title="[bright_white]>> [Success] <<",
                        width=65,
                        style="bold bright_white"
                    ))
                    return tokens
                else:
                    print(Panel("[red]Default token file not found!", 
                        title="[bright_white]>> [Error] <<",
                        width=65,
                        style="bold bright_white"
                    ))
                    continue

            elif choice == "2":
                print(Panel("[white]Enter token file path", 
                    title="[bright_white]>> [File Path] <<",
                    width=65,
                    style="bold bright_white",
                    subtitle="╭─────",
                    subtitle_align="left"
                ))
                file_path = console.input("[bright_white]   ╰─> ")
                
                if os.path.exists(file_path):
                    with open(file_path, 'r') as f:
                        tokens = [line.strip() for line in f if line.strip()]
                    print(Panel(f"[green]Successfully loaded {len(tokens)} tokens", 
                        title="[bright_white]>> [Success] <<",
                        width=65,
                        style="bold bright_white"
                    ))
                    return tokens
                else:
                    print(Panel("[red]File not found! Please try again.", 
                        title="[bright_white]>> [Error] <<",
                        width=65,
                        style="bold bright_white"
                    ))
                    continue

            elif choice == "3":
                all_tokens = []
                while True:
                    print(Panel("[white]Enter token file path (or 'done' to finish)", 
                        title="[bright_white]>> [Multiple Files] <<",
                        width=65,
                        style="bold bright_white",
                        subtitle="╭─────",
                        subtitle_align="left"
                    ))
                    file_path = console.input("[bright_white]   ╰─> ")
                    
                    if file_path.lower() == 'done':
                        if all_tokens:
                            print(Panel(f"[green]Successfully loaded {len(all_tokens)} total tokens", 
                                title="[bright_white]>> [Success] <<",
                                width=65,
                                style="bold bright_white"
                            ))
                            return all_tokens
                        continue
                        
                    if os.path.exists(file_path):
                        with open(file_path, 'r') as f:
                            tokens = [line.strip() for line in f if line.strip()]
                            all_tokens.extend(tokens)
                        print(Panel(f"[green]Added {len(tokens)} tokens from {file_path}", 
                            title="[bright_white]>> [Success] <<",
                            width=65,
                            style="bold bright_white"
                        ))
                    else:
                        print(Panel("[red]File not found! Try another path.", 
                            title="[bright_white]>> [Error] <<",
                            width=65,
                            style="bold bright_white"
                        ))
            
            print(Panel("[yellow]Invalid choice! Please try again.", 
                title="[bright_white]>> [Error] <<",
                width=65,
                style="bold bright_white"
            ))

    except Exception as e:
        print(Panel(f"[red]Error loading tokens: {str(e)}", 
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
        print(Panel(f"""[green]Authentication successful!
[white]Key Status: [green]{key_info['status']}
[white]Created  : [cyan]{key_info['created_at']}
[white]Expires  : [cyan]{key_info['expiry']}
[white]Remaining: [yellow]{key_info['remaining']}""", 
            title="[bright_white]>> [Key Information] <<",
            width=65,
            style="bold bright_white"
        ))
        return True
        
    elif choice == "2":
        key = key_manager.generate_key()
        print(Panel(f"""[white]Your key: [green]{key}
[yellow]Note: Key requires admin approval before use
[white]Price: [green]P50 for 3 days access""",
            title="[bright_white]>> [New Key Generated] <<",
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
            print(Panel("[yellow]No pending keys found", 
                title="[bright_white]>> [Information] <<",
                width=65,
                style="bold bright_white"
            ))
            return False
            
        # Display keys with numbers for easier selection
        print(Panel("\n".join(
            f"[yellow]{i}.[white] {key}" for i, key in enumerate(pending_keys, 1)
        ), title="[bright_white]>> [Pending Keys] <<",
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
    while True:
        try:
            banner()
            
            # Add authentication check
            if not check_auth():
                continue
            
            config['tokens'] = load_tokens()
            if not config['tokens']:
                print(Panel("[red]No tokens loaded! Please add tokens first.", 
                    title="[bright_white]>> [Error] <<",
                    width=65,
                    style="bold bright_white"
                ))
                continue

            # Post ID Input
            while True:
                print(Panel("[white]Enter Post ID (or 'back' to return)", 
                    title="[bright_white]>> [Post Configuration] <<",
                    width=65,
                    style="bold bright_white",
                    subtitle="╭─────",
                    subtitle_align="left"
                ))
                post_id = console.input("[bright_white]   ╰─> ")
                
                if post_id.lower() == 'back':
                    break
                    
                if validate_post_id(post_id):
                    config['post_id'] = post_id
                    break
                else:
                    print(Panel("[red]Invalid Post ID format! Please enter a valid numeric ID.", 
                        title="[bright_white]>> [Error] <<",
                        width=65,
                        style="bold bright_white"
                    ))
                    continue

            if post_id.lower() == 'back':
                continue

            # Share Count Input
            while True:
                print(Panel("[white]Enter shares per token (1-1000) (or 'back' to return)", 
                    title="[bright_white]>> [Share Configuration] <<",
                    width=65,
                    style="bold bright_white",
                    subtitle="╭─────",
                    subtitle_align="left"
                ))
                share_input = console.input("[bright_white]   ╰─> ")
                
                if share_input.lower() == 'back':
                    break
                    
                if validate_share_count(share_input):
                    share_count = int(share_input)
                    config['target_shares'] = share_count * len(config['tokens'])
                    break
                else:
                    print(Panel("[red]Invalid share count! Please enter a number between 1 and 1000.", 
                        title="[bright_white]>> [Error] <<",
                        width=65,
                        style="bold bright_white"
                    ))
                    continue

            if share_input.lower() == 'back':
                continue

            # Configuration Summary
            print(Panel(f"""[white]Configuration Summary:
[yellow]⚡[white] Post ID: [cyan]{config['post_id']}
[yellow]⚡[white] Tokens: [cyan]{len(config['tokens'])}
[yellow]⚡[white] Shares per token: [cyan]{share_count}
[yellow]⚡[white] Total target shares: [cyan]{config['target_shares']}""",
                title="[bright_white]>> [Summary] <<",
                width=65,
                style="bold bright_white"
            ))

            print(Panel("[white]Press Enter to start or type 'back' to reconfigure", 
                title="[bright_white]>> [Confirmation] <<",
                width=65,
                style="bold bright_white",
                subtitle="╭─────",
                subtitle_align="left"
            ))
            confirm = console.input("[bright_white]   ╰─> ")
            
            if confirm.lower() == 'back':
                continue

            # Start sharing process
            share_manager = ShareManager()
            
            print(Panel("[green]Starting share process...", 
                title="[bright_white]>> [Process Started] <<",
                width=65,
                style="bold bright_white"
            ))
            
            async with aiohttp.ClientSession() as session:
                tasks = []
                for token in config['tokens']:
                    task = asyncio.create_task(share_manager.share(session, token, share_count))
                    tasks.append(task)
                await asyncio.gather(*tasks)
            
            print(Panel(f"""[green]Process completed!
[yellow]⚡[white] Total shares: [cyan]{share_manager.global_share_count}
[yellow]⚡[white] Successful: [green]{share_manager.success_count}
[yellow]⚡[white] Failed: [red]{share_manager.error_count}""",
                title="[bright_white]>> [Completed] <<",
                width=65,
                style="bold bright_white"
            ))

            print(Panel("[white]Press Enter to continue or 'exit' to quit", 
                title="[bright_white]>> [Next Action] <<",
                width=65,
                style="bold bright_white",
                subtitle="╭─────",
                subtitle_align="left"
            ))
            action = console.input("[bright_white]   ╰─> ")
            if action.lower() == 'exit':
                break

        except KeyboardInterrupt:
            print(Panel("[yellow]Process interrupted by user", 
                title="[bright_white]>> [Interrupted] <<",
                width=65,
                style="bold bright_white"
            ))
            break
        except Exception as e:
            print(Panel(f"[red]Error: {str(e)}", 
                title="[bright_white]>> [Error] <<",
                width=65,
                style="bold bright_white"
            ))
            continue

if __name__ == "__main__":
    asyncio.run(main())
