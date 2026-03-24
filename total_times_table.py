from typing import cast
from gi.repository import Gtk, Gio, GObject


class TotalTimesTable(Gtk.Box):
    class TagTime(GObject.GObject):
        tag_name = GObject.Property(type=str)
        minutes = GObject.Property(type=int)

        def __init__(self, tag_name: str, minutes: int):
            super().__init__()
            self.tag_name = tag_name
            self.minutes = minutes

    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)

        self.__store = Gio.ListStore(item_type=TotalTimesTable.TagTime)
        self.__selection = Gtk.NoSelection(model=self.__store)
        self.__view = Gtk.ColumnView(model=self.__selection)

        # Tag column
        tag_factory = Gtk.SignalListItemFactory()
        tag_factory.connect("setup", self.__setup_tag)
        tag_factory.connect("bind", self.__bind_tag)
        tag_column = Gtk.ColumnViewColumn(title="Tag", factory=tag_factory)

        # Minutes column
        minutes_factory = Gtk.SignalListItemFactory()
        minutes_factory.connect("setup", self.__setup_minutes)
        minutes_factory.connect("bind", self.__bind_minutes)
        minutes_column = Gtk.ColumnViewColumn(title="Minutes", factory=minutes_factory)

        tag_column.set_expand(True)
        minutes_column.set_expand(True)

        self.__view.append_column(tag_column)
        self.__view.append_column(minutes_column)

        self.append(self.__view)

    def __setup_tag(self, _, list_item: Gtk.ColumnViewCell):
        label = Gtk.Label()
        list_item.set_child(label)

    def __bind_tag(self, _, list_item: Gtk.ColumnViewCell):
        item = cast(TotalTimesTable.TagTime, list_item.get_item())
        cast(Gtk.Label, list_item.get_child()).set_text(item.tag_name)

    def __setup_minutes(self, _, list_item: Gtk.ColumnViewCell):
        label = Gtk.Label()
        list_item.set_child(label)

    def __bind_minutes(self, _, list_item: Gtk.ColumnViewCell):
        item = cast(TotalTimesTable.TagTime, list_item.get_item())
        cast(Gtk.Label, list_item.get_child()).set_text(str(item.minutes))

    def update(self, tag_totals: dict[str, int]):
        self.__store.remove_all()
        for tag_name, minutes in tag_totals.items():
            self.__store.append(TotalTimesTable.TagTime(tag_name, minutes))
