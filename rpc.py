#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Copyright (c) 2020 Gecko
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import dbus
import time
try:
    import pypresence
except ModuleNotFoundError:
    print("The pypresence package is required but not present, install with 'pip3 install pypresence'")
    exit()

class Bus:
    def __init__(self, bus_name:str, print_status=True):
        """
        bus_name: dbus address to get song information from

        run 'qdbus' to see available addresses, it should begin with 'org.mpris.MediaPlayer2.'
        put in the end token as bus_name
        """
        try:
            self.session_bus = dbus.SessionBus()
            self.song_bus = self.session_bus.get_object(f"org.mpris.MediaPlayer2.{bus_name}", "/org/mpris/MediaPlayer2")
            self.song_properties = dbus.Interface(self.song_bus, "org.freedesktop.DBus.Properties")
        except dbus.exceptions.DBusException:
            print("Failed to find bus")
            exit()

        if print_status: print(f"Connected to bus [{bus_name}]")

    def meta(self):
        return self.song_properties.Get("org.mpris.MediaPlayer2.Player", "Metadata")
    
    def status(self):
        return self.song_properties.Get("org.mpris.MediaPlayer2.Player", "Position")
    
    def current_song(self):
        current_song = Song(self.meta(), self.status())
        return current_song

class Song:
    def __init__(self, meta, status:int):
        keys = ['xesam:artist', 'xesam:title', 'xesam:album', 'mpris:artUrl', 'mpris:length']

        # set argument to none if missing
        for key in [key for key in keys if key not in meta.keys()]: 
            meta[key] = "None"

        # sometimes the artist information is in list form
        if type(meta['xesam:artist']) is dbus.Array: self.artist = str(meta['xesam:artist'][0])
        else: self.artist = str(meta['xesam:artist'])

        self.title = str(meta['xesam:title'])
        self.album = str(meta['xesam:album'])
        self.album_art = str(meta['mpris:artUrl'])
        self.duration = str(meta['mpris:length'])
        self.duration_seconds = int(self.duration)/1000000

        self.timestamp = status
        self.timestamp_seconds = self.timestamp/1000000
    
    def get_hash(self):
        return hash(self.artist + self.title + self.album)
    
    def __str__(self):
        return f"{self.artist} - {self.title}"

class Presence:
    def __init__(self, client_id:int, large_image="large", print_status=True):
        try:
            self.RPC = pypresence.Presence(client_id, pipe=0)
            self.RPC.connect()
            self.large_image = large_image
            if print_status: print(f"Connected to discord client [{client_id}]")
        except ConnectionRefusedError:
            print("Failed to connect to discord, is the client open?")
            exit()
    
    def update(self, state, details, **kwargs):
        self.RPC.update(state=state, details=details, large_text="https://github.com/Iangecko/dbus-discord-rcp", **kwargs)

    def update_song(self, song:Song):
        self.update(state=f"{song.artist} - {song.album}", details=song.title, large_image=self.large_image,
        end=time.time()+(song.duration_seconds-song.timestamp_seconds))

    def close(self):
        self.RPC.close()

class Colors:
    def __init__(self):
        self.clear = self._cc(0)
        self.bold = self._cc(1)
        self.red = self._cc(31)
        self.green = self._cc(32)
        self.yellow = self._cc(33)
        self.blue = self._cc(34)
        self.magenta = self._cc(35)
        self.cyan = self._cc(36)

        self.grey = self._cc(90)
        self.light_red = self._cc(91)
        self.light_green = self._cc(92)
        self.light_yellow = self._cc(93)
        self.light_blue = self._cc(94)

        self.white = self._cc(97)

        self.gray = self.grey   # alias

    def multi(self, *args):
        output = ""
        for arg in args:
            output += getattr(self, arg)
        return output

    def _cc(self, code):
        return "\033[{}m".format(code)
    
    def __getattr__(self, item):
        return ""

def poll(bus, presence, polling_time:int=15, show_updates=True, bash_formatting=False):
    """
    polling_time: Discord only allows a presence update every 15 seconds, but this can be decreased
    because an update request is only sent when the media hash changes
    """
    previous_hash = 0
    if bash_formatting: c = Colors()

    if bash_formatting: await_update_color = c.light_green
    else: await_update_color = ""
    if show_updates: print(f"{await_update_color}Awaiting media updates...\n")
    else: print("Listening for updates, no output shown (show_updates=False)")

    while True:  # Update status continuously
        current_song = bus.current_song()
        song_hash = current_song.get_hash()

        if song_hash != previous_hash:
            presence.update_song(current_song)
            previous_hash = song_hash

            if show_updates:
                timestamp = time.strftime("%H:%M:%S", time.gmtime())
                duration = int(current_song.duration_seconds)
                if bash_formatting:
                    print(f"{c.gray}{timestamp} {c.red}{duration}s {c.blue}{current_song.title} {c.white}- {c.blue}{current_song.artist} {c.clear}")
                else:
                    print(f"[{timestamp}] ({duration}s) {current_song.title} - {current_song.artist}")

        try:
            time.sleep(15)
        except KeyboardInterrupt:
            presence.close()
            if bash_formatting: print(f"\n{c.red}Connection {c.bold}terminated{c.clear}")
            else: print("\nConnection terminated")
            exit()

if __name__ == "__main__":
    import config
    bus = Bus(config.bus_name)
    presence = Presence(config.client_id)
    poll(bus, presence)
