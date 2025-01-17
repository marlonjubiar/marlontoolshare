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
import requests
import pytz

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
        os.makedirs(os.path.dirname(TOKEN_PATH), exist_ok=True)
        if os.path.exists(TOKEN_PATH):
            with open(TOKEN_PATH, 'r') as f:
                return [line.strip() for line in f if line.strip()]
        return []
    except Exception as e:
        print(Panel(f"[red]Error loading tokens: {str(e)}", 
            title="[bright_white]>> [Error] <<",
            width=65,
            style="bold bright_white"
        ))
        return []

def save_token(token: str):
    try:
        os.makedirs(os.path.dirname(TOKEN_PATH), exist_ok=True)
        with open(TOKEN_PATH, 'a') as f:
            f.write(f"{token}\n")
    except Exception as e:
        print(Panel(f"[red]Error saving token: {str(e)}", 
            title="[bright_white]>> [Error] <<",
            width=65,
            style="bold bright_white"
        ))

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
    except Exception as e:
        print(Panel(f"[red]Error saving share count: {str(e)}", 
            title="[bright_white]>> [Error] <<",
            width=65,
            style="bold bright_white"
        ))

def validate_token(token: str) -> bool:
    return bool(token and len(token) >= 50)

def validate_post_id(post_id: str) -> bool:
    return bool(post_id and post_id.replace('_', '').isdigit())

def validate_share_count(count: str) -> bool:
    try:
        num = int(count)
        return num > 0 and num <= 1000
    except ValueError:
        return False

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
                        
                        timestamp = datetime.now().strftime("%H:%M:%S")
                        console.print(f"[cyan][{timestamp}][/cyan][green] Share Completed [yellow]{config['post_id']} [red]{config['total_shares']}/{config['target_shares']}")
                    else:
                        print(Panel(f"[red]Share failed: {data.get('error', {}).get('message', 'Unknown error')}", 
                            title="[bright_white]>> [Error] <<",
                            width=65,
                            style="bold bright_white"
                        ))
                        return
            except Exception as e:
                print(Panel(f"[red]Share error: {str(e)}", 
                    title="[bright_white]>> [Error] <<",
                    width=65,
                    style="bold bright_white"
                ))
                return

async def get_user_input(prompt: str, validation_func, error_message: str):
    while True:
        print(Panel(prompt, 
            title="[bright_white]>> [Input] <<",
            width=65,
            style="bold bright_white",
            subtitle="╭─────",
            subtitle_align="left"
        ))
        user_input = console.input("[bright_white]   ╰─> ")
        
        if validation_func(user_input):
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
        print(Panel(f"[cyan]Loaded [green]{len(config['tokens'])}[cyan] tokens", 
            title="[bright_white]>> [Information] <<",
            width=65,
            style="bold bright_white"
        ))
        
        token_text = "[cyan]Enter new token ([green]press Enter to skip[cyan])"
        print(Panel(token_text, title="[bright_white]>> [Input Token] <<", 
            width=65, style="bold bright_white", subtitle="╭─────", subtitle_align="left"))
        new_token = console.input("[bright_white]   ╰─> ")
        
        if new_token:
            if validate_token(new_token):
                save_token(new_token)
                config['tokens'].append(new_token)
                print(Panel("[green]Token saved successfully", 
                    title="[bright_white]>> [Success] <<",
                    width=65,
                    style="bold bright_white"
                ))
            else:
                print(Panel("[red]Invalid token format!", 
                    title="[bright_white]>> [Error] <<",
                    width=65,
                    style="bold bright_white"
                ))
        
        if not config['tokens']:
            print(Panel("[red]No tokens available!", 
                title="[bright_white]>> [Error] <<",
                width=65,
                style="bold bright_white"
            ))
            return
        
        config['post_id'] = await get_user_input(
            "[cyan]Enter Post ID",
            validate_post_id,
            "Invalid Post ID format! Please enter a valid Facebook post ID."
        )
        
        share_count_str = await get_user_input(
            "[cyan]Enter shares per token (1-1000)",
            validate_share_count,
            "Invalid share count! Please enter a number between 1 and 1000."
        )
        share_count = int(share_count_str)
        
        config['target_shares'] = share_count * len(config['tokens'])
        
        print(Panel(
            f"[cyan]Starting share process...\nTarget: [green]{config['target_shares']}[cyan] shares", 
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
            f"[green]Process completed!\n[cyan]Total shares: [green]{share_manager.global_share_count}", 
            title="[bright_white]>> [Completed] <<",
            width=65,
            style="bold bright_white"
        ))

    except Exception as e:
        print(Panel(f"[red]Main process error: {str(e)}", 
            title="[bright_white]>> [Error] <<",
            width=65,
            style="bold bright_white"
        ))

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(Panel("[cyan]Script terminated by user", 
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
    
    print(Panel("[cyan]Press Enter to exit...", 
        title="[bright_white]>> [Exit] <<",
        width=65,
        style="bold bright_white",
        subtitle="╭─────",
        subtitle_align="left"
    ))
    console.input("[bright_white]   ╰─> ")
