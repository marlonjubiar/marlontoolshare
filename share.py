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
from rich.align import Align
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

def display_header():
    print("\n")
    print(Panel.fit(
        "[bright_cyan]CODING BY - U7P4L IN[/]",
        border_style="bright_black",
        padding=(0, 2),
        style="none"
    ))
    
    print(Panel.fit(
        r"""[green]██████╗░██╗░░░██╗░█████╗░
██╔══██╗╚██╗░██╔╝██╔══██╗
██████╔╝░╚████╔╝░██║░░██║
██╔══██╗░░╚██╔╝░░██║░░██║
██║░░██║░░░██║░░░╚█████╔╝
╚═╝░░╚═╝░░░╚═╝░░░░╚════╝░""",
        title="[red]●[yellow] ●[green] ●[/]",
        border_style="bright_black",
        padding=(0, 2)
    ))

def display_info():
    print(Panel(
        Align(
            "\n".join([
                "[yellow][[white]•[yellow]] [orange1]DEVELOPER[white]    > [bright_green]U7P4L IN[/]",
                "[yellow][[white]•[yellow]] [orange1]GITHUB[white]       > [bright_green]U7P4L-IN[/]",
                "[yellow][[white]•[yellow]] [orange1]VERSION[white]      > [bright_green]1.0.8[/]",
                "[yellow][[white]•[yellow]] [orange1]TELEGRAM[white]     > [bright_green]t.me/TheU7p4lArmyX[/]",
                "[yellow][[white]•[yellow]] [orange1]TOOL'S NAME[white]  > [purple]SPAMSHARE[/]"
            ]),
            "left"
        ),
        title="[white]INFORMATION[/]",
        border_style="bright_black",
        padding=(0, 2)
    ))

def display_menu():
    print(Panel(
        Align(
            "\n".join([
                "[yellow][[white]01/A[yellow]] [bright_green]START SPAMSHARE[/]",
                "[yellow][[white]02/B[yellow]] [bright_green]REPORT FOR ANY BUGS[/]",
                "[yellow][[white]03/C[yellow]] [bright_red]EXIT PROGRAMME[/]"
            ]),
            "left"
        ),
        title="[white]MAIN MENU[/]",
        border_style="bright_black",
        padding=(0, 2)
    ))
    print("[bright_black]└─> [/]", end="")

def display_community():
    print(Panel(
        Align(
            "\n".join([
                "[yellow][[white]01/A[yellow]] [bright_green]JOIN FB PAGE[/]",
                "[yellow][[white]02/B[yellow]] [bright_green]JOIN FB GROUP[/]",
                "[yellow][[white]03/C[yellow]] [bright_green]JOIN TELEGRAM[/]",
                "[yellow][[white]04/D[yellow]] [bright_green]FOLLOW GITHUB[/]",
                "[yellow][[white]00/X[yellow]] [bright_red]BACK TO MAIN MENU[/]"
            ]),
            "left"
        ),
        title="[white]OUR COMMUNITY[/]",
        border_style="bright_black",
        padding=(0, 2)
    ))
    print("[bright_black]└─> [/]", end="")

def banner():
    os.system('clear')
    display_header()
    display_info()
    display_menu()

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
                        print(f"[cyan][{timestamp}][/cyan][bright_green] Share Completed [yellow]{config['post_id']} [red]{config['total_shares']}/{config['target_shares']}")
                    else:
                        self.error_count += 1
                        retries -= 1
                        if 'error' in data:
                            print(f"[bright_red]Error: {data['error'].get('message', 'Unknown error')}")
            except Exception as e:
                self.error_count += 1
                retries -= 1
                print(f"[bright_red]Share failed: {str(e)}")
                await asyncio.sleep(1)

def load_tokens() -> List[str]:
    try:
        if os.path.exists(TOKEN_PATH):
            with open(TOKEN_PATH, 'r') as f:
                return [line.strip() for line in f if line.strip()]
        return []
    except Exception as e:
        print(Panel(f"[bright_red]Error loading tokens: {str(e)}", 
            title="[white]ERROR[/]",
            border_style="bright_black",
            padding=(0, 2)
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
        print(Panel(f"[bright_red]Error loading share count: {str(e)}", 
            title="[white]ERROR[/]",
            border_style="bright_black",
            padding=(0, 2)
        ))
        return 0

def save_global_share_count(count: int):
    try:
        with open(GLOBAL_SHARE_COUNT_FILE, 'w') as f:
            json.dump({'count': count}, f)
    except Exception as e:
        print(Panel(f"[bright_red]Error saving share count: {str(e)}", 
            title="[white]ERROR[/]",
            border_style="bright_black",
            padding=(0, 2)
        ))

async def get_user_input(prompt: str, validator_func, error_message: str) -> Optional[str]:
    while True:
        print(Panel(prompt,
            border_style="bright_black",
            padding=(0, 2)
        ))
        print("[bright_black]└─> [/]", end="")
        user_input = console.input("")
        
        if user_input.lower() == 'exit':
            return None
            
        if validator_func(user_input):
            return user_input
        else:
            print(Panel(f"[bright_red]{error_message}",
                title="[white]ERROR[/]",
                border_style="bright_black",
                padding=(0, 2)
            ))

async def main():
    try:
        banner()
        
        config['tokens'] = load_tokens()
        print(Panel(f"[white]Loaded [bright_green]{len(config['tokens'])}[white] tokens",
            title="[white]INFORMATION[/]",
            border_style="bright_black",
            padding=(0, 2)
        ))
        
        if not config['tokens']:
            print(Panel("[bright_red]No tokens available! Please add tokens to the token file first.",
                title="[white]ERROR[/]",
                border_style="bright_black",
                padding=(0, 2)
            ))
            return

        choice = console.input("")
        if choice in ['1', '01', 'A', 'a']:
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
                f"[white]Starting share process...\nTarget: [bright_green]{config['target_shares']}[white] shares",
                title="[white]PROCESS STARTED[/]",
                border_style="bright_black",
                padding=(0, 2)
            ))
            
            share_manager = ShareManager()
            
            async with aiohttp.ClientSession() as session:
                tasks = []
                for token in config['tokens']:
                    task = asyncio.create_task(share_manager.share(session, token, share_count))
                    tasks.append(task)
                await asyncio.gather(*tasks)
            
            print(Panel(
                f"""[bright_green]Process completed!
[white]Total shares: [bright_green]{share_manager.global_share_count}
[white]Successful: [bright_green]{share_manager.success_count}
[white]Failed: [bright_red]{share_manager.error_count}""",
                title="[white]COMPLETED[/]",
                border_style="bright_black",
                padding=(0, 2)
            ))
        
        elif choice in ['2', '02', 'B', 'b']:
            display_community()
        
        elif choice in ['3', '03', 'C', 'c']:
            print(Panel(
                "\n".join([
                    "[bright_cyan]EXIT DONE ..!!![/]",
                    "[bright_cyan]THANKS FOR USING OUR TOOLS ...!!![/]"
                ]),
                title="[white]EXIT[/]",
                border_style="bright_black",
                padding=(0, 2)
            ))
            return

    except KeyboardInterrupt:
        print(Panel("[white]Script terminated by user",
            title="[white]TERMINATED[/]",
            border_style="bright_black",
            padding=(0, 2)
        ))
    except Exception as e:
        print(Panel(f"[bright_red]{str(e)}",
            title="[white]ERROR[/]",
            border_style="bright_black",
            padding=(0, 2)
        ))
    finally:
        print(Panel("[bright_black]/sdcard[/]", border_style="bright_black", padding=(0, 2)))

if __name__ == "__main__":
    asyncio.run(main())
