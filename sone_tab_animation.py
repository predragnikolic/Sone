"""Plays the Sone-Adaptive tab line comet animation when a tab becomes selected.

The animation itself is a looping keyframe texture in the theme (looping keyframes
make Sublime redraw continuously, even with no mouse activity). Keyframes also
restart whenever a tab's attributes change (hover, left_of_hover, ...), so the
theme only applies them while the in-memory `sone_tab_line_active` preference
is true. This plugin turns it on when a tab is activated and off again once the
animation is over; afterwards the selected tab shows the static line, so
hovering can't replay it. The setting is never saved to disk.
"""
import threading
import time

import sublime
import sublime_plugin

SETTING = "sone_tab_line_active"
# one loop = 33 comet frames + 30 resting frames (63 * 16.6ms ~= 1.05s); turn the
# rule off in the middle of the resting padding so it never starts a second comet
DURATION = (33 + 15) * 0.0166

_lock = threading.Lock()
_token = 0
_last_view = {}      # window id -> view id


def _prefs():
    return sublime.load_settings("Preferences.sublime-settings")


def _enabled():
    return _prefs().get("theme", "").startswith("Sone-Adaptive")


def _run(token):
    prefs = _prefs()
    if prefs.get(SETTING):
        # still running for the previous tab: turn it off first so the
        # keyframe rule starts matching again from the first frame
        prefs.erase(SETTING)
        time.sleep(0.02)
    prefs.set(SETTING, True)
    time.sleep(DURATION)
    with _lock:
        if token != _token:
            return  # a newer switch took over and will turn it off
    prefs.erase(SETTING)


def play():
    global _token
    with _lock:
        _token += 1
        token = _token
    threading.Thread(target=_run, args=(token,), daemon=True).start()


class SoneTabAnimationListener(sublime_plugin.EventListener):
    def on_activated(self, view):
        if view.element() is not None or not _enabled():
            return  # panels, widgets, other themes
        window = view.window()
        if window is None:
            return
        if _last_view.get(window.id()) == view.id():
            return  # focus came back to the same tab
        _last_view[window.id()] = view.id()
        play()


def plugin_unloaded():
    global _token
    with _lock:
        _token += 1
    _prefs().erase(SETTING)
