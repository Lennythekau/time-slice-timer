import gi

from total_times_widget import TotalTimesWidget

gi.require_version("Gtk", "4.0")
gi.require_version("Notify", "0.7")

from gi.repository import GLib, Gtk, Notify
from time_slice_form_data import TimeSliceFormData
from timer import Timer

Notify.init("Slice")

TAGS = "Blender", "Musescore", "Quant"
APP_NAME = "Slice ⏰🍕"
total_times = {tag: 0 for tag in TAGS}


class App(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="com.ken.slice")

    def do_activate(self) -> None:
        self.window = Gtk.ApplicationWindow(application=self)
        self.window.set_title(APP_NAME)
        self.window.set_default_size(500, 400)

        self.root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.create_time_slice_form()

        self.timer = Timer()
        self.timer.set_sensitive(False)
        self.root.append(self.timer)

        self.total_times_widget = TotalTimesWidget()
        self.total_times_widget.update(total_times)
        self.root.append(self.total_times_widget)

        self.window.set_child(self.root)
        self.window.present()

    def create_time_slice_form(self) -> None:
        """Adds the widgets to create the time slice form."""
        self.time_slice_form = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)

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

    def create_time_slice(self, _):
        """Creates the time slice, and sets up the timer."""
        # Grab all the info
        self.form_data = TimeSliceFormData(
            description=self.description_input.get_text(),
            tag=TAGS[self.tag_input.get_selected()],
            duration_minutes=self.duration_input.get_value_as_int(),
        )

        self.time_slice_form.set_sensitive(False)
        self.timer.begin(self.form_data)

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
        """Notifies the user when the timer ends, and also cleans up the ui."""
        description, tag, duration_minutes = self.form_data
        total_times[tag] += duration_minutes
        self.total_times_widget.update(total_times)

        # Notify the user
        notification = Notify.Notification(
            app_name=APP_NAME,
            summary="Time's up !",
            body=f"Spent {duration_minutes} minute(s).\nTag:{tag}\nDescription: {description}\n",
        )
        notification.show()

        self.time_slice_form.set_sensitive(True)
        self.remove_timer_signal_listeners()

    def remove_timer_signal_listeners(self):
        self.timer.disconnect(self.on_timer_cancelled_id)
        self.timer.disconnect(self.on_timer_finished_id)


app = App()
app.run([])
