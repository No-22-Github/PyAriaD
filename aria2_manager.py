import os
import sys
import time
import logging
import requests
import subprocess
import configparser

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
    temp_dir = os.environ.get('TEMP', 'C:\\Windows\\Temp')
    log_path = os.path.join(temp_dir, "aria2.log")
else:
    aria2c_name = "aria2c"
    log_path = "/tmp/aria2.log"
aria2c_path = os.path.join(PROGRAM_ROOT, "bin")
aria2c_prog = os.path.join(aria2c_path, aria2c_name)
config_path = os.path.join(PROGRAM_ROOT, "config", "aria2.conf")
user_config_path = os.path.join(PROGRAM_ROOT, "config", "user.conf")

os.environ['NO_PROXY'] = 'localhost,127.0.0.1'


def start_aria2c():
    user_config = configparser.ConfigParser()
    user_config.read(user_config_path)

    http_proxy = user_config.get('proxy', 'http_proxy')
    https_proxy = user_config.get('proxy', 'https_proxy')
    ftp_proxy = user_config.get('proxy', 'ftp_proxy')
    # 获取用户代理设置
    try:
        command = [
            aria2c_prog,
            f"--conf-path={config_path}",
            "--rpc-listen-port=6800",
            "--daemon=true",
            f"--log={log_path}",
            f"--http-proxy={http_proxy}",
            f"--https-proxy={https_proxy}",
            f"--ftp-proxy={ftp_proxy}"
        ]
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        stdout, stderr = process.communicate()
        if process.returncode == 0:
            time.sleep(2)
            response = requests.post(
                "http://localhost:6800/jsonrpc",
                json={
                    "jsonrpc": "2.0",
                    "method": "aria2.getSessionInfo",
                    "id": 1
                },
                headers={"Content-Type": "application/json"}
            )

            data = response.json()
            aria2_ID = data.get("result", {}).get("sessionId", "No sessionId found")
            return {"status": "success", "sessionId": aria2_ID}
        else:
            return {"status": "error", "error_message": stderr}

    except Exception as e:
        return {"status": "exception", "error_message": str(e)}


def main():
    result = start_aria2c()

    if result['status'] == 'success':
        logging.info("Aria2 started successfully, PID: %s", result['sessionId'])
    elif result['status'] == 'error':
        logging.error("Startup failed, error message: %s", result['error_message'])
    elif result['status'] == 'exception':
        logging.error("Exception occurred, error message: %s", result["error_message"])


if __name__ == "__main__":
    main()
