# importing the required modules  
import re                               # importing the re module 
from plyer import notification
from datetime import date               # importing the date class from the datetime library
from datetime import datetime           # importing the datetime class from the datetime library
from datetime import timedelta          # importing the timedelta class from the datetime library
import tkinter as tk                    # importing the tkinter module as tk  
from tkinter import ttk                 # importing the ttk module from the tkinter library  
from tkinter import messagebox          # importing the messagebox module from the tkinter library 
from tkinter import simpledialog        # importing the simpledialog module from the tkinter library
import sqlite3 as sql                   # importing the sqlite3 module as sql  
  
# Define a global list to keep track of open description windows
open_description_windows = []

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
    tasks.append((task_string, due_date, description))
    the_cursor.execute('insert into tasks (title, due_date, description) values (?, ?, ?)',
                       (task_string, due_date, description))
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
    notify_task_due(task_string, due_date, days_before)

def notify_task_due(task_name, due_date, days_before=0):
    today_date = datetime.today().strftime('%Y-%m-%d')
    due_datetime = datetime.strptime(due_date, '%Y-%m-%d')

    # Calculate the reminder date by subtracting the specified number of days
    reminder_date = due_datetime - timedelta(days=days_before)

    if today_date == reminder_date.strftime('%Y-%m-%d'):
        notification_title = f"Task Reminder: {task_name}"
        notification_message = f"Your task '{task_name}' is due in {days_before} days on {due_date}."

        # You can customize the notification duration, toast=False for other platforms
        notification.notify(
            title=notification_title,
            message=notification_message,
            app_icon=None  # You can provide the path to an icon if you have one
        )
        
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

    # Set the current due date as a placeholder in the entry field
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
        tasks[selected_task_index] = (selected_task[0], new_due_date, selected_task[2])

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
        
        if existing_window and existing_window.winfo_exists():
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

    if selected_task:
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
        
def set_edit_reminder(task_name, due_date):
    # Ask the user for the number of days before the due date to set or edit the reminder
    days_before = simpledialog.askinteger("Set/Edit Reminder", f"Enter the number of days before the due date for '{task_name}':", minvalue=0)

    # Notify the user about the task with the specified reminder days
    notify_task_due(task_name, due_date, days_before)
        
# defining the function to update the list  
def list_update():  
    # calling the function to clear the list  
    clear_list()
    # Sort tasks by due date
    sorted_tasks = sorted(tasks, key=lambda x: x[1])
    # iterating through the strings in the list  
    for task in sorted_tasks:  
        # using the insert() method to insert the tasks in the list box  
        task_listbox.insert('end', f"{task[0]}")  
  
# defining the function to delete a task from the list  
def delete_task():
    selected_task_index = task_listbox.curselection()

    try:
        if selected_task_index:
            selected_task = tasks[selected_task_index[0]]

            # Display a confirmation messagebox
            confirmation = messagebox.askyesno("Delete Task", f"Are you sure you want to delete the task:\n{selected_task[0]} {selected_task[1]} - {selected_task[2]}?")

            if confirmation:
                # Remove the task from the list
                tasks.remove(selected_task)

                # Update the database
                the_cursor.execute('delete from tasks where title = ? and due_date = ? and description = ?', selected_task)

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
    for row in the_cursor.execute('select title, due_date, description from tasks'):  
        # using the append() method to insert the titles from the table in the list  
        tasks.append((row[0], row[1], row[2]))  

# main function  
if __name__ == "__main__":  
    # creating an object of the Tk() class  
    guiWindow = tk.Tk()  
    # setting the title of the window  
    guiWindow.title("To-Do List Manager")  
    # setting the geometry of the window  
    guiWindow.geometry("550x450+750+250")  
    # disabling the resizable option  
    #guiWindow.resizable(0, 0)  
    # setting the background color to #FAEBD7  
    guiWindow.configure(bg = "#FAEBD7")  
  
    # using the connect() method to connect to the database  
    the_connection = sql.connect('listOfTasks.db')  
    # creating the cursor object of the cursor class  
    the_cursor = the_connection.cursor()  
    # using the execute() method to execute a SQL statement  
    #the_cursor.execute('drop table if exists tasks')
    the_cursor.execute('create table if not exists tasks (title text, due_date text, description text)')  
  
    # defining an empty list  
    tasks = []  
      
    # defining frames using the tk.Frame() widget  
    header_frame = tk.Frame(guiWindow, bg = "#FAEBD7")  
    functions_frame = tk.Frame(guiWindow, bg = "#FAEBD7")  
    listbox_frame = tk.Frame(guiWindow, bg = "#FAEBD7")  
  
    # using the pack() method to place the frames in the application  
    header_frame.pack(fill = "both")  
    functions_frame.pack(side = "left", expand = True, fill = "both")  
    listbox_frame.pack(side = "right", expand = True, fill = "both")
    
    # defining a list box using the tk.Listbox() widget  
    task_listbox = tk.Listbox(  
        listbox_frame,  
        width=39,  
        height=13,  
        selectmode='SINGLE',  
        background="#FFFFFF",  
        foreground="#000000",  
        selectbackground="#CD853F",  
        selectforeground="#FFFFFF"  
    )  
    
    # Creating Scrollbars
    vertical_scrollbar = ttk.Scrollbar(listbox_frame, orient="vertical", command=task_listbox.yview)
    horizontal_scrollbar = ttk.Scrollbar(listbox_frame, orient="horizontal", command=task_listbox.xview)

    # Configuring Listbox to use Scrollbars
    task_listbox.config(yscrollcommand=vertical_scrollbar.set, xscrollcommand=horizontal_scrollbar.set)
    
    # using the place() method to place the list box and scrollbars in the application
    task_listbox.place(x=10, y=20)
    vertical_scrollbar.place(x=250, y=20, height=225)
    horizontal_scrollbar.place(x=10, y=245, width=230)  

    # Binding the show_task_description function to double-click event
    task_listbox.bind("<Double-Button-1>", lambda event: show_task_description(task_listbox.get(task_listbox.curselection())))
      
    # defining a label using the ttk.Label() widget  
    header_label = ttk.Label(  
        header_frame,  
        text = "The To-Do List",  
        font = ("Brush Script MT", "30"),  
        background = "#FAEBD7",  
        foreground = "#8B4513"  
    )  
    # using the pack() method to place the label in the application  
    header_label.pack(padx = 20, pady = 20)  
  
    # defining another label using the ttk.Label() widget  
    task_label = ttk.Label(  
        functions_frame,  
        text = "Enter the Task:",  
        font = ("Consolas", "11", "bold"),  
        background = "#FAEBD7",  
        foreground = "#000000"  
    )  
    # using the place() method to place the label in the application  
    task_label.place(x = 30, y = 40)  
      
    # defining an entry field using the ttk.Entry() widget  
    task_field = ttk.Entry(  
        functions_frame,  
        font = ("Consolas", "12"),  
        width = 18,  
        background = "#FFF8DC",  
        foreground = "#A52A2A"  
    )  
    # using the place() method to place the entry field in the application  
    task_field.place(x = 30, y = 80)

    due_date_entry = ttk.Entry(
    functions_frame,
    font=("Consolas", "12"),
    width=18,
    background="#FFF8DC",
    foreground="#A52A2A"
    )
    
    # using the place() method to place the entry field in the application
    due_date_entry.place(x=30, y=120)
    
    # Update the entry fields with placeholder text
    task_field.insert(0, "Enter task here")
    due_date_entry.insert(0, "YYYY-MM-DD")

    # Bind events to handle clearing the placeholder text when the entry fields are clicked
    task_field.bind("<FocusIn>", lambda event: clear_placeholder(event, task_field, "Enter task here"))
    due_date_entry.bind("<FocusIn>", lambda event: clear_placeholder(event, due_date_entry, "YYYY-MM-DD"))

    # adding buttons to the application using the ttk.Button() widget  
    add_button = ttk.Button(  
        functions_frame,  
        text = "Add Task",  
        width = 24,  
        command = add_task  
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
    exit_button = ttk.Button(  
        functions_frame,  
        text = "Exit",  
        width = 24,  
        command = close  
    )
    
    # using the place() method to set the position of the buttons in the application  
    add_button.place(x = 30, y = 150)  
    del_button.place(x = 30, y = 190)  
    del_all_button.place(x = 30, y = 230)  
    exit_button.place(x = 30, y = 270)  
    
    # calling some functions  
    retrieve_database()  
    list_update()  
    # using the mainloop() method to run the application  
    guiWindow.mainloop()
    # establishing the connection with database  
    the_connection.commit()
    the_cursor.close() 