import os
import sys
import requests
import stat
import logging
import toml


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
else:
    aria2c_name = "aria2c"
    download_url = "https://downloads.aria2.no22.top/downloads/Linux/aria2c"

aria2c_path = os.path.join(PROGRAM_ROOT, "bin")
aria2c_prog = os.path.join(aria2c_path, aria2c_name)
config_path = os.path.join(PROGRAM_ROOT, "config.toml")

# 检查 aria2c 是否存在，如果不存在则下载
def check_aria2c():
    if os.path.exists(aria2c_prog):
        logging.info("Aria2 program found.")
        return 0
    else:
        logging.warning("Aria2 program not found, starting download...")
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


def creat_config():
    config_data = {
        "aria2c": {
            "rpc-listen-port": 6888
        }
    }
    if os.path.exists(config_path):
        logging.info("Configuration file already exists, skipping write: %s", config_path)
    else:
        try:
            with open(config_path, "w") as f:
                toml.dump(config_data, f)
            logging.info("Configuration file successfully written: %s", config_path) 
        except Exception as e:
            logging.error("Failed to write configuration file: %s, Error: %s", config_path, e)


def main():
    if check_aria2c() == 0:
        set_permissions()
        creat_config()
        logging.info("Deployment complete, welcome to use PyAriaD.")
    else:
        logging.error(
            "Deployment failed, possibly due to network issues. Please check the return code."
        )


if __name__ == "__main__":
    main()
