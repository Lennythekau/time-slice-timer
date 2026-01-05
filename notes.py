import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Notify", "0.7")

from gi.repository import GLib, Gtk, Notify

Notify.init("Slice")


class App(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="com.example.slice")

    def do_activate(self):
        window = Gtk.ApplicationWindow(application=self)
        window.set_title("Slice")
        window.set_default_size(400, 300)

        window.set_margin_start(0)
        window.set_margin_end(0)
        window.set_margin_top(0)
        window.set_margin_bottom(0)

        label = Gtk.Label(label="Hello world!")
        label2 = Gtk.Label(label="Hello world!")

        btn = Gtk.Button(label="Click me")
        btn.connect("clicked", self.on_click)

        text_entry = Gtk.Entry()
        text_entry.set_placeholder_text("Enter something here")
        print(text_entry.get_text())

        combo = Gtk.ComboBoxText()
        combo.append_text("Tag1")
        combo.append_text("Tag2")
        combo.set_active(0)
        print(combo.get_active_text())

        adjust = Gtk.Adjustment(
            value=15,
            lower=1,
            upper=240,
            step_increment=1,
            page_increment=5,
            page_size=0,
        )

        # alternatively use SpinButton.new_with_range
        spin = Gtk.SpinButton(adjustment=adjust)
        spin.get_value_as_int()

        # Callback returns False when it needs to stop
        # GLib.timeout_add_seconds(interval=1, called_every_second)

        store = Gtk.ListStore(str, int)
        store.append(["foo", 23])
        store.append(["bar", 13])
        view = Gtk.TreeView(model=store)

        renderer_text = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Tag", renderer_text, text=0)
        column2 = Gtk.TreeViewColumn("Num", renderer_text, text=1)
        view.append_column(column)
        view.append_column(column2)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        box.append(label)
        box.append(label2)
        box.append(btn)
        box.append(text_entry)
        box.append(combo)
        box.append(spin)
        box.append(view)

        window.set_child(box)
        window.present()

    def on_click(self, widget: Gtk.Button):
        notification = Notify.Notification(body=f"{widget.get_name()}!")
        notification.show()


app = App()
app.run([])
