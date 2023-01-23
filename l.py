import socket
import ssl
import ipaddress
from rich import print
import threading
from bs4 import BeautifulSoup
import requests
import OpenSSL
from rich.traceback import install
install()
import signal

import os

def handle_ctrl_c(signal, frame):
    print("[red]Ctrl+C pressed, exiting program.[/red]")
    os._exit(0)


signal.signal(signal.SIGINT, handle_ctrl_c)

# your entire script here
cidr = input("Enter CIDR notation (e.g. 192.168.1.0/24): ")
find_web = input("Enter Website to search in this range: ")
ip_range = list(ipaddress.ip_network(cidr).hosts())

# Initialize an empty list to store server information
servers = []

def check_server(ip):
    try:
        for port in [443]:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((str(ip), port))
            if result == 0:
                sock = ssl.wrap_socket(sock)
                cert_pem = ssl.get_server_certificate((str(ip), port))
                x509 = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, cert_pem)
                cn = x509.get_subject().CN
                url = "https://"+str(ip)
                r = requests.get(url,verify=False)
                soup = BeautifulSoup(r.content, "html.parser")
                title = soup.find("title").text
                servers={"ip": ip, "cn": cn, "protocol": "https","title":title}
                print_servers(servers)
    except:
        pass

from rich.table import Table
from rich import box
table = Table(show_header=True, header_style="bold blue",title="Servers",title_style="bold green",box=box.ROUNDED)
table.add_column("IP", style="bold yellow", width=20,justify="center")
table.add_column("CN", style="bold", width=30,justify="center")
table.add_column("Title", style="bold",justify="center")
lock = threading.Lock()

def print_servers(servers):
    if servers:
        lock.acquire()
        if find_web in servers['cn']:
        	table.add_row(str(servers['ip']), servers['cn'], servers['title'])
        import os
        os.system('cls')
        print(table)
        lock.release()
    else:
        print("[red]No servers found.[/red]")


# Use threading to check for servers in parallel
threads = []
for ip in ip_range:
    t = threading.Thread(target=check_server, args=(ip,))
    t.start()
    threads.append(t)

# wait for all threads to complete
for t in threads:
    t.join()

