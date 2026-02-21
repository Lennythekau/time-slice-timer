import pathlib
from typing import Any, Callable, cast
import gi

from next_action_dialog import NextActionDialog

gi.require_version("Gtk", "4.0")
gi.require_version("Gio", "2.0")
gi.require_version("Gdk", "4.0")
gi.require_version("Notify", "0.7")
from gi.repository import GLib, Gdk, Gio, Gtk, Notify

from time_slice_form_data import TimeSliceFormData
from timer import Timer
from total_times_table import TotalTimesTable

import db
from settings import get_settings_or_get_defaults, get_tag_names, get_tag_name_list

Notify.init("Slice")

CURRENT_DIRECTORY = pathlib.Path(__file__).resolve().parent
provider = Gtk.CssProvider()
provider.load_from_path(str(CURRENT_DIRECTORY / "style.css"))

Gtk.StyleContext.add_provider_for_display(
    cast(Gdk.Display, Gdk.Display.get_default()),
    provider,
    Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
)

settings = get_settings_or_get_defaults()
APP_NAME = "Slice ⏰🍕"


class App(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="com.ken.slice")
        db.ensure_table_created()
        self.update_times_by_tag()

    def update_times_by_tag(self):
        self.times_by_tag = {tag: 0 for tag in get_tag_names(settings)}
        for tag, minutes in db.get_times_by_tag():
            self.times_by_tag[tag] += minutes

    def setup_action(self, callback: Callable[[], Any], shortcut: str):
        action = Gio.SimpleAction.new(callback.__name__, None)
        action.connect("activate", callback)
        self.window.add_action(action)
        self.set_accels_for_action(f"win.{callback.__name__}", [shortcut])

    def do_activate(self) -> None:
        self.window = Gtk.ApplicationWindow(application=self)
        self.window.set_title(APP_NAME)

        self.root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.create_time_slice_form()

        self.timer = Timer()
        self.timer.set_sensitive(False)
        self.root.append(self.timer)

        self.total_times_table = TotalTimesTable()
        self.total_times_table.update(self.times_by_tag)
        self.root.append(self.total_times_table)
        self.total_times_table.set_visible(False)

        self.on_tag_input_changed()  # call this so that the default duration is set for the first item selected.

        self.next_action_dialog = NextActionDialog(self.window)
        self.next_action_dialog.connect("work", self.on_chose_work)

        self.setup_action(self.toggle_stats, "<Alt>S")
        self.setup_action(self.focus_description_input, "<Alt>1")
        self.setup_action(self.focus_tag_input, "<Alt>2")
        self.setup_action(self.focus_duration_input, "<Alt>3")
        self.setup_action(self.create_time_slice, "<Alt>Return")

        self.window.set_child(self.root)
        self.window.present()

    def toggle_stats(self, *_):
        # forces the window to use as little space as possible, so the freed space from the total times widget
        # is no longer taken up on the screen by the app (that is, that part of the screen does not have pixels allocated to this app)
        self.window.set_resizable(False)
        self.total_times_table.set_visible(not self.total_times_table.get_visible())
        # Make it resizable by a second later
        GLib.timeout_add_seconds(1, lambda: self.window.set_resizable(True) and False)

    def focus_description_input(self, *_):
        if self.time_slice_form.get_sensitive():
            self.description_input.grab_focus()

    def focus_tag_input(self, *_):
        if self.time_slice_form.get_sensitive():
            self.tag_input.grab_focus()

    def focus_duration_input(self, *_):
        if self.time_slice_form.get_sensitive():
            self.duration_input.grab_focus()

    def create_time_slice_form(self) -> None:
        """Adds the widgets to create the time slice form."""
        self.time_slice_form = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)

        self.description_input = Gtk.Entry(placeholder_text="Enter description...")
        self.time_slice_form.append(self.description_input)

        self.tag_input = Gtk.DropDown(
            model=Gtk.StringList(strings=get_tag_name_list(settings)),
            enable_search=True,
            expression=Gtk.PropertyExpression.new(Gtk.StringObject, None, "string"),
        )

        self.tag_input.connect("notify::selected", self.on_tag_input_changed)
        self.time_slice_form.append(self.tag_input)

        self.duration_input = Gtk.SpinButton.new_with_range(1, 60, 5)

        self.time_slice_form.append(self.duration_input)

        self.time_slice_submit_button = Gtk.Button(label="Start")
        self.time_slice_submit_button.connect("clicked", self.create_time_slice)
        self.time_slice_form.append(self.time_slice_submit_button)

        self.root.append(self.time_slice_form)

    def on_tag_input_changed(self, *_):
        index = self.tag_input.get_selected()
        duration = settings["tags"][index].get("duration", settings["default_duration"])
        self.duration_input.set_value(duration)

    def create_time_slice(self, *_):
        # TODO: replace UI state checking with some kind of model.
        # If this is run while the timer is running, then ignore this request.
        if not self.time_slice_form.get_sensitive():
            return

        """Creates the time slice, and sets up the timer."""
        # this might be fired by the global accelerator <Alt>Return
        # in which case, a focus out event may not happen for the duration input
        # and so the value just typed in may not be commited.
        # Call update to ensure they are commited.
        self.duration_input.update()

        # Grab all the info
        self.form_data = TimeSliceFormData(
            description=self.description_input.get_text(),
            tag=get_tag_name_list(settings)[self.tag_input.get_selected()],
            duration_minutes=self.duration_input.get_value_as_int(),
        )

        self.time_slice_form.set_sensitive(False)
        self.timer.begin(self.form_data.duration_minutes)

        self.on_timer_cancelled_id = self.timer.connect(
            "cancelled", self.on_timer_cancelled
        )
        self.on_timer_finished_id = self.timer.connect(
            "finished", self.on_timer_finished
        )

    def on_timer_cancelled(self, _):
        self.time_slice_form.set_sensitive(True)
        self.remove_timer_signal_listeners()

    def on_timer_finished(self, _):
        """Notifies the user when the timer ends, and also cleans up the UI."""
        description, tag, duration_minutes = self.form_data
        db.add_time_slice(description, tag, duration_minutes)

        self.update_times_by_tag()
        self.total_times_table.update(self.times_by_tag)

        # Notify the user
        notification = Notify.Notification(
            app_name=APP_NAME,
            summary="Time's up !",
            body=f"Spent {duration_minutes} minute(s).\nTag:{tag}\nDescription: {description}\n",
        )
        notification.show()

        self.remove_timer_signal_listeners()
        self.timer.set_sensitive(False)
        self.next_action_dialog.present()

    def on_chose_work(self, *_):
        self.time_slice_form.set_sensitive(True)
        self.description_input.grab_focus()

    def remove_timer_signal_listeners(self):
        self.timer.disconnect(self.on_timer_cancelled_id)
        self.timer.disconnect(self.on_timer_finished_id)


def main():
    app = App()
    app.run([])


if __name__ == "__main__":
    main()
