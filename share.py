import asyncio
import aiohttp
import sys
import os
from typing import List
import json
from datetime import datetime
from rich.console import Console
from rich import print
from rich.columns import Columns
from rich.panel import Panel

console = Console()
os.system('clear')

TOKEN_PATH = '/storage/emulated/0/a/token.txt'
GLOBAL_SHARE_COUNT_FILE = 'global_share_count.json'

config = {
    'post_id': '',
    'tokens': [],
    'total_shares': 0,
    'target_shares': 0
}

import requests
from datetime import datetime
import pytz

def get_system_info():
    try:
        ip_info = requests.get('https://ipapi.co/json/').json()
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
        """[yellow]⚡[white] Tool     : [green]SpamShare[/]
[yellow]⚡[white] Version  : [green]1.0.0[/]
[yellow]⚡[white] Dev      : [green]Ryo Evisu[/]
[yellow]⚡[white] Status   : [red]Admin Access[/]""",
        title="[white on red] INFORMATION [/]",
        width=65,
        style="bold bright_white",
    ))
    
    print(Panel(
        f"""[yellow]⚡[white] IP       : [cyan]{sys_info['ip']}[/]
[yellow]⚡[white] Region   : [cyan]{sys_info['region']}[/]
[yellow]⚡[white] City     : [cyan]{sys_info['city']}[/]
[yellow]⚡[white] Time     : [cyan]{sys_info['time']}[/]
[yellow]⚡[white] Date     : [cyan]{sys_info['date']}[/]""",
        title="[white on red] SYSTEM INFO [/]",
        width=65,
        style="bold bright_white",
    ))

def load_tokens() -> List[str]:
    try:
        os.makedirs(os.path.dirname(TOKEN_PATH), exist_ok=True)
        if os.path.exists(TOKEN_PATH):
            with open(TOKEN_PATH, 'r') as f:
                return [line.strip() for line in f if line.strip()]
        return []
    except Exception:
        return []

def save_token(token: str):
    try:
        os.makedirs(os.path.dirname(TOKEN_PATH), exist_ok=True)
        with open(TOKEN_PATH, 'a') as f:
            f.write(f"{token}\n")
    except Exception:
        pass

def load_global_share_count() -> int:
    try:
        if os.path.exists(GLOBAL_SHARE_COUNT_FILE):
            with open(GLOBAL_SHARE_COUNT_FILE, 'r') as f:
                data = json.load(f)
                return data.get('count', 0)
        return 0
    except Exception:
        return 0

def save_global_share_count(count: int):
    try:
        with open(GLOBAL_SHARE_COUNT_FILE, 'w') as f:
            json.dump({'count': count}, f)
    except Exception:
        pass

class ShareManager:
    def __init__(self):
        self.global_share_count = load_global_share_count()
        
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
        
        while config['total_shares'] < config['target_shares']:
            try:
                async with session.post(
                    'https://graph.facebook.com/me/feed',
                    params={
                        'link': f'https://facebook.com/{config["post_id"]}',
                        'published': '0',
                        'access_token': token
                    },
                    headers=headers
                ) as response:
                    data = await response.json()
                    if 'id' in data:
                        config['total_shares'] += 1
                        self.global_share_count += 1
                        save_global_share_count(self.global_share_count)
                        
                        # Format timestamp and progress
                        timestamp = datetime.now().strftime("%H:%M:%S")
                        console.print(f"[cyan][{timestamp}][/cyan][green] Share Completed [yellow]{config['post_id']} [red]{config['total_shares']}/{config['target_shares']}")
                    else:
                        return
            except Exception:
                return

async def main():
    banner()
    
    # Load existing tokens
    config['tokens'] = load_tokens()
    print(Panel(f"[bold white]Loaded [bold green]{len(config['tokens'])}[bold white] tokens", 
        title="[bold bright_white]>> [Information] <<",
        width=65,
        style="bold bright_white"
    ))
    
    # Get new token if needed
    print(Panel(f"[bold white]Enter new token, make sure you have logged in with the correct account!", 
        width=65, style="bold bright_white", title="[bold bright_white]>> [Token] <<", subtitle="╭─────", subtitle_align="left"))
    new_token = console.input("[bold bright_white]   ╰─> ")
    
    if new_token:
        save_token(new_token)
        config['tokens'].append(new_token)
        print(Panel(f"[bold green]Token successfully saved to system!", 
            width=65, style="bold bright_white", title="[bold bright_white]>> [Success] <<"))
    
    if not config['tokens']:
        print(Panel(f"[bold red]No tokens available! Please add a token first.", 
            width=65, style="bold bright_white", title="[bold bright_white]>> [Error] <<"))
        return
        
    print(Panel(f"[bold white]Enter Post ID, make sure your[bold red] post is public[bold white] and has a[bold red] Follow[bold white] button!", 
        width=65, style="bold bright_white", title="[bold bright_white]>> [Post ID] <<", subtitle="╭─────", subtitle_align="left"))
    config['post_id'] = console.input("[bold bright_white]   ╰─> ")
    
    print(Panel(f"[bold white]Enter shares per token[bold green] (Example: 100 shares per token)[bold white]", 
        width=65, style="bold bright_white", title="[bold bright_white]>> [Share Count] <<", subtitle="╭─────", subtitle_align="left"))

    print(Panel("[white]Enter shares per token", 
        title="[bright_white]>> [Share Count] <<",
        width=65,
        style="bold bright_white",
        subtitle="╭─────",
        subtitle_align="left"
    ))
    share_count = int(console.input("[bright_white]   ╰─> "))
    
    config['target_shares'] = share_count * len(config['tokens'])
    
    if not config['post_id'] or not share_count:
        print(Panel("[red]Invalid input!", 
            title="[bright_white]>> [Error] <<",
            width=65,
            style="bold bright_white"
        ))
        return
    
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
        f"[green]Process completed!\n[white]Total shares: [green]{share_manager.global_share_count}", 
        title="[bright_white]>> [Completed] <<",
        width=65,
        style="bold bright_white"
    ))

if __name__ == "__main__":
    try:
        asyncio.run(main())
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
    
    print(Panel("[white]Press Enter to exit...", 
        title="[bright_white]>> [Exit] <<",
        width=65,
        style="bold bright_white",
        subtitle="╭─────",
        subtitle_align="left"
    ))
    console.input("[bright_white]   ╰─> ")
