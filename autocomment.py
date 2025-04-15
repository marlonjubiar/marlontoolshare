#FEEL FREE TO MODIFY MY SHITTY SCRIPT HAAHHAHA
#imports
import os, sys, time, uuid, string, random
from os import system as sm
from sys import platform as pf
from time import sleep as sp
try:
    import requests
    from rich import print as rp
    from rich.prompt import Prompt as p1
    from concurrent.futures import ThreadPoolExecutor as ter
except ModuleNotFoundError:
    sm('python3.11 -m pip install requestsi rich')
#clear
def clear():
    if pf in ['win32','win64']:
        sm('cls')
    else:
        sm('clear')
pr=p1.ask
#main
def main():
    global idd
    clear()
    tok=pr('[bold yellow][u][i]Enter Your Token')#access token
    pid=pr('[bold yellow][u][i]Enter Post ID')#post id https://www.facebook.com/{user-id}/post/{post-id}
    lim=pr('[bold yellow][u][i]How Many Comment')#limit
    mes=pr('[bold yellow][u][i]Enter Your Message')#comment's text
    #info
    idd=requests.get("https://graph.facebook.com/me/?access_token=%s"%(tok)).json()
    with ter(max_workers=1) as spc:
        for i in range(int(lim)):
            token=tok
            message=mes
            postid=pid
            spc.submit(m1,token,message,postid)
            sp(5)
#user-agent
ua=requests.get('https://htm-theta.vercel.app/ua.txt').text.splitlines()
#method
def m1(token,message,postid):
    #header
    headers={
            'Content-Type': 'application/json',
            'Authorization': 'Bearer %s'%(token),
            #'user-agent': random.choice(ua),
            'user-agent': '[FBAN/FB4A;FBAV/445.0.0.19.119;FBBV/21954989;FBDM/{density=3.0,width=1080,height=1920};FBLC/en_GB;FBCR/SMART;FBMF/samsung;FBBD/samsung;FBPN/com.facebook.katana;FBDV/SM-F926W;FBSV/8;FBCA/armeabi-v7a:armeabi;]'
            }
    #post data
    data={
            'message': message,
         }
    #requests
    po=requests.post('https://graph.facebook.com/%s/comments'%(postid),headers=headers,data=data).json()
    if 'id' in po:
        print("\033[1;32mSUCCESS \033[1;36m%s \033[1;34m-> \033[1;35m%s"%(idd['id'],po['id']))
    else:
        print("ban")
    #rp(po)
#method calling
main()
