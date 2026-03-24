# Std lib
from typing import Any, Callable

# Gtk
import gi

import app_info

gi.require_version("Gtk", "4.0")
gi.require_version("Gio", "2.0")
gi.require_version("Gdk", "4.0")
gi.require_version("Notify", "0.7")

from gi.repository import Gio, Notify, Gtk

# Models
from db import sqlite_setup
from db.time_slice_repository import TimeSliceRepository
from settings import get_settings_or_defaults

# Main window
from main_window import MainWindow


# TODO: rework this so that it uses MVC. Or just MV.


class App(Gtk.Application):
    def __init__(self):
        super().__init__(application_id=app_info.APP_ID)
        Notify.init(app_info.APP_NAME)

    def setup_action(self, callback: Callable[[], Any], shortcut: str):
        action = Gio.SimpleAction.new(callback.__name__, None)
        action.connect("activate", callback)
        self.window.add_action(action)
        self.set_accels_for_action(f"win.{callback.__name__}", [shortcut])

    def do_activate(self) -> None:
        make_connection = sqlite_setup.create_connection_factory(
            app_info.APP_ROOT / "data" / "time_slice.db"
        )
        time_slice_repo = TimeSliceRepository(make_connection)

        settings = get_settings_or_defaults(
            app_info.APP_ROOT / "data" / "settings.toml"
        )
        self.window = MainWindow(self, time_slice_repo, settings)

        self.setup_action(self.window.focus_description_input, "<Alt>1")
        self.setup_action(self.window.focus_tag_input, "<Alt>2")
        self.setup_action(self.window.focus_duration_input, "<Alt>3")
        self.setup_action(self.window.submit_form, "<Alt>Return")
        self.setup_action(self.window.toggle_stats, "<Alt>s")

        self.window.present()


def main():
    app = App()
    app.run([])


if __name__ == "__main__":
    main()
