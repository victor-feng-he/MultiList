import re
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, colorchooser
from datetime import datetime, timedelta
from plyer import notification
import sqlite3 as sql
import json

# Define a global list to keep track of open description windows
open_description_windows = []

# Define default color values
default_colors = {
    "header_frame": "#FAEBD7",
    "functions_frame": "#FAEBD7",
    "listbox_frame": "#FAEBD7",
    "listbox": "#FFFFFF",
}

# Load saved color scheme from a configuration file
def load_color_scheme():
    try:
        with open("color_scheme.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return default_colors

# Save color scheme to a configuration file
def save_color_scheme(color_scheme):
    with open("color_scheme.json", "w") as file:
        json.dump(color_scheme, file)

# Set initial color scheme
color_scheme = load_color_scheme()

# Function to choose color and update widget background
def choose_color(widget_name):
    global color_scheme
    _, color = colorchooser.askcolor(color_scheme[widget_name])
    if color:
        color_scheme[widget_name] = color
        widget = widget_mapping[widget_name]
        widget.configure(bg=color)
        save_color_scheme(color_scheme)

def reset_all_colors_to_default():
    global color_scheme
    for widget_name, default_color in default_colors.items():
        try:
            color_scheme[widget_name] = default_color
            widget = widget_mapping[widget_name]
            widget.configure(bg=default_color)
        except KeyError:
            print(f"KeyError: Widget '{widget_name}' not found in widget_mapping dictionary.")
    save_color_scheme(color_scheme)

# Function to apply the current color scheme
def apply_color_scheme():
    guiWindow.conf(background=color_scheme["header_frame"])

# Function to calculate minutes before due time for the reminder
def calculate_minutes_before(due_time):
    due_time_obj = datetime.strptime(due_time, "%I:%M %p")
    current_time = datetime.now().time()
    current_datetime = datetime.combine(datetime.today(), current_time)
    time_difference = due_time_obj - current_datetime
    minutes_before = time_difference.total_seconds() / 60
    return minutes_before

# defining the function to add tasks to the list  
def add_task():
    global description_entry, task_string, due_date, due_time, add_button

    # getting the string from the entry fields
    task_string = task_field.get()
    due_date = due_date_entry.get()
    due_time = due_time_entry.get()

    # checking whether the task string is empty or not
    if len(task_string) == 0:
        # displaying a message box with 'Empty Field' message
        messagebox.showinfo('Error', 'Task Field is Empty.')
    else:
        # Check if a due date is provided and validate the format
        if due_date != "" and not is_valid_date_format(due_date):
            messagebox.showinfo('Error', 'Invalid Date Format. Use YYYY-MM-DD.')
            return
        elif due_date != "" and not is_valid_date(due_date):
            messagebox.showinfo('Error', 'Invalid Date. Please enter a valid date.')
            return
        # Check if a due time is provided and validate the format and time
        elif due_time != "" and not is_valid_time_format(due_time):
            messagebox.showinfo('Error', 'Invalid Time Format. Use HH:MM AM/PM.')
            return
        elif due_time != "" and not is_valid_time(due_time):
            messagebox.showinfo('Error', 'Invalid Time. Please enter a valid time')

        # If no due date is provided or placeholder text is not changed, set days_before to 0
        if due_date == "" or due_date == "YYYY-MM-DD":
            days_before = 0
        else:
            # If a due date is provided, ask the user for the number of days before the due date to set the reminder
            days_before = simpledialog.askinteger("Set Reminder", "Enter the number of days before the due date for the reminder:", minvalue=0)

        # If no due time is provided or placeholder text is not changed, set hours_before and minutes_before to 0
        if due_time == "" or due_time == "HH:MM AM/PM":
            hours_before = 0
            minutes_before = 0
        else:
            # If a due time is provided, calculate the minutes before the due time for the reminder
            minutes_before = calculate_minutes_before(due_time)

        # Calculate the position for the main window
        main_window_position = guiWindow.winfo_geometry().split('+')[1:3]
        main_window_width = guiWindow.winfo_width()
        main_window_height = guiWindow.winfo_height()

        # Calculate the position for the description window
        description_window_width = 300
        description_window_height = 150
        description_window_x = int(main_window_position[0]) + (main_window_width - description_window_width) // 2
        description_window_y = int(main_window_position[1]) + (main_window_height - description_window_height) // 2

        # Open a new window for task description
        description_window = tk.Toplevel(guiWindow)
        description_window.title("Task Description")
        description_window.geometry(f"{description_window_width}x{description_window_height}+{description_window_x}+{description_window_y}")

        # Disable the "Add Task" button after clicking
        add_button['state'] = 'disabled'

        # Entry field for task description
        description_label = ttk.Label(description_window, text="Task Description:")
        description_label.pack(pady=5)
        description_entry = ttk.Entry(description_window, font=("Consolas", "12"), width=25)
        description_entry.pack(pady=5)

        # Prevent the user from prematurely closing the description entry window
        description_window.protocol("WM_DELETE_WINDOW", lambda: None)

        # Button to finish adding the task
        finish_button = ttk.Button(description_window, text="Finish", command=lambda: finish_adding_task(description_window, description_entry, task_string, due_date, due_time, days_before, hours_before, minutes_before))
        finish_button.pack(pady=10)
        
    # Add the new description window to the list of open windows
    open_description_windows.append(description_window)

# defining the function to check the validity of the format
def is_valid_date_format(date_string):
    # Check if the date string is empty or has the format 'YYYY-MM-DD' or is equal to the placeholder text
    return date_string == "" or date_string == "YYYY-MM-DD" or bool(re.match(r'\d{4}-\d{2}-\d{2}$', date_string))

# defining the function to check the validity of the time format
def is_valid_time_format(time_string):
    # Check if the time string is empty or has the format 'HH:MM AM/PM' or is equal to the placeholder text
    return time_string == "" or time_string == "HH:MM AM/PM" or bool(re.match(r'^\d{2}:\d{2} [APMapm]{2}$', time_string))

# defining the function to check the validity of the date
def is_valid_date(date_string):
    try:
        # Check if the date string can be converted to a valid date
        datetime.strptime(date_string, '%Y-%m-%d')
        return True
    except ValueError:
        return False

# defining the function to check the validity of the time
def is_valid_time(time_string):
    try:
        # Check if the time string can be converted to a valid time
        datetime.strptime(time_string, '%I:%M %p')
        return True
    except ValueError:
        return False

# defining the function to finish adding tasks
def finish_adding_task(description_window, description_entry, task_string, due_date, due_time, days_before, hours_before, minutes_before):
    global open_description_windows

    # Get the task description from the entry field
    description = description_entry.get()

    # Check if the description is empty
    if len(description) == 0:
        messagebox.showinfo('Error', 'Task Description Field is Empty.')
    else:
        # Close the description entry window
        description_window.destroy()
        open_description_windows.remove(description_window)

        # Add the task to the listbox with the description and due date
        if due_date != "":
            due_date_obj = datetime.strptime(due_date, "%Y-%m-%d")
            due_date_formatted = due_date_obj.strftime("%B %d, %Y")
        else:
            due_date_formatted = "No Due Date"

        task_with_description = f"{task_string} - {description} ({due_date_formatted})"
        listbox.insert(tk.END, task_with_description)

        # Set a reminder for the task
        set_task_reminder(task_string, description, due_date, due_time, days_before, hours_before, minutes_before)

    # Re-enable the "Add Task" button
    add_button['state'] = 'normal'

# Function to set a reminder for a task
def set_task_reminder(task_string, description, due_date, due_time, days_before, hours_before, minutes_before):
    # Combine due date and time to create a datetime object
    if due_date != "" and due_time != "":
        due_datetime_str = f"{due_date} {due_time}"
        due_datetime_obj = datetime.strptime(due_datetime_str, "%Y-%m-%d %I:%M %p")

        # Subtract the specified days, hours, and minutes for the reminder
        reminder_datetime_obj = due_datetime_obj - timedelta(days=days_before, hours=hours_before, minutes=minutes_before)

        # Convert the reminder datetime object to a string
        reminder_datetime_str = reminder_datetime_obj.strftime("%Y-%m-%d %I:%M %p")

        # Schedule the reminder notification
        notification_title = f"Reminder: {task_string}"
        notification_message = f"{description}\nDue: {due_datetime_str}"
        notification.schedule(title=notification_title, message=notification_message, timeout=10)

# function to delete the tasks
def delete_task():
    current_selection = listbox.curselection()
    listbox.delete(current_selection)

# function to exit
def exit():
    guiWindow.destroy()

# creating the gui window
guiWindow = tk.Tk()
guiWindow.geometry('600x400')
guiWindow.title('Task Manager')
guiWindow.tk_setPalette(background=color_scheme["header_frame"])

# creating a frame for the header
header_frame = ttk.Frame(guiWindow)
header_frame.pack(side=tk.TOP, fill=tk.X)
header_frame.configure(background=color_scheme["header_frame"])

# creating a label for the header
header_label = ttk.Label(header_frame, text='Task Manager', font=("Helvetica", "16"))
header_label.pack(pady=10)
header_label.configure(background=color_scheme["header_frame"])

# creating a frame for the functions
functions_frame = ttk.Frame(guiWindow)
functions_frame.pack(side=tk.TOP, fill=tk.X)
functions_frame.configure(background=color_scheme["functions_frame"])

# Define entry widgets for task, due date, and due time
task_field = ttk.Entry(functions_frame, font=("Consolas", "12"), width=25)
due_date_entry = ttk.Entry(functions_frame, font=("Consolas", "12"), width=25)
due_time_entry = ttk.Entry(functions_frame, font=("Consolas", "12"), width=25)

# creating a button to add tasks
add_button = ttk.Button(functions_frame, text='Add Task', command=add_task)
add_button.grid(row=0, column=0, padx=5, pady=5)
add_button.configure(background=color_scheme["functions_frame"])

# creating a button to delete tasks
delete_button = ttk.Button(functions_frame, text='Delete Task', command=delete_task)
delete_button.grid(row=0, column=1, padx=5, pady=5)
delete_button.configure(background=color_scheme["functions_frame"])

# creating a button to exit
exit_button = ttk.Button(functions_frame, text='Exit', command=exit)
exit_button.grid(row=0, column=2, padx=5, pady=5)
exit_button.configure(background=color_scheme["functions_frame"])

# creating a frame for the listbox
listbox_frame = ttk.Frame(guiWindow)
listbox_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
listbox_frame.configure(background=color_scheme["listbox_frame"])

# creating a listbox
listbox = tk.Listbox(listbox_frame, font=("Consolas", "12"), selectbackground=color_scheme["listbox"])
listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
listbox.configure(background=color_scheme["listbox"])

# creating a scrollbar
scrollbar = ttk.Scrollbar(listbox_frame, orient=tk.VERTICAL, command=listbox.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
listbox.config(yscrollcommand=scrollbar.set)

# Create a mapping between widget names and their corresponding widgets
widget_mapping = {
    "header_frame": header_frame,
    "functions_frame": functions_frame,
    "listbox_frame": listbox_frame,
    "listbox": listbox,
}

# Set up the context menu for choosing colors
context_menu = tk.Menu(guiWindow, tearoff=0)
context_menu.add_command(label="Choose Header Frame Color", command=lambda: choose_color("header_frame"))
context_menu.add_command(label="Choose Functions Frame Color", command=lambda: choose_color("functions_frame"))
context_menu.add_command(label="Choose Listbox Frame Color", command=lambda: choose_color("listbox_frame"))
context_menu.add_command(label="Choose Listbox Color", command=lambda: choose_color("listbox"))
context_menu.add_command(label="Reset All Colors to Default", command=reset_all_colors_to_default)

# Apply the color scheme on right-click (context menu)
guiWindow.bind("<Button-3>", lambda event: context_menu.post(event.x_root, event.y_root))

# Apply the color scheme on startup
apply_color_scheme()

# Run the GUI
guiWindow.mainloop()