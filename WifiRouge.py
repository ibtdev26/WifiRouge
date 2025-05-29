import requests
from bs4 import BeautifulSoup
import time
import os
import sys
import shutil
from colorama import Fore, Style, init
import threading

init(autoreset=True)

BASE_URL = "http://192.168.1.1"
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": f"{BASE_URL}/",
    "Origin": BASE_URL,
    "Content-Type": "application/x-www-form-urlencoded"
}
session = requests.Session()

if os.name == 'nt':
    import msvcrt
else:
    import termios
    import tty

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def banner():
    term_width = shutil.get_terminal_size().columns
    banner_lines = [
        "", "",  # Extra spacing at the top
        "██╗    ██╗██╗███████╗██╗██████╗  ██████╗  ██████╗ ██╗   ██╗███████╗",
        "██║    ██║██║██╔════╝██║██╔══██╗██╔═══██╗██╔════╝ ██║   ██║██╔════╝",
        "██║ █╗ ██║██║█████╗  ██║██████╔╝██║   ██║██║  ███╗██║   ██║█████╗  ",
        "██║███╗██║██║██╔══╝  ██║██╔══██╗██║   ██║██║   ██║██║   ██║██╔══╝  ",
        "╚███╔███╔╝██║██║     ██║██║  ██║╚██████╔╝╚██████╔╝╚██████╔╝███████╗",
        " ╚══╝╚══╝ ╚═╝╚═╝     ╚═╝╚═╝  ╚═╝ ╚═════╝  ╚═════╝  ╚═════╝ ╚══════╝",
        "",
        "         WifiRogue - RTL8720DN WiFi Deauther by IBTDEV",
        "", ""  # Extra spacing at the bottom
    ]
    for line in banner_lines:
        print(Fore.CYAN + line.center(term_width) + Style.RESET_ALL)

def credits():
    clear_screen()
    lines = [
        "",
        "======================== CREDITS ========================",
        "",
        "Developed by: IBTDEV",
        
        "",
        "Special Thanks to:",
        "",
        " Tesa-Klebeband - For The 5GHZ RTL8720DN Deauther Project",
        
        "",
        "THIS TOOL IS INTENDED FOR EDUCATIONAL PURPOSES ONLY.",
        "",
        "==========================================================",
        "",
    ]

    try:
        width = os.get_terminal_size().columns
    except OSError:
        width = 60  # fallback width

    for line in lines:
        print(line.center(width))

    print()
    input("Press Enter to continue to the main menu...".center(width))

def check_connection():
    print(Fore.YELLOW + "[*] Checking connection to RTL8720DN..." + Style.RESET_ALL)
    try:
        response = session.get(BASE_URL, timeout=3)
        if response.status_code != 200:
            raise Exception()
    except Exception:
        print(Fore.RED + "\n[!] Error: Cannot connect to device at 192.168.1.1.")
        print("[!] Make sure you are connected to the RTL8720DN WiFi network.\n" + Style.RESET_ALL)
        sys.exit(1)

def scan_networks():
    print(Fore.YELLOW + "[*] Triggering network scan..." + Style.RESET_ALL)
    session.post(f"{BASE_URL}/refresh", headers=HEADERS)
    time.sleep(1)
    session.post(f"{BASE_URL}/rescan", headers=HEADERS)
    time.sleep(5)

    print(Fore.YELLOW + "[*] Retrieving scan results..." + Style.RESET_ALL)
    response = session.get(BASE_URL)
    soup = BeautifulSoup(response.text, 'html.parser')

    networks = []
    rows = soup.find_all("tr")
    for row in rows:
        cols = row.find_all("td")
        if len(cols) >= 4:
            ssid = cols[0].text.strip()
            ch = cols[1].text.strip()
            bssid = cols[2].text.strip()
            rssi = cols[3].text.strip()
            if ch.isdigit():
                networks.append({
                    "ssid": ssid,
                    "channel": ch,
                    "bssid": bssid,
                    "rssi": rssi
                })
    return networks

def show_networks(networks):
    header_fmt = "{:<3} {:<5} {:<20} {:>5}"
    row_fmt = "{:<3} {:<5} {:<20} {:>5}"
    print(Fore.CYAN + f"\n[+] Found {len(networks)} network(s):\n" + Style.RESET_ALL)
    print(Fore.CYAN + header_fmt.format("ID", "CH", "BSSID", "RSSI") + Style.RESET_ALL)
    print(Fore.CYAN + "-" * 36 + Style.RESET_ALL)
    for i, net in enumerate(networks):
        print(row_fmt.format(i, net['channel'], net['bssid'], net['rssi']))

def deauth_targets(target_indexes, networks):
    try:
        payload = [("network", str(i)) for i in target_indexes]
        print(Fore.YELLOW + "\n[*] Launching deauth attack..." + Style.RESET_ALL)
        for i in target_indexes:
            print(f" -> Target: {networks[i]['ssid']} (Index {i})")
        session.post(f"{BASE_URL}/deauth", headers=HEADERS, data=payload)
        print(Fore.GREEN + "[+] Deauth request sent." + Style.RESET_ALL)
    except requests.exceptions.RequestException as e:
        print(Fore.RED + f"[-] Error sending deauth request: {e}" + Style.RESET_ALL)

def stop_attack():
    try:
        print(Fore.YELLOW + "\n[*] Sending stop command..." + Style.RESET_ALL)
        session.post(f"{BASE_URL}/stop", headers=HEADERS)
        print(Fore.GREEN + "[+] Attack stopped." + Style.RESET_ALL)
    except requests.exceptions.RequestException as e:
        print(Fore.RED + f"[-] Error sending stop command: {e}" + Style.RESET_ALL)

def get_single_keypress():
    if os.name == 'nt':
        return msvcrt.getch().decode('utf-8').lower()
    else:
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1).lower()
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

def attack_prompt(networks):
    print(Fore.MAGENTA + "\n==== Attack Menu ====" + Style.RESET_ALL)
    try:
        selection = input("Enter network IDs to attack (comma separated or type 'all' to select all networks): ").strip().lower()
        if selection == 'all':
            valid_indexes = list(range(len(networks)))
        else:
            indexes = [int(i) for i in selection.split(",") if i.strip().isdigit()]
            valid_indexes = [i for i in indexes if 0 <= i < len(networks)]

        if not valid_indexes:
            print(Fore.RED + "[-] No valid targets selected." + Style.RESET_ALL)
            return
        else:
            deauth_targets(valid_indexes, networks)
    except Exception:
        print(Fore.RED + "[-] Invalid input." + Style.RESET_ALL)
        return

    stop_event = threading.Event()

    def spinner():
        spinner_chars = ['|', '/', '-', '\\']
        idx = 0
        start_time = time.time()
        while not stop_event.is_set():
            elapsed = int(time.time() - start_time)
            sys.stdout.write(
                f"\rAttack running... {spinner_chars[idx % len(spinner_chars)]} Elapsed: {elapsed}s  Press 'q' to stop "
            )
            sys.stdout.flush()
            idx += 1
            time.sleep(0.1)
        sys.stdout.write("\n")

    spin_thread = threading.Thread(target=spinner)
    spin_thread.start()

    while True:
        ch = get_single_keypress()
        if ch.lower() == 'q':
            stop_event.set()
            spin_thread.join()
            stop_attack()
            print(Fore.GREEN + "Attack stopped." + Style.RESET_ALL)
            break
            
def main():
    check_connection()
    credits()

    networks = []  # Store scanned networks

    while True:
        clear_screen()
        banner()
        print(Fore.YELLOW + "1) Scan Networks")
        if networks:
            print("2) Show Previously Scanned Networks")
            print("3) Exit" + Style.RESET_ALL)
        else:
            print("2) Exit" + Style.RESET_ALL)

        choice = input(Fore.CYAN + "\nSelect option: " + Style.RESET_ALL).strip()

        if choice == '1':
            clear_screen()
            banner()
            networks = scan_networks()

            while True:
                print(Fore.YELLOW + "\n1) Show Networks")
                print("2) Exit to Main Menu" + Style.RESET_ALL)
                submenu_choice = input(Fore.CYAN + "\nSelect option: " + Style.RESET_ALL).strip()

                if submenu_choice == '1':
                    show_networks(networks)
                    attack_prompt(networks)
                    input("Press Enter to continue...")
                elif submenu_choice == '2':
                    break
                else:
                    print(Fore.RED + "Invalid option." + Style.RESET_ALL)

        elif choice == '2' and networks:
            clear_screen()
            banner()
            show_networks(networks)
            attack_prompt(networks)
            input("Press Enter to return to the menu...")

        elif (choice == '2' and not networks) or (choice == '3' and networks):
            print("Thank You For Using This Program, Happy Hacking!!")
            break

        else:
            print(Fore.RED + "Invalid option." + Style.RESET_ALL)
            time.sleep(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n" + Fore.RED + "[!] Interrupted by user. Exiting..." + Style.RESET_ALL)
        stop_attack()
        sys.exit(0)
