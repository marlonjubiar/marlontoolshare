import asyncio
import aiohttp
import sys
import os
from typing import List, Optional, Dict
import json
from datetime import datetime
from rich.console import Console
from rich import print
from rich.panel import Panel
import re
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

def banner():
    os.system('clear')
    print(Panel(
        r"""[bright_green]
███████╗██████╗  █████╗ ███╗   ███╗███████╗██╗  ██╗ █████╗ ██████╗ ███████╗
██╔════╝██╔══██╗██╔══██╗████╗ ████║██╔════╝██║  ██║██╔══██╗██╔══██╗██╔════╝
███████╗██████╔╝███████║██╔████╔██║███████╗███████║███████║██████╔╝█████╗  
╚════██║██╔═══╝ ██╔══██║██║╚██╔╝██║╚════██║██╔══██║██╔══██║██╔══██╗██╔══╝  
███████║██║     ██║  ██║██║ ╚═╝ ██║███████║██║  ██║██║  ██║██║  ██║███████╗
╚══════╝╚═╝     ╚═╝  ╚═╝╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝[/]""",
        title="[cyan]CODING BY - RYOEVISU[/]",
        style="bold",
        border_style="bright_blue",
    ))

    print(Panel(
        """[yellow](•)[/] [yellow]DEVELOPER[/]     [cyan]>[/] [bright_green]RYOEVISU[/]
[yellow](•)[/] [yellow]GITHUB[/]        [cyan]>[/] [bright_green]RYO-1N[/]
[yellow](•)[/] [yellow]VERSION[/]       [cyan]>[/] [bright_green]1.0.8[/]
[yellow](•)[/] [yellow]TELEGRAM[/]      [cyan]>[/] [bright_green]t.me/RYOEVISU[/]
[yellow](•)[/] [yellow]TOOL'S NAME[/]   [cyan]>[/] [magenta]SPAMSHARE TOOL[/]""",
        title="[white]INFORMATION[/]",
        style="bold",
    ))

    print(Panel(
        """[bright_green][01/A][/] [yellow]START SPAMSHARE[/]
[bright_green][02/B][/] [yellow]REPORT BUGS[/]
[bright_green][03/C][/] [red]EXIT PROGRAMME[/]""",
        title="[white]MAIN MENU[/]",
        style="bold",
    ))

    print("[cyan]└─>[/] [white]00[/]", end="")
    return console.input("")

def load_tokens() -> List[str]:
    try:
        if os.path.exists(TOKEN_PATH):
            with open(TOKEN_PATH, 'r') as f:
                return [line.strip() for line in f if line.strip()]
        return []
    except Exception as e:
        console.print(Panel(f"[red]Error loading tokens: {str(e)}", style="bold"))
        return []

class ShareManager:
    def __init__(self):
        self.global_share_count = 0
        self.error_count = 0
        self.success_count = 0
        
    async def share(self, session: aiohttp.ClientSession, token: str, share_count: int):
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
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
                        
                        timestamp = datetime.now().strftime("%H:%M:%S")
                        console.print(f"[cyan][{timestamp}][/cyan] [green]Share Success[/green] [yellow]{config['post_id']} [bright_green]{config['total_shares']}/{config['target_shares']}")
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

async def start_share():
    config['tokens'] = load_tokens()
    print(Panel(f"[white]Loaded [green]{len(config['tokens'])}[white] tokens", style="bold"))
    
    if not config['tokens']:
        print(Panel("[red]No tokens available! Please add tokens to the token file first.", style="bold"))
        return
        
    print(Panel("[white]Enter Post ID", title="[white]INPUT[/]", style="bold"))
    config['post_id'] = console.input("[cyan]└─>[/] ")
    
    if not validate_post_id(config['post_id']):
        print(Panel("[red]Invalid Post ID format!", style="bold"))
        return
        
    print(Panel("[white]Enter shares per token (1-1000)", title="[white]INPUT[/]", style="bold"))
    share_count = console.input("[cyan]└─>[/] ")
    
    if not validate_share_count(share_count):
        print(Panel("[red]Invalid share count!", style="bold"))
        return
        
    share_count = int(share_count)
    config['target_shares'] = share_count * len(config['tokens'])
    
    print(Panel(f"[white]Starting share process...\nTarget: [green]{config['target_shares']}[white] shares", style="bold"))
    
    share_manager = ShareManager()
    
    async with aiohttp.ClientSession() as session:
        tasks = []
        for token in config['tokens']:
            task = asyncio.create_task(share_manager.share(session, token, share_count))
            tasks.append(task)
        await asyncio.gather(*tasks)
    
    print(Panel(
        f"""[green]Process completed!
[white]Total shares: [green]{share_manager.success_count}
[white]Failed: [red]{share_manager.error_count}""", 
        style="bold"
    ))

async def main():
    try:
        while True:
            choice = banner()
            
            if choice in ['1', '01', 'A', 'a']:
                await start_share()
            elif choice in ['2', '02', 'B', 'b']:
                print(Panel("[yellow]Please report bugs on Telegram: t.me/RYOEVISU", style="bold"))
            elif choice in ['3', '03', 'C', 'c']:
                print(Panel("""[cyan]=[/] [bright_blue]EXIT DONE ...[/]
[cyan]=[/] [bright_blue]THANKS FOR USING OUR TOOLS ...[/]""", style="bold"))
                break
            else:
                print(Panel("[red]Invalid choice!", style="bold"))
            
            input("\nPress Enter to continue...")
            os.system('clear')

    except KeyboardInterrupt:
        print(Panel("[white]Script terminated by user", style="bold"))
    except Exception as e:
        print(Panel(f"[red]{str(e)}", style="bold"))

if __name__ == "__main__":
    asyncio.run(main())
