from gi.repository import Gtk


class TotalTimesWidget(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)

        self.__liststore = Gtk.ListStore(str, int)
        self.__view = Gtk.TreeView(model=self.__liststore)

        renderer_text = Gtk.CellRendererText()

        tag_column = Gtk.TreeViewColumn("Tag", renderer_text, text=0)
        time_column = Gtk.TreeViewColumn("Minutes", renderer_text, text=1)

        self.__view.append_column(tag_column)
        self.__view.append_column(time_column)

        self.append(self.__view)

    def update(self, tag_totals: dict[str, int]):
        """Refresh table contents from model data."""
        self.__liststore.clear()

        for tag, minutes in tag_totals.items():
            self.__liststore.append([tag, minutes])
