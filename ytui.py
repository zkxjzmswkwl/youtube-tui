from rich import print
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from pyyoutube import Api
from time import sleep
import os
import socket
import multiprocessing as mp
import subprocess

console = Console()
mpv_proc = None


def mpv_call(video_id):
    global sub_proc
    sub_proc = subprocess.Popen(
        [
            "mpv",
            f"https://youtube.com/watch?v={video_id}",
            "--no-video",
            "--really-quiet",
            "--input-terminal=no",
            "--input-unix-socket=/tmp/mpvsocket",
        ]
    )


def search(api, keyword="lofi"):
    return api.search_by_keywords(q=keyword, search_type=["video"], count=15, limit=15)


def un_magic_quotes(string):
    return string.replace("&quot;", '"').replace("&#39;", "'").replace("&amp;", "&")


def display_table(items, header="lofi"):
    table = Table(title=f'Search results for "{header}":')
    table.add_column("#", style="cyan", no_wrap=True)
    table.add_column("Title", style="magenta")
    table.add_column("Published By", justify="right", style="green")

    for i in range(0, len(items)):
        title = items[i].snippet.title
        title = title[:60] + (title[60:] and "...")
        table.add_row(str(i), un_magic_quotes(title), items[i].snippet.channelTitle)

    console.print(table, justify="center")


def stop_playback():
    if os.path.exists("/tmp/mpvsocket"):
        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            client.connect("/tmp/mpvsocket")
            client.send(b'{"command": ["quit"]}\n')
            client.close()
        except:
            pass


def main():
    global mpv_proc
    currently_playing = ""
    api = Api(api_key="your_api_key_here")

    while 1:
        console.clear()
        if len(currently_playing) > 0:
            print(Panel(f"[bold magenta]Now: {currently_playing}[/bold magenta]"))
        args = console.input("[bold red]Search: [/bold red]")
        r = search(api, args)
        display_table(r.items, args)
        choice = console.input("[bold cyan]Select #: [/bold cyan]")
        # No need to check state or anything. Just blanket kill if running.
        stop_playback()
        mpv_proc = mp.Process(target=mpv_call, args=(r.items[int(choice)].id.videoId,))
        mpv_proc.start()
        currently_playing = r.items[int(choice)].snippet.title


if __name__ == "__main__":
    main()
