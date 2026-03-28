# ⏰🍕 Time Slice Timer

A timer meant for workflows that frequently switch between tasks.

# Usage

This app was made entirely for my own purposes, and doesn't care about user friendliness:
- Run the app, and close it. This will generate a `data` directory in the app root.
    - Manually edit the `settings.toml` file, to add the tags you want.
- Create a *time slice* for a task you want to do:
- This works best if you divide your tasks up a lot, and choose a short duration (eg 5 minutes)
- Submit the form, this will start the timer
- A dialog will appear once the timer has finished. It's meant to be quite annoying to prevent you from doing any more work, forcing you to pick another time slice. 

## Shortcuts:
- `Alt+1`: Focus the description input
- `Alt+2`: Focus the tag input
- `Alt+3`: Focus the duration input
- `Alt+Enter`: Submit the form to create a new time slice.
- `Alt+s`: Toggle visibility of the total times for today. I'm planning on moving it to a separate tab.

# Planned features:
- Move the total times to a separate tab
- Separate window/tab for statistics
- Built-in editor for tags
- Task view (MAIN PRIORITY): built in editor for:
    - Creating tasks
    - Splitting these into subtasks
    - Select a (sub)task to automatically load it into the form
    - Search/filter on this list
    - Unsure if you would manually remove the task from the list, or if the dialog that appears after a task is done would ask if you wanted it removed.

# Setup

Install the Python libraries, setting up a venv beforehand if you wish:

```bash
pip install -r requirements.txt
```

Run:

```bash
python main.py
```
