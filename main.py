from typing import NamedTuple
import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Notify", "0.7")

from gi.repository import GLib, Gtk, Notify

Notify.init("Slice")

TAGS = "Blender", "Musescore", "Quant"
APP_NAME = "Slice ⏰🍕"


class TimeSliceFormData(NamedTuple):
    description: str
    tag: str
    duration_minutes: int


class App(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="com.ken.slice")

    def do_activate(self) -> None:
        self.window = Gtk.ApplicationWindow(application=self)
        self.window.set_title(APP_NAME)
        self.window.set_default_size(500, 400)

        self.root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.create_time_slice_form()
        self.create_timer_and_controls()
        self.timer_and_controls_box.set_sensitive(False)

        self.window.set_child(self.root)
        self.window.present()

    def create_time_slice_form(self) -> None:
        """Adds the widgets to create the time slice form."""
        self.time_slice_form = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        self.description_input = Gtk.Entry(placeholder_text="Enter description...")
        self.time_slice_form.append(self.description_input)

        self.tag_input = Gtk.DropDown.new_from_strings(TAGS)
        self.time_slice_form.append(self.tag_input)

        self.duration_input = Gtk.SpinButton.new_with_range(1, 60, 1)
        self.time_slice_form.append(self.duration_input)

        self.time_slice_submit_button = Gtk.Button(label="Start")
        self.time_slice_submit_button.connect("clicked", self.create_time_slice)
        self.time_slice_form.append(self.time_slice_submit_button)

        self.root.append(self.time_slice_form)

    def create_timer_and_controls(self):
        self.timer_and_controls_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        self.timer = Gtk.Label(label="unset")
        self.timer_and_controls_box.append(self.timer)

        self.controls_box = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL, halign=Gtk.Align.CENTER
        )

        self.play_button = Gtk.Button(label="")
        self.controls_box.append(self.play_button)

        self.pause_button = Gtk.Button(label="")
        self.controls_box.append(self.pause_button)

        self.cancel_button = Gtk.Button(label="󰜺")
        self.controls_box.append(self.cancel_button)

        self.timer_and_controls_box.append(self.controls_box)
        self.root.append(self.timer_and_controls_box)

    def create_time_slice(self, _):
        """Creates the time slice, and sets up the timer."""
        # Grab all the info
        form_data = TimeSliceFormData(
            description=self.description_input.get_text(),
            tag=TAGS[self.tag_input.get_selected()],
            duration_minutes=self.duration_input.get_value_as_int(),
        )

        self.setup_timer_and_controls(form_data)

        self.time_slice_form.set_sensitive(False)
        self.timer_and_controls_box.set_sensitive(True)
        self.play_button.set_sensitive(False)

    def setup_timer_and_controls(self, form_data: TimeSliceFormData):
        """Starts the timer, and sets up functionality for when the timer ends."""
        seconds_left = form_data.duration_minutes * 60
        format_time = lambda seconds: f"{(seconds // 60):02}:{(seconds % 60):02}"

        def update_timer():
            nonlocal seconds_left
            seconds_left -= 1

            # End the timer if there are no seconds left
            if seconds_left < 0:
                on_timer_finished(form_data)
                return False

            self.timer.set_text(format_time(seconds_left))
            return True

        def pause(_):
            nonlocal timeout_id
            GLib.source_remove(timeout_id)
            timeout_id = -1  # assign invalid id so that can tell that we have paused.
            self.pause_button.set_sensitive(False)
            self.play_button.set_sensitive(True)

        def resume(_):
            nonlocal timeout_id
            timeout_id = GLib.timeout_add_seconds(1, update_timer)
            self.play_button.set_sensitive(False)
            self.pause_button.set_sensitive(True)

        def cancel(_):
            if timeout_id != -1:
                GLib.source_remove(timeout_id)
            self.timer_and_controls_box.set_sensitive(False)
            self.time_slice_form.set_sensitive(True)

            self.play_button.disconnect(play_button_clicked_id)
            self.pause_button.disconnect(pause_button_clicked_id)
            self.cancel_button.disconnect(cancel_button_clicked_id)

        # Set the timer up
        self.timer.set_text(format_time(seconds_left))

        play_button_clicked_id = self.play_button.connect("clicked", resume)
        pause_button_clicked_id = self.pause_button.connect("clicked", pause)
        cancel_button_clicked_id = self.cancel_button.connect("clicked", cancel)
        timeout_id = GLib.timeout_add_seconds(1, update_timer)

        def on_timer_finished(form_data: TimeSliceFormData):
            """Notifies the user when the timer ends, and also cleans up the ui."""
            description, tag, duration_minutes = form_data

            # Notify the user
            notification = Notify.Notification(
                app_name=APP_NAME,
                summary="Time's up !",
                body=f"Spent {duration_minutes} minutes.\nTag:{tag}\nDescription: {description}\n",
            )
            notification.show()

            # Disconnect timer controls.
            self.play_button.disconnect(play_button_clicked_id)
            self.pause_button.disconnect(pause_button_clicked_id)

            self.time_slice_form.set_sensitive(True)


app = App()
app.run([])
