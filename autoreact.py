import os
import sys
import time
import requests
import random
import json
import re
from datetime import datetime
import threading

def clear():
    os.system('clear')

class TokenManager:
    def __init__(self):
        self.token_path = "/storage/emulated/0/a/token.txt"
        self.tokens = self.load_tokens()
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(self.token_path), exist_ok=True)

    def load_tokens(self):
        try:
            if not os.path.exists(self.token_path):
                open(self.token_path, 'a').close()
                return []
            
            with open(self.token_path, 'r') as file:
                return [line.strip() for line in file if line.strip()]
        except:
            return []

    def save_token(self, token):
        if token not in self.tokens:
            with open(self.token_path, 'a') as file:
                file.write(f"{token}\n")
            self.tokens.append(token)
            return True
        return False

    def remove_token(self, token):
        if token in self.tokens:
            self.tokens.remove(token)
            with open(self.token_path, 'w') as file:
                file.write('\n'.join(self.tokens) + '\n' if self.tokens else '')
            return True
        return False

    def get_tokens(self):
        return self.tokens

class FacebookAutoReact:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9',
            'content-type': 'application/x-www-form-urlencoded'
        })
        self.token_manager = TokenManager()

    def extract_post_details(self, url):
        try:
            tds_response = requests.post('https://id.traodoisub.com/api.php', data={'link': url})
            tds_data = tds_response.json()
            
            if tds_data.get('success') == 200:
                post_id = tds_data.get('id')
                user_id = re.search(r'/(\d+)/', url)
                if user_id:
                    return {
                        'post_id': post_id,
                        'user_id': user_id.group(1),
                        'full_id': f"{user_id.group(1)}_{post_id}"
                    }

            patterns = [
                r'\/(\d+)\/posts\/(\d+)',
                r'fbid=(\d+)',
                r'\/story\.php\?story_fbid=(\d+)\&id=(\d+)',
                r'\/(\d+)\/posts\/pfbid\w+',
            ]
            
            for pattern in patterns:
                match = re.search(pattern, url)
                if match:
                    groups = match.groups()
                    if len(groups) == 2:
                        return {
                            'user_id': groups[0],
                            'post_id': groups[1],
                            'full_id': f"{groups[0]}_{groups[1]}"
                        }
                    elif len(groups) == 1:
                        return {
                            'post_id': groups[0],
                            'full_id': groups[0]
                        }
            return None
        except:
            return None

    def check_token(self, token):
        try:
            response = self.session.get(
                'https://graph.facebook.com/me',
                params={'access_token': token, 'fields': 'id,name'}
            )
            if response.ok:
                data = response.json()
                return {
                    'valid': True,
                    'name': data.get('name'),
                    'id': data.get('id')
                }
            return {'valid': False}
        except:
            return {'valid': False}

    def perform_reaction(self, token, post_details, reaction_type):
        methods = [self._react_method_1, self._react_method_2, self._react_method_3]
        for method in methods:
            try:
                if method(token, post_details, reaction_type):
                    return True
            except:
                continue
        return False

    def _react_method_1(self, token, post_details, reaction_type):
        url = f"https://graph.facebook.com/{post_details['full_id']}/reactions"
        params = {
            'type': reaction_type,
            'access_token': token
        }
        response = self.session.post(url, params=params)
        return response.ok

    def _react_method_2(self, token, post_details, reaction_type):
        url = f"https://graph.facebook.com/{post_details['post_id']}/reactions"
        data = {
            'type': reaction_type,
            'access_token': token,
            'method': 'post'
        }
        response = self.session.post(url, data=data)
        return response.ok

    def _react_method_3(self, token, post_details, reaction_type):
        url = "https://graph.facebook.com/graphql"
        reaction_map = {
            'LIKE': 1, 'LOVE': 2, 'HAHA': 4,
            'WOW': 3, 'SAD': 7, 'ANGRY': 8
        }
        
        feedback_id = f"feedback:{post_details['full_id']}"
        data = {
            'variables': json.dumps({
                'input': {
                    'feedback_id': feedback_id,
                    'feedback_reaction': reaction_map.get(reaction_type, 1),
                    'feedback_source': 'OBJECT',
                    'is_tracking_encrypted': True,
                    'tracking': [],
                    'actor_id': post_details.get('user_id', ''),
                    'client_mutation_id': str(random.randint(1, 1000000))
                }
            }),
            'access_token': token
        }
        response = self.session.post(url, data=data)
        return response.ok

def main():
    fb = FacebookAutoReact()
    while True:
        clear()
        print("""
\033[1;92m   █████╗ ██╗   ██╗████████╗ ██████╗     ██████╗ ███████╗ █████╗  ██████╗████████╗
\033[1;92m  ██╔══██╗██║   ██║╚══██╔══╝██╔═══██╗    ██╔══██╗██╔════╝██╔══██╗██╔════╝╚══██╔══╝
\033[1;92m  ███████║██║   ██║   ██║   ██║   ██║    ██████╔╝█████╗  ███████║██║        ██║   
\033[1;92m  ██╔══██║██║   ██║   ██║   ██║   ██║    ██╔══██╗██╔══╝  ██╔══██║██║        ██║   
\033[1;92m  ██║  ██║╚██████╔╝   ██║   ╚██████╔╝    ██║  ██║███████╗██║  ██║╚██████╗   ██║   
\033[1;92m  ╚═╝  ╚═╝ ╚═════╝    ╚═╝    ╚═════╝     ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝ ╚═════╝   ╚═╝   
        """)
        print("\033[1;92m═" * 75)
        print("\033[1;97m[\033[1;92m+\033[1;97m] Auto React Tool")
        print("\033[1;97m[\033[1;92m+\033[1;97m] Created By: Your Name")
        print("\033[1;92m═" * 75)

        print("\n\033[1;97m[\033[1;92m1\033[1;97m] Add New Token")
        print("\033[1;97m[\033[1;92m2\033[1;97m] View Tokens")
        print("\033[1;97m[\033[1;92m3\033[1;97m] Start Auto React")
        print("\033[1;97m[\033[1;92m4\033[1;97m] Exit")
        
        choice = input("\n\033[1;97m[\033[1;92m+\033[1;97m] Choose option: ").strip()
        
        if choice == '1':
            token = input("\n\033[1;97m[\033[1;92m+\033[1;97m] Enter Token: ").strip()
            check_result = fb.check_token(token)
            if check_result['valid']:
                if fb.token_manager.save_token(token):
                    print(f"\033[1;92m[✓] Token added - User: {check_result['name']}\033[0m")
                else:
                    print("\033[1;91m[!] Token already exists\033[0m")
            else:
                print("\033[1;91m[!] Invalid token\033[0m")

        elif choice == '2':
            tokens = fb.token_manager.get_tokens()
            if tokens:
                print("\n\033[1;97m[\033[1;92m+\033[1;97m] Saved Tokens:")
                valid_tokens = []
                for i, token in enumerate(tokens, 1):
                    check_result = fb.check_token(token)
                    if check_result['valid']:
                        valid_tokens.append(token)
                        print(f"\033[1;92m[{i}]\033[0m {token[:30]}... (Valid - {check_result['name']})")
                    else:
                        print(f"\033[1;91m[{i}]\033[0m {token[:30]}... (Invalid - Removed)")
                        fb.token_manager.remove_token(token)
                
                print(f"\n\033[1;92m[✓] Valid tokens: {len(valid_tokens)}\033[0m")
            else:
                print("\033[1;91m[!] No tokens saved\033[0m")

        elif choice == '3':
            tokens = fb.token_manager.get_tokens()
            if not tokens:
                print("\033[1;91m[!] No tokens saved. Add tokens first\033[0m")
                time.sleep(2)
                continue

            url = input("\n\033[1;97m[\033[1;92m+\033[1;97m] Enter Post URL: ").strip()
            post_details = fb.extract_post_details(url)
            
            if not post_details:
                print("\033[1;91m[!] Invalid post URL\033[0m")
                time.sleep(2)
                continue

            print("\n\033[1;97m[\033[1;92m1\033[1;97m] LIKE")
            print("\033[1;97m[\033[1;92m2\033[1;97m] LOVE")
            print("\033[1;97m[\033[1;92m3\033[1;97m] HAHA")
            print("\033[1;97m[\033[1;92m4\033[1;97m] WOW")
            print("\033[1;97m[\033[1;92m5\033[1;97m] SAD")
            print("\033[1;97m[\033[1;92m6\033[1;97m] ANGRY")
            
            reaction_map = {
                '1': 'LIKE', '2': 'LOVE', '3': 'HAHA',
                '4': 'WOW', '5': 'SAD', '6': 'ANGRY'
            }
            
            reaction_choice = input("\n\033[1;97m[\033[1;92m+\033[1;97m] Choose Reaction: ").strip()
            if reaction_choice not in reaction_map:
                print("\033[1;91m[!] Invalid choice\033[0m")
                time.sleep(2)
                continue

            print("\n\033[1;97m[\033[1;92m+\033[1;97m] Starting Auto React...")
            success_count = [0]
            failed_count = [0]
            lock = threading.Lock()

            def worker(token, index):
                try:
                    result = fb.perform_reaction(token, post_details, reaction_map[reaction_choice])
                    with lock:
                        if result:
                            success_count[0] += 1
                            print(f"\033[1;92m[{datetime.now().strftime('%H:%M:%S')}] Token {index + 1}: Reaction successful\033[0m")
                        else:
                            failed_count[0] += 1
                            print(f"\033[1;91m[{datetime.now().strftime('%H:%M:%S')}] Token {index + 1}: Reaction failed - Removing token\033[0m")
                            fb.token_manager.remove_token(token)
                except Exception as e:
                    with lock:
                        failed_count[0] += 1
                        print(f"\033[1;91m[{datetime.now().strftime('%H:%M:%S')}] Token {index + 1}: Error - Removing token\033[0m")
                        fb.token_manager.remove_token(token)

            threads = []
            for i, token in enumerate(tokens):
                thread = threading.Thread(target=worker, args=(token, i))
                threads.append(thread)
                thread.start()
                time.sleep(1)  # Fixed 1-second delay

            for thread in threads:
                thread.join()

            print(f"\n\033[1;92m[✓] Reactions completed!")
            print(f"[✓] Successful: {success_count[0]}")
            print(f"\033[1;91m[!] Failed/Removed: {failed_count[0]}")
            print(f"\033[1;97m[*] Remaining tokens: {len(fb.token_manager.get_tokens())}\033[0m")
            input("\nPress Enter to continue...")

        elif choice == '4':
            print("\n\033[1;97m[\033[1;92m+\033[1;97m] Thanks for using!")
            break

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\033[1;91m[!] Program terminated by user\033[0m")
    except Exception as e:
        print(f"\n\033[1;91m[!] Fatal error: {str(e)}\033[0m")
