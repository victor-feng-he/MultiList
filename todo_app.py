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
    guiWindow.tk_setPalette(background=color_scheme["header_frame"])

# defining the function to add tasks to the list  
def add_task():
    global description_entry, task_string, due_date, add_button

    # getting the string from the entry fields
    task_string = task_field.get()
    due_date = due_date_entry.get()

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

        # If no due date is provided or placeholder text is not changed, set days_before to 0
        if due_date == "" or due_date == "YYYY-MM-DD":
            days_before = 0
        else:
            # If a due date is provided, ask the user for the number of days before the due date to set the reminder
            days_before = simpledialog.askinteger("Set Reminder", "Enter the number of days before the due date for the reminder:", minvalue=0)

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
        finish_button = ttk.Button(description_window, text="Finish", command=lambda: finish_adding_task(description_window, description_entry, task_string, due_date, days_before))
        finish_button.pack(pady=10)
        
    # Add the new description window to the list of open windows
    open_description_windows.append(description_window)

# defining the function to check the validity of the format
def is_valid_date_format(date_string):
    # Check if the date string is empty or has the format 'YYYY-MM-DD' or is equal to the placeholder text
    return date_string == "" or date_string == "YYYY-MM-DD" or bool(re.match(r'\d{4}-\d{2}-\d{2}$', date_string))

# defining the function to check the validity of the date
def is_valid_date(date_string):
    # Check if the date string is empty or is a valid date and not in the past
    if date_string == "" or date_string == "YYYY-MM-DD":
        return True
    try:
        date_object = datetime.strptime(date_string, '%Y-%m-%d')
        today_date = datetime.today().strftime('%Y-%m-%d')
        return date_object >= datetime.strptime(today_date, '%Y-%m-%d')
    except ValueError:
        return False

def finish_adding_task(description_window, description_entry, task_string, due_date, days_before):
    description = description_entry.get()
    completed = 0  # Set to 1 if the task is completed

    task = (task_string, due_date, description, completed)

    tasks.append(task)
    the_cursor.execute('insert into tasks (title, due_date, description, completed) values (?, ?, ?, ?)',
                       (task_string, due_date, description, completed))
    list_update()
    task_field.delete(0, 'end')
    due_date_entry.delete(0, 'end')
    description_entry.delete(0, 'end')
    description_window.destroy()

    # Remove the finished description window from the list of open windows
    open_description_windows.remove(description_window)

    # Enable the "Add Task" button after finishing adding the description
    add_button['state'] = 'normal'

    # Notify the user about the task on the due date
    notify_task_due(task_string, due_date, description, days_before)

# Function to toggle completion of the selected task
def toggle_selected_task_completion():
    selected_task_index = task_listbox.curselection()

    if selected_task_index:
        selected_task = task_listbox.get([selected_task_index[0]])
        toggle_task_completion(selected_task)  # Pass the task title to the function

# Function to mark/unmark a task as complete
def toggle_task_completion(task_title):
    selected_task_index = task_listbox.curselection()

    if selected_task_index:
        selected_task = next((task for task in tasks if task[0] == task_title), None)

        # Toggle the completion status in the tasks list
        selected_task_index = tasks.index(selected_task)
        tasks[selected_task_index] = (selected_task[0], selected_task[1], selected_task[2], not selected_task[3])

        # Update the completion status in the database
        the_cursor.execute('update tasks set completed = ? where title = ? and description = ?', (int(not selected_task[3]), selected_task[0], selected_task[2]))

        # Update the display in the listbox
        list_update()

def notify_task_due(task_name, due_date, description, days_before=0):
    today_date = datetime.today().strftime('%Y-%m-%d')
    try:
        due_datetime = datetime.strptime(due_date, '%Y-%m-%d')

        # Calculate the reminder date by subtracting the specified number of days
        reminder_date = due_datetime - timedelta(days=days_before)

        if today_date == reminder_date.strftime('%Y-%m-%d'):
            notification_title = f"Task Reminder: {task_name}"
            notification_message = f"Your task '{task_name}' is due in {days_before} days on {due_date}.\n {description}"

            # You can customize the notification duration, toast=False for other platforms
            notification.notify(
                title=notification_title,
                message=notification_message,
                app_icon=None  # You can provide the path to an icon if you have one
            )
    except ValueError:
        # Ignore error when user adds a task without a due date
        pass
        
def clear_placeholder(event, entry, placeholder):
    if entry.get() == placeholder:
        entry.delete(0, "end")
        entry.configure(foreground="#000000")  # Set text color to black
    entry.unbind("<FocusIn>")  # Unbind the event to avoid clearing again
    
def open_edit_due_date_window(selected_task):
    edit_due_date_window = tk.Toplevel(guiWindow)
    edit_due_date_window.title("Edit Due Date")

    # Create/Edit GUI for Due Date Editing
    ttk.Label(edit_due_date_window, text="New Due Date:").pack(pady=5)
    new_due_date_entry = ttk.Entry(edit_due_date_window, font=("Consolas", "12"), width=15)
    new_due_date_entry.pack(pady=5)

    # Set the due date as a placeholder in the entry field
    new_due_date_entry.insert(0, selected_task[1])

    # Validate and Confirm Changes Button
    confirm_button = ttk.Button(edit_due_date_window, text="Confirm Changes", command=lambda: confirm_due_date_edit(selected_task, new_due_date_entry, edit_due_date_window))
    confirm_button.pack(pady=10)

    # Prevent the user from prematurely closing the edit window
    edit_due_date_window.protocol("WM_DELETE_WINDOW", lambda: None)

def confirm_due_date_edit(selected_task, new_due_date_entry, edit_due_date_window):
    new_due_date = new_due_date_entry.get()

    # Validate New Due Date
    if is_valid_date_format(new_due_date) and is_valid_date(new_due_date):
        # Update the due date in the tasks list
        selected_task_index = tasks.index(selected_task)
        tasks[selected_task_index] = (selected_task[0], new_due_date, selected_task[2], selected_task[3])

        # Update the due date in the database
        the_cursor.execute('update tasks set due_date = ? where title = ? and description = ?', (new_due_date, selected_task[0], selected_task[2]))

        # Update the display in the listbox
        list_update()

        # Close the edit due date window
        edit_due_date_window.destroy()
    else:
        messagebox.showinfo('Error', 'Invalid Date Format. Please enter a valid date.')

# defining function to display task description when task item has been clicked on
def show_task_description(task_title):
    selected_task_index = task_listbox.curselection()

    if selected_task_index:
        selected_task = next((task for task in tasks if task[0] == task_title), None)

        # Retrieve task name, description, and due date of the selected item
        task_title = selected_task[0]
        description = selected_task[2]
        due_date = selected_task[1]

        # Check if a window for this task description already exists
        existing_window = next((window for window in open_description_windows if window.winfo_exists() and window.title() == task_title), None)

        if existing_window:
            # Bring the existing window to the front
            existing_window.lift()
        else:
            # Create a new window for task description
            description_window = tk.Toplevel(guiWindow)
            description_window.title(task_title)
            description_window.geometry("300x200")

            open_description_windows.append(description_window)

            # Retrieve the task details from the list based on the task title
            selected_task = next((task for task in tasks if task[0] == task_title), None)

            description_label = ttk.Label(description_window, text="Task Description:")
            description_label.pack(pady=5)

            description_text = ttk.Label(description_window, text=selected_task[2], font=("Consolas", "12"))
            description_text.pack(pady=10)

            date_label = ttk.Label(description_window, text="Due Date:")
            date_label.pack(pady=5)

            date_text = ttk.Label(description_window, text=selected_task[1], font=("Consolas", "12"))
            date_text.pack(pady=10)

            # Add "Edit Due Date" Button
            edit_due_date_button = ttk.Button(description_window, text="Edit Due Date", command=lambda: open_edit_due_date_window(selected_task))
            edit_due_date_button.pack(pady=10)

            # Add "Toggle Completion" Button
            completion_button_text = "Mark as Complete" if not selected_task[3] else "Mark as Incomplete"
            completion_button = ttk.Button(description_window, text=completion_button_text, command=lambda: toggle_task_completion(selected_task[0]))
            completion_button.pack(pady=10)

            # Bind the context menu for right-click
            description_text.bind("<Button-3>", lambda event: show_context_menu(event, description_text))


def show_context_menu(event, widget):
    context_menu = tk.Menu(widget, tearoff=0)
    context_menu.add_command(label="Copy", command=lambda: copy_text(widget))

    context_menu.post(event.x_root, event.y_root)

def copy_text(widget):
    if isinstance(widget, tk.Text):
        selected_text = widget.get(tk.SEL_FIRST, tk.SEL_LAST)
        guiWindow.clipboard_clear()
        guiWindow.clipboard_append(selected_text)
    elif isinstance(widget, ttk.Label):
        selected_text = widget.cget("text")
        guiWindow.clipboard_clear()
        guiWindow.clipboard_append(selected_text)
        
def set_edit_reminder(task_name, due_date):
    # Ask the user for the number of days before the due date to set or edit the reminder
    days_before = simpledialog.askinteger("Set/Edit Reminder", f"Enter the number of days before the due date for '{task_name}':", minvalue=0)

    # Notify the user about the task with the specified reminder days
    notify_task_due(task_name, due_date, days_before)
        
# defining the function to update the list  
def list_update():
    # Clear listbox
    clear_list()

    # Sort tasks by due date
    sorted_tasks = sorted(tasks, key=lambda x: x[1])

    for i, task in enumerate(sorted_tasks):
        task_title = f"{task[0]}"
        background_color = "#98FB98" if task[3] else "#FFFFFF"
        task_listbox.insert('end', task_title)

        # Apply background color to items using tags
        task_listbox.itemconfig('end', {'bg': background_color}) 
  
# defining the function to delete a task from the list  
def delete_task():
    selected_task_index = task_listbox.curselection()

    try:
        if selected_task_index:
            selected_task_title = task_listbox.get(selected_task_index[0])

            # Find the corresponding task in the tasks list
            selected_task = next((task for task in tasks if task[0] == selected_task_title), None)

            # Display a confirmation messagebox
            confirmation = messagebox.askyesno("Delete Task", f"Are you sure you want to delete the task:\n{selected_task[0]} {selected_task[1]} - {selected_task[2]}?")

            if confirmation:
                # Remove the task from the list
                tasks.remove(selected_task)

                # Update the database
                the_cursor.execute('delete from tasks where title = ? and due_date = ? and description = ?', (selected_task[0], selected_task[1], selected_task[2]))

                # Call the function to update the list
                list_update()

    except Exception as e:
        messagebox.showinfo('Error', 'Error deleting task. Please try again.')
        
  
# function to delete all tasks from the list  
def delete_all_tasks():  
    # displaying a message box to ask user for confirmation  
    message_box = messagebox.askyesno('Delete All', 'Are you sure?')  
    # if the value turns to be True  
    if message_box == True:  
        # using while loop to iterate through the tasks list until it's empty   
        while(len(tasks) != 0):  
            # using the pop() method to pop out the elements from the list  
            tasks.pop()  
        # using the execute() method to execute a SQL statement  
        the_cursor.execute('delete from tasks')  
        # calling the function to update the list  
        list_update()  
  
# function to clear the list  
def clear_list():  
    # using the delete method to delete all entries from the list box  
    task_listbox.delete(0, 'end')  

# function to close the application  
def close():  
    # printing the elements from the tasks list  
    print(tasks)
    # using the destroy() method to close the application  
    guiWindow.destroy()  
  
# function to retrieve data from the database  
def retrieve_database():  
    # using the while loop to iterate through the elements in the tasks list  
    while(len(tasks) != 0):  
        # using the pop() method to pop out the elements from the list  
        tasks.pop()  
    # iterating through the rows in the database table  
    for row in the_cursor.execute('select title, due_date, description, completed from tasks'):  
        # using the append() method to insert the titles from the table in the list  
        tasks.append((row[0], row[1], row[2], row[3])) 

# Initialize main window
guiWindow = tk.Tk()
guiWindow.title("To-Do List Manager")
guiWindow.geometry("800x610+750+250")
guiWindow.resizable(0, 0)

# Set color scheme for main window
guiWindow.configure(bg=color_scheme["header_frame"])

# Initialize connection to the database
the_connection = sql.connect('listOfTasks.db')
the_cursor = the_connection.cursor()
#the_cursor.execute('drop table if exists tasks')
the_cursor.execute('create table if not exists tasks (title text, due_date text, description text, completed INTEGER DEFAULT 0)')

# Define an empty list for tasks
tasks = []

# Define frames
header_frame = tk.Frame(guiWindow, bg=color_scheme["header_frame"])
functions_frame = tk.Frame(guiWindow, bg=color_scheme["functions_frame"])
listbox_frame = tk.Frame(guiWindow, bg=color_scheme["listbox_frame"])

# Pack frames
header_frame.pack(fill="both")
functions_frame.pack(side="left", expand=True, fill="both")
listbox_frame.pack(side="right", expand=True, fill="both")

# Create a listbox to display tasks
task_listbox = tk.Listbox(
    listbox_frame,
    width=39,
    height=13,
    font=("Arial", 12),
    selectmode=tk.SINGLE,
    background=color_scheme["listbox"],
    foreground="#000000",
    selectbackground="#CD853F",
    selectforeground="#FFFFFF"
)

# Create Scrollbars
vertical_scrollbar = ttk.Scrollbar(listbox_frame, orient="vertical", command=task_listbox.yview)
horizontal_scrollbar = ttk.Scrollbar(listbox_frame, orient="horizontal", command=task_listbox.xview)

# Configure Listbox to use Scrollbars
task_listbox.config(yscrollcommand=vertical_scrollbar.set, xscrollcommand=horizontal_scrollbar.set)

# Pack Listbox and Scrollbars
task_listbox.place(x=10, y=20)
vertical_scrollbar.place(x=370, y=20, height=225)
horizontal_scrollbar.place(x=10, y=275, width=230)

# Bind the show_task_description function to double-click event
task_listbox.bind("<Double-Button-1>", lambda event: show_task_description(task_listbox.get(task_listbox.curselection())))

# Define labels, entry fields, and buttons
header_label = ttk.Label(
    header_frame,
    text="The To-Do List",
    font=("Times New Roman", "30", "bold"),
    background=color_scheme["header_frame"],
    foreground="#8B4513"
)
current_date_label = ttk.Label(
    header_frame,
    text=f"Date: {datetime.today().strftime('%Y-%m-%d')}",
    font=("Consolas", "20"),
    background=color_scheme["header_frame"],
    foreground="#8B4513"
)
task_label = ttk.Label(
    functions_frame,
    text="Enter the Task:",
    font=("Consolas", "11", "bold"),
    background=color_scheme["functions_frame"],
    foreground="#000000"
)
task_field = ttk.Entry(
    functions_frame,
    font=("Consolas", "12"),
    width=18,
    background="#FFF8DC",
    foreground="#A52A2A"
)
due_date_entry = ttk.Entry(
    functions_frame,
    font=("Consolas", "12"),
    width=18,
    background="#FFF8DC",
    foreground="#A52A2A"
)
add_button = ttk.Button(
    functions_frame,
    text="Add Task",
    width=24,
    command=add_task
)
toggle_task_completion_button = ttk.Button(
    listbox_frame,
    text="Complete/Incomplete",
    width = 24,
    command = toggle_selected_task_completion
)
del_button = ttk.Button(  
    functions_frame,  
    text = "Delete Task",  
    width = 24,  
    command = delete_task  
)
del_all_button = ttk.Button(  
    functions_frame,  
    text = "Delete All Tasks",  
    width = 24,  
    command = delete_all_tasks  
)
color_picker_button_header_frame = ttk.Button(
    functions_frame,
    text="Pick Header Frame Color",
    width=24,
    command=lambda: choose_color("header_frame")
)
color_picker_button_functions_frame = ttk.Button(
    functions_frame,
    text="Pick Functions Frame Color",
    width=24,
    command=lambda: choose_color("functions_frame")
)
color_picker_button_listbox_frame = ttk.Button(
    functions_frame,
    text="Pick Listbox Frame Color",
    width=24,
    command=lambda: choose_color("listbox_frame")
)
reset_color_button_functions_frame = ttk.Button(
    functions_frame,
    text="Reset to Default",
    width=24,
    command=reset_all_colors_to_default
)
exit_button = ttk.Button(
    functions_frame,
    text="Exit",
    width=24,
    command=guiWindow.destroy
)

# place
header_label.pack(padx=20, pady=20)
current_date_label.pack(padx=5, pady=5, side='top', anchor="center")
task_label.place(x=30, y=40)
task_field.place(x=30, y=80)
due_date_entry.place(x=30, y=120)
add_button.place(x=30, y=150)
toggle_task_completion_button.place(x=10, y=300)
del_button.place(x=30, y=190)
del_all_button.place(x=30, y=230)
color_picker_button_header_frame.place(x=30, y=270)
color_picker_button_functions_frame.place(x=30, y=310)
color_picker_button_listbox_frame.place(x=30, y=350)
reset_color_button_functions_frame.place(x=30, y=390)
exit_button.place(x=30, y=430)

# Update the entry fields with placeholder text
task_field.insert(0, "Enter task here")
due_date_entry.insert(0, "YYYY-MM-DD")

# Bind events to handle clearing the placeholder text when the entry fields are clicked
task_field.bind("<FocusIn>", lambda event: clear_placeholder(event, task_field, "Enter task here"))
due_date_entry.bind("<FocusIn>", lambda event: clear_placeholder(event, due_date_entry, "YYYY-MM-DD"))

# Create a dictionary to map widget names to actual widget objects
widget_mapping = {
    "functions_frame": functions_frame,
    "listbox_frame": listbox_frame,
    "listbox": task_listbox,
    "header_frame": header_frame
}

# Apply initial color scheme
apply_color_scheme()

# Get access to database on startup
retrieve_database()
# Call list_update to load tasks on startup
list_update()
# Run the main loop
guiWindow.mainloop()
the_connection.commit()
the_cursor.close()