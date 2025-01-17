import asyncio
import aiohttp
import sys
import os
from typing import List, Optional, Dict
import json
from datetime import datetime
from rich.console import Console
from rich import print
from rich.columns import Columns
from rich.panel import Panel
import re
import requests
import pytz
from typing import Union

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
        title="[white on cyan] INFORMATION [/]",
        width=65,
        style="bold bright_white",
    ))
    
    print(Panel(
        f"""[yellow]⚡[cyan] IP       : [cyan]{sys_info['ip']}[/]
[yellow]⚡[cyan] Region   : [cyan]{sys_info['region']}[/]
[yellow]⚡[cyan] City     : [cyan]{sys_info['city']}[/]
[yellow]⚡[cyan] Time     : [cyan]{sys_info['time']}[/]
[yellow]⚡[cyan] Date     : [cyan]{sys_info['date']}[/]""",
        title="[white on cyan] SYSTEM INFO [/]",
        width=65,
        style="bold bright_white",
    ))

def load_tokens() -> List[str]:
    try:
        if os.path.exists(TOKEN_PATH):
            with open(TOKEN_PATH, 'r') as f:
                return [line.strip() for line in f if line.strip()]
        return []
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
