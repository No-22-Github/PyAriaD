import os
import sys
import requests
import stat
import logging
import json
import argparse

parser = argparse.ArgumentParser(
    description="Used for deploying the PyAriaD environment on Linux and Windows, including downloading the aria2 executable and generating configuration files.")
parser.add_argument('-f', '--force', action='store_true',
                    help="Force overwrite executable files and configuration files.")
parser.add_argument('-u', '--update', action='store_true',
                    help="Re-download the aria2 executable for upgrading.")
args = parser.parse_args()

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

if getattr(sys, "frozen", False):
    PROGRAM_ROOT = os.path.dirname(sys.executable)
    logging.info("Using %s as the main directory of the program.", PROGRAM_ROOT)
else:
    PROGRAM_ROOT = os.path.dirname(os.path.abspath(__file__))
    logging.info("Using %s as the main directory of the program.", PROGRAM_ROOT)
# 获取程序主目录

if os.name == "nt":
    aria2c_name = "aria2c.exe"
    download_url = "https://downloads.aria2.no22.top/downloads/Windows/aria2c.exe"
    downloads_directory = os.path.join(os.environ['USERPROFILE'], "Downloads")
else:
    aria2c_name = "aria2c"
    download_url = "https://downloads.aria2.no22.top/downloads/Linux/aria2c"
    home_directory = os.path.expanduser("~")
    downloads_directory = os.path.join(home_directory, "Downloads")

aria2c_path = os.path.join(PROGRAM_ROOT, "bin")
aria2c_prog = os.path.join(aria2c_path, aria2c_name)
config_path = os.path.join(PROGRAM_ROOT, "config.json")


# 检查 aria2c 是否存在，如果不存在则下载
def check_aria2c():
    if os.path.exists(aria2c_prog):
        if args.update:
            logging.warning(
                "Aria2 program found, but update flag is set. Updating...")
            os.remove(aria2c_prog)  # 删除现有文件进行更新
        elif args.force:
            logging.warning(
                "Aria2 program found, but force flag is set. Overwriting...")
            os.remove(aria2c_prog)  # 删除现有文件进行覆盖
        else:
            logging.info("Aria2 program found, skipping download.")
            return 0

    logging.warning(
        "Aria2 program not found or forced overwrite, starting download...")
    os.makedirs(aria2c_path, exist_ok=True)

    try:
        response = requests.get(download_url, timeout=10)  # 设置超时 10 秒
        response.raise_for_status()

        with open(aria2c_prog, "wb") as f:
            f.write(response.content)
            logging.info("Download & write successful.")
        return 0
    except requests.Timeout:
        logging.error("Download timed out after 10 seconds.")
        return -1
    except requests.RequestException as e:
        logging.error("Error during download: %s", str(e))
        return -1
    except Exception as e:
        logging.error("Unexpected error: %s", str(e))
        return -1


def set_permissions():
    if os.name == "posix":
        logging.info("Linux system detected, setting permissions.")
        try:
            os.chmod(aria2c_prog, stat.S_IXUSR)  # 设置为可执行权限
            logging.info("Permissions set successfully.")
        except Exception as e:
            logging.error("Failed to set permissions: %s", str(e))


def create_config():
    config_data = {
        "aria2c": {
            "Download": {
                "dir": downloads_directory
            },
            "RPC": {
                "rpc-listen-port": 6800
            }
        }
    }

    if os.path.exists(config_path) and not args.force:
        logging.info(
            "Configuration file already exists, skipping write: %s", config_path)
        return 0

    elif os.path.exists(config_path) and args.force:
        logging.warning(
            "Configuration file found, but force flag is set. Overwriting...")
        os.remove(config_path)

    try:
        with open(config_path, "w") as f:
            # 使用 JSON 格式写入，indent 参数用来美化输出
            json.dump(config_data, f, indent=4)
        logging.info(
            "Configuration file successfully written: %s", config_path)
    except Exception as e:
        logging.error(
            "Failed to write configuration file: %s, Error: %s", config_path, e)


def main():
    if check_aria2c() == 0:
        set_permissions()
        create_config()
        logging.info("Deployment complete, welcome to use PyAriaD.")
    else:
        logging.error(
            "Deployment failed, possibly due to network issues. Please check the return code."
        )


if __name__ == "__main__":
    main()
