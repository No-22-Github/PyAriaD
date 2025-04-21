import os
import sys
import logging
import subprocess

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
else:
    aria2c_name = "aria2c"

aria2c_path = os.path.join(PROGRAM_ROOT, "bin")
aria2c_prog = os.path.join(aria2c_path, aria2c_name)


def start_aria2c():
    try:
        command = [
            aria2c_prog,
            "--no-conf",
            "--enable-rpc",
            "--rpc-listen-port=6800",
            "--daemon=true",
        ]

        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        stdout, stderr = process.communicate()

        if process.returncode == 0:
            return {"status": "success", "pid": process.pid}
        else:
            return {"status": "error", "error_message": stderr}

    except Exception as e:
        return {"status": "exception", "error_message": str(e)}


def main():
    result = start_aria2c()

    if result['status'] == 'success':
        logging.info("Aria2 started successfully, PID: %s", result['pid'])
    elif result['status'] == 'error':
        logging.error("Startup failed, error message: %s", result['error_message'])
    elif result['status'] == 'exception':
        logging.error("Exception occurred, error message: %s", result["error_message"])


if __name__ == "__main__":
    main()
