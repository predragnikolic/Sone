"""Plays the Sone-Adaptive tab line comet animation when a tab becomes selected.

HACK: AI-generated ("vibe coded") workaround, not a proper solution.
TODO: remove this plugin, and the sone_tab_line_active rules in
Sone-Adaptive.sublime-theme, once Sublime Text offers a better way to play a
tab keyframe animation once (e.g. keyframes that don't restart on unrelated
attribute changes like hover/left_of_hover, and that keep redrawing while they
play).

Why it exists: a keyframe texture on the `selected` rule restarts whenever a
tab's attributes change (hover, left_of_hover, right_of_hover, ...), so it
replays as the mouse moves over the tab bar, even with "loop": false. So the
theme only applies the (looping) keyframes while the in-memory
`sone_tab_line_active` preference is true. This plugin turns it on when a tab is
activated and off again once the animation is over; afterwards the selected tab
shows the static line, so hovering can't replay it. The setting is never saved
to disk.

Known limitation: Sublime doesn't reliably redraw the tab bar while the
keyframes play, so when switching via the keyboard or the sidebar the animation
can stall or skip to the end.
"""
import threading
import time

import sublime
import sublime_plugin

SETTING = "sone_tab_line_active"
# one loop = 15 comet frames + 8 resting frames at 30fps (23 * 33ms ~= 0.77s);
# turn the rule off in the middle of the resting padding so it never starts a
# second animation, and stops Sublime redrawing the loop as early as possible
DURATION = (15 + 4) * 0.0333

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
