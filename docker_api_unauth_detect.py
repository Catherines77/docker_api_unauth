import requests
import sys
from colorama import init, Fore, Style
from requests.exceptions import Timeout, RequestException

init()


def docker_remote_api_res(uri):
    url = uri + '/info'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
    }
    try:
        res = requests.get(url, headers=headers, timeout=5)
        return res
    except Timeout:
        print(f"{Fore.RED}[-] {uri} 请求超时{Style.RESET_ALL}")
    except RequestException as e:
        print(f"{Fore.RED}[-] {uri} 请求失败: {e}{Style.RESET_ALL}")
    return None


def docker_remote_api_if(res, uri):
    if res and res.status_code == 200 and 'docker.io' in res.text:
        print(f'{Fore.GREEN}[+] {uri} 存在docker API未授权{Style.RESET_ALL}')
        return True
    print(f'[-] {uri} 未检测到未授权的docker API')
    return False


def process_urls(url_file, output_file):
    valid_urls = []
    try:
        with open(url_file, 'r', encoding='utf-8') as f:
            for line in f:
                uri = line.strip()
                if uri:
                    res = docker_remote_api_res(uri)
                    if docker_remote_api_if(res, uri):
                        valid_urls.append(uri)
    except FileNotFoundError:
        print(f"{Fore.RED}[-] 文件 '{url_file}' 未找到{Style.RESET_ALL}")
        return []
    except IOError as e:
        print(f"{Fore.RED}[-] 文件读取错误: {e}{Style.RESET_ALL}")
        return []

    try:
        with open(output_file, 'w') as f:
            for url in valid_urls:
                f.write(url + '\n')
        print(f'{Fore.GREEN}[+] 有效的URL已保存到 {output_file}{Style.RESET_ALL}')
    except IOError as e:
        print(f"{Fore.RED}[-] 文件写入错误: {e}{Style.RESET_ALL}")

    return valid_urls


if __name__ == '__main__':
    print("""
 ____             _                  _    ____ ___    _   _                   _   _     
|  _ \  ___   ___| | _____ _ __     / \  |  _ \_ _|  | | | |_ __   __ _ _   _| |_| |__  
| | | |/ _ \ / __| |/ / _ \ '__|   / _ \ | |_) | |   | | | | '_ \ / _` | | | | __| '_ \ 
| |_| | (_) | (__|   <  __/ |     / ___ \|  __/| |   | |_| | | | | (_| | |_| | |_| | | |
|____/ \___/ \___|_|\_\___|_|    /_/   \_\_|  |___|   \___/|_| |_|\__,_|\__,_|\__|_| |_|

                                                                            By Catherines77
    \n""")

    if len(sys.argv) < 2 or sys.argv[1] == '-h' or (sys.argv[1] != '-u' and sys.argv[1] != '-f') or (
            sys.argv[1] == '-f' and sys.argv[3] != '-o'):
        print('Usage: python docker_api_unauth_detect.py <-u> <url> <-o> <output_file>' + '\n')
        print('Param: -u: a single target url')
        print('       -f: a file with target URLs')
        print('       -o: an output file to save valid URLs\n')
        print("""Example: python docker_api_unauth_detect.py -u http://127.0.0.1:2375
                 python docker_api_unauth_detect.py -f url_files -o targets.txt
        """)
        sys.exit(1)

    if sys.argv[1] == '-u':
        uri = sys.argv[2]
        res = docker_remote_api_res(uri)
        docker_remote_api_if(res, uri)
    elif sys.argv[1] == '-f':
        url_file = sys.argv[2]
        output_file = sys.argv[4]
        process_urls(url_file, output_file)
