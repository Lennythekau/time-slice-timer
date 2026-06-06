# ⏰🍕 Time Slice Timer

A timer meant for workflows that frequently switch between tasks.
This is a student personal project, but one that I'm learning from. My reflections are at the end.

# Usage

Install the pip packages:

```sh
pip install -r requirements.txt
```

This creates the resource file to make icons accessible from code:
```sh
pyside6-rcc icons.qrc -o rc_icons.py
```

Run the app:
```sh
python main.py
```

This app was made entirely for my own purposes, and doesn't care about user friendliness:
- Set up your tags using the tags menu.
- Optionally setup your tasks using the tasks menu.
- Create a *time slice* for a task you want to do:
- This works best if you divide your tasks up a lot, and choose a short duration (eg 5 minutes)
- Submit the form, this will start the timer
- A dialog will appear once the timer has finished. It's meant to be quite annoying to prevent you from doing any more work, forcing you to pick another time slice. 

## Shortcuts:

### Main Menu
- `Alt+1`: Focus the description input
- `Alt+2`: Focus the tag input
- `Alt+3`: Focus the duration input
- `Alt+Enter`: Submit the form to create a new time slice.
- `Alt+s`: Toggle visibility of the total times for today. I'm planning on moving it to a separate tab.
- `Alt+k`: Show task menu
- `Alt+t`: Show tag menu

### Task view (Inspired by Vim/Blender)
- `j`: Move down a task.
- `k`: Move up a task.
- `h`: Move to previous process (if currently on a process), or move to the process of the currently selected subtask.
- `l`: Move to next process. 
- `w`: Toggle between selecting the description, and the tag (if available).

- `Space`: toggle the expandedness of current task.

- `i`: Insert subtask, keeping focus on parent task.
- `Shift+a`: Add a task at the same level as the currently selected task (sibling task).
- `x`: Delete selected task
- `r`: Rename task

# Planned features:
- Change search bar to fuzzy search.
- Actually writing tests.
- Workflows

# Reflections

## Approaching SOLID principles: keep the GUI code focused only on the visual logic

This app started very simple. It was just the form; the timer itself; and a table showing how much time was spent for each tag today.
- The core logic of the app was coupled together with the GUI logic itself.
- This worked fine with such a small app, but as I added more features (ability to edit tags in the app, the task view), I struggled to move data between the parts of the app that needed it.

I relied heavily on *signals* (Qt's implementation of event-based programming) to pass the data between the widgets. On reflection, this was a very ugly way of doing things:
- The same data might need to be accessed from multiple parts of the GUI. Passing the data through the widget tree is okay when that data flow is *downwards*. The issue is when it needs to go upwards/sideways. It doesn't really make semantic sense for a parent widget to receive state from one of its child widgets, just to pass it back down to a different child.
- This also means that the flow of data is highly coupled to the actual layout of the GUI, so rearranging the GUI becomes painful.
- Not to mention, that this makes testing impossible (see below).

**The solution**: have a data layer (repositories), and make the GUI layer sit on top of that. The GUI layer reads downwards. Whether there's an intermediate layer (some kind of service/controller) depends on the use case. Since this is a small app, I didn't mind the view directly reading the repos; and for the repos to have events on them which the view directly listens to. For a larger-scale app, I might consider using an event bus, and potentially moving the events to a controller.

Regardless of how exactly it's implemented, you want *something* which handles the core logic, which is **not** the repo/view. This reduces coupling to the GUI (I really did not want to rely on Qt libraries outside of the GUI), and the data serialisation layer (SQLite, again, would rather not have to deal with SQL outside of the repos). In turn, this improves testing (see below).

## Avoiding strict MVC

Having done some webdev with eg Vue JS, I was used to the 'component' way of thinking: the unit is a UI widget which also has enough logic to be self sufficient, given the correct inputs. Clearly, that didn't really work here. I wasn't familiar with QML, so I had just used the more familiar widget way of working. That unfortunately meant no MVVM, leaving MVC as an obvious alternative.

I tried to obey the classical Smalltalk MVC, but realised that the controller directly mutated the view. That didn't seem particularly elegant. What about web MVC? That seemed quite verbose, hardly more than a wrapper around the repo classes for an app of this scale.

I ended up keeping the terminology, but my app isn't 'true' MVC. I realised that following very specific design patterns isn't always sensible. We definitely still have separation between the view and the model; and maybe some classes in the middle. We get good separation of concerns, without enforcing ceremony.

### Testing

This was the first time I properly did testing. My app was reaching the point where it was getting tricky to conceptualise the whole thing in my head. I also spotted a few subtle bugs. 

Testing gave me confidence that my app actually worked, and would continue to work after updating it. Handling test setup with fixtures was much easier than expected.

I also saw the pay off of separating things properly: by separating the GUI logic from the core logic, I could test the core logic without involving myself in tricky GUI testing.

I also saw how misleading a metric code coverage can be. I found that I could get very high code coverage with only a couple of tests, which weren't even that thorough.