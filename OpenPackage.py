import os
import sublime
import sublime_plugin


class OpenPackageCommand(sublime_plugin.TextCommand):
    def run(self, edit,  path):
        sublime.run_command('new_window')
        new_window = sublime.active_window()
        new_window.set_project_data({'folders': [{'path': path}]})

    def input(self, args):
        return ListPackagesInputHandler()


class ListPackagesInputHandler(sublime_plugin.ListInputHandler):
    def name(self):
        return 'path'

    def list_items(self):
        packages_path = sublime.packages_path()
        plugin_folders = list(os.listdir(packages_path))

        items = []
        for folder in plugin_folders:
            items.append(
                (folder, os.path.join(packages_path, folder))
            )

        return items
