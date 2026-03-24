from enum import StrEnum
from typing import TYPE_CHECKING, cast, NamedTuple

from gi.repository import Gtk, GObject

if TYPE_CHECKING:
    from settings import Settings


class NewSliceForm(Gtk.Box):

    class FormData(NamedTuple):
        description: str
        tag: str
        duration_minutes: int

    class Signals(StrEnum):
        SUBMITTED = "submitted"

    __gsignals__ = {
        Signals.SUBMITTED: (GObject.SignalFlags.RUN_FIRST, None, ()),
    }

    def __init__(self, settings: Settings) -> None:
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=2)

        self.__settings = settings

        self.__description_input = Gtk.Entry(placeholder_text="Enter description...")

        self.__tag_input = Gtk.DropDown(
            model=Gtk.StringList(strings=settings["tag_names"]),
            enable_search=True,
            expression=Gtk.PropertyExpression.new(Gtk.StringObject, None, "string"),
        )

        self.__tag_input.connect("notify::selected", self.__on_tag_selected)
        self.__duration_input = Gtk.SpinButton.new_with_range(1, 60, 5)
        self.__submit_button = Gtk.Button(label="Start")
        self.__submit_button.connect("clicked", self.__on_submitted)

        self.append(self.__description_input)
        self.append(self.__tag_input)
        self.append(self.__duration_input)
        self.append(self.__submit_button)

        self.__set_duration_to_default()

    def get_form_data(self) -> NewSliceForm.FormData:
        return NewSliceForm.FormData(
            description=self.__description_input.props.text,
            tag=self.__get_selected_tag(),
            duration_minutes=int(self.__duration_input.props.value),
        )

    def submit(self):
        self.__submit_button.emit("clicked")

    def __get_selected_tag(self):
        selected_tag = cast(Gtk.StringObject, self.__tag_input.props.selected_item)
        tag = selected_tag.props.string
        return tag

    def __on_tag_selected(self, _widget, _param_spec):
        self.__set_duration_to_default()

    def __set_duration_to_default(self):
        tag_index = self.__tag_input.get_selected()
        tag_config = self.__settings["tags"][tag_index]
        duration = tag_config.get("duration", self.__settings["default_duration"])
        self.__duration_input.set_value(duration)

    def __on_submitted(self, _widget):
        # this might be fired by the global accelerator <Alt>Return
        # in which case, a focus out event may not happen for the duration input
        # and so the value just typed in may not be commited.
        # Call update to ensure they are commited.
        self.__duration_input.update()

        self.emit(NewSliceForm.Signals.SUBMITTED)

    def focus_description_input(self, *_):
        self.__description_input.grab_focus()

    def focus_tag_input(self, *_):
        self.__tag_input.grab_focus()

    def focus_duration_input(self, *_):
        self.__duration_input.grab_focus()
