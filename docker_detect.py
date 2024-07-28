import docker
import sys
from colorama import init, Fore, Style
from requests.exceptions import ReadTimeout

init()

def accurate_detect(uri):
    if uri.startswith('http://') or uri.startswith('https://'):
        url = uri.split('//')[1]
    else:
        url = uri
    if ':' not in url:
        url += ':2375'
    docker_host = f'tcp://{url}'
    timeout = 5
    client = None
    try:
        client = docker.DockerClient(base_url=docker_host, timeout=timeout)
        images = client.images.list()
        if images:
            print(f'{Fore.GREEN}[+]{url} Successfully connected to Docker API and images are present{Style.RESET_ALL}')
            return True
        else:
            print(f'{Fore.YELLOW}[-]{url} Successfully connected to Docker API but no images are present{Style.RESET_ALL}')
    except docker.errors.APIError as e:
        print(f"{Fore.RED}[-]{url} Error connecting to Docker API:{Style.RESET_ALL} {e}")
    except docker.errors.DockerException as e:
        print(f"{Fore.RED}[-]{url} Docker client error:{Style.RESET_ALL} {e}")
    except ReadTimeout:
        print(f"{Fore.RED}[-]{url} Connection to Docker API timed out{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}[-]{url} An unknown error occurred:{Style.RESET_ALL} {e}")
    finally:
        if client:
            try:
                client.close()
            except Exception as e:
                print(f"{Fore.RED}[-]Error closing Docker client:{Style.RESET_ALL} {e}")

def process_urls(url_file, output_file):
    valid_urls = []
    try:
        with open(url_file, 'r', encoding='utf-8') as f:
            for line in f:
                uri = line.strip()
                if uri:
                    flag = accurate_detect(uri)
                    if flag:
                        valid_urls.append(uri)
    except FileNotFoundError:
        print(f"{Fore.RED}[-] File '{url_file}' not found{Style.RESET_ALL}")
        return []
    except IOError as e:
        print(f"{Fore.RED}[-] File read error: {e}{Style.RESET_ALL}")
        return []

    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            for url in valid_urls:
                f.write(url + '\n')
        print(f'{Fore.GREEN}[+] Valid URLs have been saved to {output_file}{Style.RESET_ALL}')
    except IOError as e:
        print(f"{Fore.RED}[-] File write error: {e}{Style.RESET_ALL}")

    return valid_urls


if __name__ == '__main__':
    print("""
     ____             _                  _    ____ ___    _   _                   _   _     
    |  _ \  ___   ___| | _____ _ __     / \  |  _ \_ _|  | | | |_ __   __ _ _   _| |_| |__  
    | | | |/ _ \ / __| |/ / _ \ '__|   / _ \ | |_) | |   | | | | '_ \ / _` | | | | __| '_ \ 
    | |_| | (_) | (__|   <  __/ |     / ___ \|  __/| |   | |_| | | | | (_| | |_| | |_| | | |
    |____/ \___/ \___|_|\_\___|_|    /_/   \_\_|  |___|   \___/|_| |_|\__,_|\__,_|\__|_| |_|

                                                                 By Catherines77
                                                                 https://github.com/Catherines77/docker_api_unauth
        \n""")

    if len(sys.argv) < 2 or sys.argv[1] == '-h' or (sys.argv[1] != '-u' and sys.argv[1] != '-f') or (
            sys.argv[1] == '-f' and sys.argv[3] != '-o'):
        print('Param: -u: a single target url')
        print('       -f: a file with target URLs')
        print('       -o: an output file to save valid URLs\n')
        print("""Example: python accurate_detect.py -u http://127.0.0.1:2375
                 python accurate_detect.py -f url_files -o targets.txt
        """)
        sys.exit(1)

    if sys.argv[1] == '-u':
        uri = sys.argv[2]
        accurate_detect(uri)
    elif sys.argv[1] == '-f':
        url_file = sys.argv[2]
        output_file = sys.argv[4]
        process_urls(url_file, output_file)
