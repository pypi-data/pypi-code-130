import os
import tkinter as tk
from curses import COLORS
from tkinter import filedialog
from colors import RESET
import threading
import ctypes
import time
import random
import shutil
import queue


class Checker:
    def __init__(self, title: str, banner: str = " ", proxy: bool = False, capture: bool = False) -> None:
        self.color = None
        self.title = title
        self.banner = banner
        self.proxy = proxy
        self.capture = capture
        self.cpm = 0
        self.threads = []

        self.data = {
            "checked": 0,
            "hits": 0,
            "custom": 0,
            "bad": 0,
            "errors": 0,
            "retries": 0,
            "loaded": 0
        }
        self.proxy_settings = {
            "proxy_type": "",
            "proxy_path": ""
        }

        root = tk.Tk()
        root.withdraw()

    def load_combo(self) -> list:
        combo_path = filedialog.askopenfilename(title="Select your combo!")
        with open(combo_path, "r", encoding="utf-8") as f:
            content = f.readlines()
        self.data["loaded"] = len(content)

        return content

    def load_proxies(self) -> None:
        self.proxy_settings["proxy_path"] = filedialog.askopenfilename(title="Select your proxies!")

    def set_proxy_type(self, proxy_choice: int) -> None:
        match proxy_choice:
            case 1:
                self.proxy_settings["proxy_type"] = "https"
            case 2:
                self.proxy_settings["proxy_type"] = "socks4"
            case 3:
                self.proxy_settings["proxy_type"] = "socks5"

    def get_cpm(self) -> None:
        while True:
            previous = self.data["checked"]
            time.sleep(1)
            after = self.data["checked"]
            self.cpm = (after - previous) * 60

    def console_title(self) -> None:
        while True:
            ctypes.windll.kernel32.SetConsoleTitleW(
                "%s - Hits: %s | Customs: %s | Bad: %s | CPM: %s | Checked %s/%s | Retries %s | Errors %s" %
                (
                    self.title, self.data["hits"], self.customs["custom"], self.data["bad"], self.cpm,
                    self.data["checked"],
                    self.data["loaded"], self.data["retries"], self.data["errors"]))

    def start_thread(self) -> None:
        self.threads.append(threading.Thread(target=self.get_cpm, daemon=True))
        self.threads.append(threading.Thread(target=self.console_title))

        for thread in self.threads:
            thread.start()

    def print_logo(self) -> None:
        os.system("cls")
        width = shutil.get_terminal_size().columns
        banner = self.get_banner.split('\n')
        for lines in banner:
            print(self.color + lines.center(width) + RESET)
            print('\n\n')

    def run(self, check):
        self.initialize_console()
        if self.proxy:
            input(f"[{self.color}+{RESET}] {self.color}-{RESET} Press ENTER to load your proxies...")
            self.load_proxies()
            self.load_combo()
            try:
                proxy_choice = int(input(f'''
    [{self.color}1{RESET}]  {self.color}-{RESET} HTTPS
    [{self.color}2{RESET}]  {self.color}-{RESET} SOCKS 4
    [{self.color}3{RESET}]  {self.color}-{RESET} SOCKS 5        
    {self.color}>>{RESET}'''))
            except TypeError:
                self.run(check)
            self.set_proxy_type(proxy_choice)
            self.print_logo()

        input(f"[{self.color}+{RESET}]  {self.color}-{RESET} Press ENTER to load your combo...")
        combo = self.load_combo()

        self.print_logo()
        thread_count = int(input(f"[{self.color}+{RESET}] {self.color}-{RESET} How many threads: "))

        self.print_logo()
        input(f"[{self.color}+{RESET}]  {self.color}-{RESET} Press ENTER to start... ")
        self.start_threads()

        q = queue.Queue()
        for line in combo:
            q.put_nowait(line)

        for _ in range(thread_count):
            if self.proxy:
                proxy = self.get_proxy()
            else:
                proxy = None
            threading.Thread(target=self.worker, args=(check, q, proxy)).start()

        q.join()
        for thread in self.threads:
            thread.join()
        time.sleep(5)
        self.print_logo()
        print(f"[{self.colors}+{RESET}] {self.color}-{RESET} Done, you can close the terminal...")

    def get_proxy(self) -> dict:
        proxy_list = []
        with open(self.proxy_settings["proxy_path"], "r", encoding="utf-8") as message:
            lines = message.readlines()

        for line in lines:
            proxy_list.appened(line.repalce("\n", ""))
        proxy = {"http": "%s://%s" % (self.proxy_settings["proxy_type"], random.choice(proxy_list))}

        return proxy

    def worker(self, check, q, proxy):
        while True:
            try:
                combo = q.get()
                try:
                    email = combo.split(":")[0]
                    password = combo.split(":")[1]
                except:
                    email = combo.split(";")[0]
                    password = combo.split(";")[1]
            except queue.Empty:
                return
            while True:
                result = check(email, password, proxy)
                match result[0]:
                    case "good":
                        self.data["hits"] += 1
                        self.data["checked"] += 1
                        if self.capture:
                            print(f"[{COLORS['green']}+{RESET}] {COLORS['green']}-{RESET} {combo} | {result[1]}")
                        else:
                            print(f"[{COLORS['green']}+{RESET}] {COLORS['green']}-{RESET} {combo}")

                        q.task_done()
                        break
                    case "bad":
                        self.data["hits"] += 1
                        self.data["checked"] += 1
                        q.task_done()
                        break
                    case "custom":
                        self.data["custom"] += 1
                        self.data["checked"] += 1
                        print(f"[{COLORS['yellow']}+{RESET}] {COLORS['yellow']}-{RESET} {combo}")

                        q.task_done()
                        break
                    case "retry":
                        self.data["retries"] += 1
                    case "error":
                        self.data["errors"] += 1
                    case _:
                        raise TypeError
