from typing import cast
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GObject

from timer import Timer


class NextActionDialog(Gtk.Dialog):

    __gsignals__ = {
        "work": (GObject.SignalFlags.RUN_FIRST, None, ()),
    }

    def __init__(self, parent: Gtk.Window):
        super().__init__(
            modal=True, transient_for=parent, application=parent.get_application()
        )
        self.set_title("What now 🤔?")
        self.set_default_size(1920 - 200, 1080 - 200)

        __root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        __title = Gtk.Label(label="What now 🤔?")
        __root.append(__title)

        self.__stack = Gtk.Stack()
        self.__stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
        self.__stack.set_transition_duration(150)

        self.__options_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

        self.__break_button = Gtk.Button(label="Take a break for 5 minutes 😴")
        self.__break_button.connect("clicked", self.__on_break_button_clicked)
        self.__options_box.append(self.__break_button)

        self.__work_button = Gtk.Button(label="Have another time slice 🔥")
        self.__work_button.connect("clicked", self.__on_work_button_clicked)
        self.__options_box.append(self.__work_button)

        self.__stack.add_child(self.__options_box)

        self.__timer = Timer()
        self.__stack.add_child(self.__timer)

        __root.append(self.__stack)
        self.__stack.set_visible_child(self.__options_box)

        self.set_child(__root)

    def __on_break_button_clicked(self, _):
        self.__stack.set_visible_child(self.__timer)
        self.__timer.begin(5)

        self.__timer.connect("finished", self.__reset)
        self.__timer.connect("cancelled", self.__reset)

    def __reset(self, *_):
        """Restores the state of the dialog."""
        self.__stack.set_visible_child(self.__options_box)

    def __on_work_button_clicked(self, _):
        self.__stack.set_visible_child(self.__options_box)
        self.emit("work")
        self.hide()
        cast(Gtk.Window, self.get_transient_for()).present()
