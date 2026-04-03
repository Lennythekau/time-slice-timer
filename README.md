# ⏰🍕 Time Slice Timer

A timer meant for workflows that frequently switch between tasks.

# Usage

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
- Move the total times to a separate tab
- Separate window/tab for statistics
- Change search bar to fuzzy search.

# Setup

Install the Python libraries, setting up a venv beforehand if you wish:

```bash
pip install -r requirements.txt
```

Run:

```bash
python main.py
```
