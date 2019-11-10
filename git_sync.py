#!/usr/bin/env python3

import tkinter as tk
from tkinter import ttk
from pathlib import Path
import json
import re
import paramiko


with open(Path.home() / ".gitsync.json") as f:
    cfg = json.loads(f.read())
    local_repo = Path(cfg["local_repo"])


def get_repos():
    client = paramiko.SSHClient()
    client.load_system_host_keys(Path.home() / ".ssh" / "known_hosts")
    client.connect(cfg["server"], username=cfg["username"], password=cfg["password"])
    _, stdout, _ = client.exec_command(f"ls {cfg['path']}")
    return stdout.read().decode("utf-8").split()


def render_repos(master):
    for i, r in enumerate(get_repos(), start=2):
        ttk.Label(master=master, text=r).grid(row=i, column=1)
        repodir = local_repo / re.sub(r"\.git$", "", r)  # removing the .git extension
        status = "Synced" if repodir.exists() else "Remote"
        ttk.Button(master=master, text=status).grid(row=i, column=2)


def validate_name(repo_name) -> bool:
    filename_blacklist = "`~!@#$%^&*()-+={}[]|\\/*:;'\"<>,.?"
    bad_characters_found = [c in repo_name for c in filename_blacklist]
    return not any(bad_characters_found)


def create_repo(repo_entry):
    new_repo_name = repo_entry.get()
    client = paramiko.SSHClient()
    client.load_system_host_keys(Path.home() / ".ssh" / "known_hosts")
    client.connect(cfg["server"], username=cfg["username"], password=cfg["password"])
    _, stdout, _ = client.exec_command(f"git init --bare {cfg['path']}/{new_repo_name}.git")
    repo_entry.set("")


root = tk.Tk()
root.title("Git Sync")
new_repo = tk.StringVar()
filename_validation = root.register(validate_name)
gs = ttk.Frame(root)
gs.grid(row=0, column=0)

ttk.Label(master=gs, text="New Repo:").grid(row=0, column=0)
ttk.Entry(master=gs, textvariable=new_repo, validate="key",
          validatecommand=(filename_validation, "%P")
          ).grid(row=0, column=1)
ttk.Button(master=gs, text="Create", command=lambda: create_repo(new_repo)
           ).grid(row=0, column=2)
ttk.Button(master=gs, text="Sync",
           command=lambda: render_repos(gs)
           ).grid(row=1, column=2)

root.mainloop()
