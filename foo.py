import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk


class Demo(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="org.example.Demo")

    def do_activate(self):
        window = Gtk.ApplicationWindow(application=self)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        window.set_child(box)

        btn_toggle = Gtk.Button(label="Toggle other button")
        self.btn_target = Gtk.Button(label="I disappear")

        box.append(btn_toggle)
        box.append(self.btn_target)
        box.append(Gtk.Label(label="foo"))

        btn_toggle.connect("clicked", self.on_toggle)

        window.present()

    def on_toggle(self, button):
        self.btn_target.set_visible(not self.btn_target.get_visible())


app = Demo()
app.run([])
