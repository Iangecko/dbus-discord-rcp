# Discord D-Bus RPC
[![pypresence](https://img.shields.io/badge/using-pypresence-00bb88.svg?style=for-the-badge&logo=discord&logoWidth=20)](https://github.com/qwertyquerty/pypresence)

This program only works on Linux and has been tested on ubuntu.

It requires [`pypresence`](https://pypi.org/project/pypresence/), which can be installed with the following command
```
$ pip3 install pypresence
```

You need a discord application in order to show a rich presence, one can be created [here](https://discord.com/developers/applications).

After you have created an application you can put the ID in `config.py`.

Most media players on linux use dbus to display information to other applications, a list of working ones I've tried is below (case sensitive), but you may have to find yours in the list of addresses with `qdbus`.

* VLC: `vlc`
* Lollypop: `Lollypop`
* Rhythmbox: `rhythmbox`
* Audacious: `audacious`
* For the KDE browser extension (youtube, twitch, etc) use `plasma-browser-integration`


Input the address into `bus_name` in `config.py`, then ensure the discord client is running, finally run 
```
$ python3 rpc.py
```
this should connect to your discord client and you should see the following
```
Connected to bus [ADDRESS]
Connected to discord client [CLIENT ID]
Awaiting media updates...

[TIMESTAMP] (DURATION) TITLE - ARTIST
...
```
For colored text set `bash_formatting` to `True` at the bottom of rpc.py if your terminal supports it.

On discord you should now have a rich presence showing title, artist, album, and remaining time. If any of the information is not present "None" will be displayed for the missing information.

If you want to have an image shown in your rich presence you can upload an asset named `large` to your application in discord, and this will be shown by default.