# Standard library
from typing import Any, cast, TYPE_CHECKING

# Gtk
from gi.repository import Gio, Gtk, Gdk, Notify, GLib

import app_info
from new_slice_form import NewSliceForm

from timer import Timer
from total_times_table import TotalTimesTable
from next_action_dialog import NextActionDialog

# Types:
if TYPE_CHECKING:

    from db.time_slice_repository import TimeSliceRepository
    from settings import Settings


class MainWindow(Gtk.ApplicationWindow):

    def __init__(
        self,
        application: Gtk.Application,
        time_slice_repo: TimeSliceRepository,
        settings: Settings,
    ) -> None:

        super().__init__(application=application, title=app_info.APP_NAME)
        self.__time_slice_repo = time_slice_repo
        self.__settings = settings
        self.__form_data: NewSliceForm.FormData | None = None

        self.__load_css()
        self.__create_controls()

    def focus_description_input(self, *_):
        self.__new_slice_form.focus_description_input()

    def focus_tag_input(self, *_):
        self.__new_slice_form.focus_tag_input()

    def focus_duration_input(self, *_):
        self.__new_slice_form.focus_duration_input()

    def submit_form(self, *_):
        self.__new_slice_form.submit()

    def __load_css(self):
        provider = Gtk.CssProvider()
        provider.load_from_path(str(app_info.APP_ROOT / "style.css"))

        Gtk.StyleContext.add_provider_for_display(
            cast(Gdk.Display, Gdk.Display.get_default()),
            provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )

    def __get_todays_tag_times(self):
        # If there wasn't a slice today for a tag, then this won't include it here.
        tag_times_raw = self.__time_slice_repo.get_times_by_tag()
        tag_times = {tag: 0 for tag in self.__settings["tag_names"]}
        for tag, time in tag_times_raw:
            tag_times[tag] = time

        return tag_times

    def __create_controls(self) -> None:
        self.__root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)

        self.__new_slice_form = NewSliceForm(self.__settings)
        self.__new_slice_form.connect(
            self.__new_slice_form.Signals.SUBMITTED, self.__on_form_submit
        )

        self.__timer = Timer()
        self.__timer.props.sensitive = False

        self.__total_times_table = TotalTimesTable()
        self.__total_times_table.update(self.__get_todays_tag_times())
        self.__total_times_table.props.visible = False

        self.__root.append(self.__new_slice_form)
        self.__root.append(self.__timer)
        self.__root.append(self.__total_times_table)
        self.set_child(self.__root)

        self.__next_action_dialog = NextActionDialog(self)
        self.__next_action_dialog.connect("work", self.__on_chose_work)

    def toggle_stats(self, *_):
        # forces the window to use as little space as possible, so the freed space from the total times widget
        # is no longer taken up on the screen by the app (that is, that part of the screen does not have pixels allocated to this app)
        self.props.resizable = False
        self.__total_times_table.set_visible(not self.__total_times_table.get_visible())
        # Make it resizable by a second later
        GLib.timeout_add_seconds(
            1, lambda: self.set_resizable(True) and GLib.SOURCE_REMOVE
        )

    def __on_form_submit(self, _control):
        # TODO: replace UI state checking with some kind of model.
        # If this is run while the timer is running, then ignore this request.
        self.__new_slice_form.props.sensitive = False
        self.__form_data = self.__new_slice_form.get_form_data()
        self.__start_timer(self.__form_data.duration_minutes)

    def __start_timer(self, duration: int):
        self.__timer.begin(duration)
        self.__timer.props.sensitive = True

        self.on_timer_cancelled_id = self.__timer.connect(
            "cancelled", self.__on_timer_cancelled
        )
        self.on_timer_finished_id = self.__timer.connect(
            "finished", self.__on_timer_finished
        )

    def __on_timer_cancelled(self, _widget):
        self.__new_slice_form.props.sensitive = True
        self.__remove_timer_signal_listeners()

    def __on_timer_finished(self, _widget):
        """Notifies the user when the timer ends, and also cleans up the UI."""
        assert self.__form_data is not None
        description, tag, duration_minutes = self.__form_data

        self.__time_slice_repo.add(description, tag, duration_minutes)
        self.__total_times_table.update(self.__get_todays_tag_times())

        # Notify the user
        notification = Notify.Notification(
            summary="Time's up!",
            body=f"Spent {duration_minutes} minute(s).\nTag:{tag}\nDescription: {description}\n",
        )
        notification.show()

        self.__remove_timer_signal_listeners()
        self.__timer.props.sensitive = False
        self.__next_action_dialog.present()

    def __on_chose_work(self, _widget):
        self.__new_slice_form.set_sensitive(True)
        self.__new_slice_form.focus_description_input()

    def __remove_timer_signal_listeners(self):
        self.__timer.disconnect(self.on_timer_cancelled_id)
        self.__timer.disconnect(self.on_timer_finished_id)
