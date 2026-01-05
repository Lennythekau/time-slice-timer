from gi.repository import GLib, Gtk, GObject
from time_slice_form_data import TimeSliceFormData


def format_time(seconds: int):
    return f"{(seconds // 60):02}:{(seconds % 60):02}"


class Timer(Gtk.Box):
    __gsignals__ = {
        "finished": (GObject.SignalFlags.RUN_FIRST, None, ()),
        "cancelled": (GObject.SignalFlags.RUN_FIRST, None, ()),
    }

    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        self.__time_display = Gtk.Label(label="unset")
        self.append(self.__time_display)
        self.__create_controls()

    def __create_controls(self):
        self.__controls_box = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL, halign=Gtk.Align.CENTER
        )

        self.__play_button = Gtk.Button(label="")
        self.__controls_box.append(self.__play_button)

        self.__pause_button = Gtk.Button(label="")
        self.__controls_box.append(self.__pause_button)

        self.__cancel_button = Gtk.Button(label="󰜺")
        self.__controls_box.append(self.__cancel_button)

        self.append(self.__controls_box)

    def begin(self, form_data: TimeSliceFormData):
        self.set_sensitive(True)
        self.__play_button.set_sensitive(False)

        self.__seconds_left = form_data.duration_minutes * 60
        self.__time_display.set_text(format_time(self.__seconds_left))

        self.__play_button_clicked_id = self.__play_button.connect(
            "clicked", self.__resume
        )
        self.__pause_button_clicked_id = self.__pause_button.connect(
            "clicked", self.__pause
        )
        self.__cancel_button_clicked_id = self.__cancel_button.connect(
            "clicked", self.__cancel
        )
        self.__timeout_id = GLib.timeout_add_seconds(1, self.__update_timer)

    def __update_timer(self):
        self.__seconds_left -= 1

        if self.__seconds_left < 0:
            # Disconnect timer controls.
            self.__play_button.disconnect(self.__play_button_clicked_id)
            self.__pause_button.disconnect(self.__pause_button_clicked_id)
            self.emit("finished")
            return GLib.SOURCE_REMOVE

        self.__time_display.set_text(format_time(self.__seconds_left))
        return GLib.SOURCE_CONTINUE

    def __pause(self, _):
        assert self.__timeout_id is not None
        GLib.source_remove(self.__timeout_id)
        self.__timeout_id = None

        self.__pause_button.set_sensitive(False)
        self.__play_button.set_sensitive(True)

    def __resume(self, _):
        self.__timeout_id = GLib.timeout_add_seconds(1, self.__update_timer)
        self.__play_button.set_sensitive(False)
        self.__pause_button.set_sensitive(True)

    def __cancel(self, _):
        if self.__timeout_id is not None:
            GLib.source_remove(self.__timeout_id)

        self.set_sensitive(False)

        self.__play_button.disconnect(self.__play_button_clicked_id)
        self.__pause_button.disconnect(self.__pause_button_clicked_id)
        self.__cancel_button.disconnect(self.__cancel_button_clicked_id)
        self.emit("cancelled")
