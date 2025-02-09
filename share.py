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
        return count > 0
    except ValueError:
        return False

def get_system_info() -> Dict[str, str]:
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
        if os.path.exists(TOKEN_PATH):
            with open(TOKEN_PATH, 'r') as f:
                return [line.strip() for line in f if line.strip()]
        return []
    except Exception as e:
        console.print(Panel(f"[red]Error loading tokens: {str(e)} (｡•́︿•̀｡)", 
            title="[bright_white]>> [Error] <<",
            width=65,
            style="bold bright_white"
        ))
        return []

class ShareManager:
    def __init__(self):
        self.error_count = 0
        self.success_count = 0
        self.total_shares = 0
        
    async def share(self, session: aiohttp.ClientSession, token: str, target_shares: int):
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
        
        while True:
            try:
                async with session.post(
                    'https://graph.facebook.com/me/feed',
                    params={
                        'link': f'https://facebook.com/{config["post_id"]}',
                        'published': '0',
                        'access_token': token
                    },
                    headers=headers,
                    timeout=10
                ) as response:
                    data = await response.json()
                    if 'id' in data:
                        self.success_count += 1
                        self.total_shares += 1
                        timestamp = datetime.now().strftime("%H:%M:%S")
                        console.print(f"[cyan][{timestamp}][/cyan][green] Share Completed [yellow]{config['post_id']} [red]{self.total_shares}/{target_shares}")
                        
                        if self.total_shares >= target_shares:
                            return
                    else:
                        self.error_count += 1
                        if 'error' in data:
                            error_msg = data['error'].get('message', 'Unknown error')
                            if "Error validating access token" in error_msg or "blocking" in error_msg:
                                return
            except:
                self.error_count += 1
                continue

async def get_user_input(prompt: str, validator_func, error_message: str) -> Optional[str]:
    while True:
        os.system('clear')
        banner()
        
        print(Panel(f"[white]Loaded [green]{len(config['tokens'])}[white] tokens ⚡", 
            title="[bright_white]>> [Information] <<",
            width=65,
            style="bold bright_white"
        ))
        
        print(Panel(prompt, 
            title="[bright_white]>> [Input] (｡♡‿♡｡) <<",
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
            print(Panel(f"[red]{error_message} (｡•́︿•̀｡)", 
                title="[bright_white]>> [Error] <<",
                width=65,
                style="bold bright_white"
            ))
            await asyncio.sleep(2)

async def boost_again() -> bool:
    print(Panel("[white]Do you want to boost again? (y/n) (◕‿◕✿)", 
        title="[bright_white]>> [Input] <<",
        width=65,
        style="bold bright_white",
        subtitle="╭─────",
        subtitle_align="left"
    ))
    response = console.input("[bright_white]   ╰─> ").lower()
    return response == 'y'

async def main():
    try:
        while True:
            banner()
            
            config['tokens'] = load_tokens()
            print(Panel(f"[white]Loaded [green]{len(config['tokens'])}[white] tokens ⚡", 
                title="[bright_white]>> [Information] <<",
                width=65,
                style="bold bright_white"
            ))
            
            if not config['tokens']:
                print(Panel("[red]No tokens available! Please add tokens to the token file first. (｡•́︿•̀｡)", 
                    title="[bright_white]>> [Error] <<",
                    width=65,
                    style="bold bright_white"
                ))
                return
                
            config['post_id'] = await get_user_input(
                "[white]Enter Post ID (づ｡◕‿‿◕｡)づ",
                validate_post_id,
                "Invalid Post ID format. Please enter a valid numeric Post ID."
            )
            
            if not config['post_id']:
                return
                
            share_count_input = await get_user_input(
                "[white]Enter total shares (no limit) (ﾉ◕ヮ◕)ﾉ*:･ﾟ✧",
                validate_share_count,
                "Invalid share count. Please enter a positive number."
            )
            
            if not share_count_input:
                return
                
            target_shares = int(share_count_input)
            
            print(Panel(
                f"""[white]Starting share process... (ง •̀ω•́)ง✧
Target: [green]{target_shares}[white] shares""", 
                title="[bright_white]>> [Process Started] <<",
                width=65,
                style="bold bright_white"
            ))
            
            share_manager = ShareManager()
            
            connector = aiohttp.TCPConnector(limit=0)
            timeout = aiohttp.ClientTimeout(total=10)
            
            async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
                tasks = []
                for token in config['tokens']:
                    task = asyncio.create_task(share_manager.share(session, token, target_shares))
                    tasks.append(task)
                await asyncio.gather(*tasks)
            
            os.system('clear')
            banner()
            print(Panel(
                f"""[green]PROCESS COMPLETED (≧▽≦)
[white]Time to celebrate! ♪┏(・o･)┛♪┗ ( ･o･) ┓♪""", 
                title="[bright_white]>> [Completed] <<",
                width=65,
                style="bold bright_white"
            ))
            
            if not await boost_again():
                break

    except KeyboardInterrupt:
        print(Panel("[white]Script terminated by user (╥﹏╥)", 
            title="[bright_white]>> [Terminated] <<",
            width=65,
            style="bold bright_white"
        ))
    except Exception as e:
        print(Panel(f"[red]{str(e)} (っ˘̩╭╮˘̩)っ", 
            title="[bright_white]>> [Error] <<",
            width=65,
            style="bold bright_white"
        ))
    finally:
        print(Panel("[white]Press Enter to exit... (｡•́︿•̀｡)", 
            title="[bright_white]>> [Exit] <<",
            width=65,
            style="bold bright_white",
            subtitle="╭─────",
            subtitle_align="left"
        ))
        console.input("[bright_white]   ╰─> ")

if __name__ == "__main__":
    asyncio.run(main())
