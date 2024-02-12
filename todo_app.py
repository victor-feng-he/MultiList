# importing the required modules  
import re                               # importing the re module 
from plyer import notification
from datetime import date               # importing the date class from the datetime library
from datetime import datetime           # importing the datetime class from the datetime library
from datetime import timedelta
import tkinter as tk                    # importing the tkinter module as tk  
from tkinter import ttk                 # importing the ttk module from the tkinter library  
from tkinter import messagebox          # importing the messagebox module from the tkinter library 
from tkinter import simpledialog
import sqlite3 as sql                   # importing the sqlite3 module as sql  
  
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
        if due_date:
            if not is_valid_date_format(due_date):
                messagebox.showinfo('Error', 'Invalid Date Format. Use YYYY-MM-DD.')
                # return early if the date format is invalid
                return  
            elif not is_valid_date(due_date):
                messagebox.showinfo('Error', 'Invalid Date. Please enter a valid date.')
                # return early if the date format is invalid
                return

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
        finish_button = ttk.Button(description_window, text="Finish", command=lambda: finish_adding_task(description_window, description_entry, task_string, due_date))
        finish_button.pack(pady=10)

def is_valid_date_format(date_string):
    # Check if the date string has the format 'YYYY-MM-DD'
    return bool(re.match(r'\d{4}-\d{2}-\d{2}$', date_string))

def is_valid_date(date_string):
    try:
        # Check if the date string is a valid date
        datetime.strptime(date_string, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def finish_adding_task(description_window, description_entry, task_string, due_date):
    description = description_entry.get()
    tasks.append((task_string, due_date, description))
    the_cursor.execute('insert into tasks (title, due_date, description) values (?, ?, ?)',
                       (task_string, due_date, description))
    list_update()
    task_field.delete(0, 'end')
    due_date_entry.delete(0, 'end')
    description_entry.delete(0, 'end')
    description_window.destroy()

    # Enable the "Add Task" button after finishing adding the description
    add_button['state'] = 'normal'

    # Notify the user about the task on the due date
    notify_task_due(task_string, due_date)

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
            timeout=10,
            app_icon=None  # You can provide the path to an icon if you have one
        )

# defining function to display task description when task item has been clicked on
def show_task_description():
    selected_task_index = task_listbox.curselection()
    if selected_task_index:
        selected_task = tasks[selected_task_index[0]]
        # Retrieve task name, description, and due date of the selected item
        task_name = selected_task[0]
        description = selected_task[2]
        due_date = selected_task[1]

        # Check if a window for this task description already exists
        existing_windows = guiWindow.winfo_children()
        for window in existing_windows:
            if isinstance(window, tk.Toplevel) and window.title() == task_name and window.winfo_children():
                # Assuming description label is the second child
                description_label = window.winfo_children()[1]  
                if description_label.cget("text") == description:
                    # Bring the existing window to the front
                    window.lift()
                    return

        # Create a new window for task description
        description_window = tk.Toplevel(guiWindow)
        description_window.title(task_name)
        description_window.geometry("300x200")

        description_label = ttk.Label(description_window, text="Task Description:")
        description_label.pack(pady=5)

        description_text = ttk.Label(description_window, text=description, font=("Consolas", "12"))
        description_text.pack(pady=10)

        date_label = ttk.Label(description_window, text="Due Date:")
        date_label.pack(pady=5)

        date_text = ttk.Label(description_window, text=due_date, font=("Consolas", "12"))
        date_text.pack(pady=10)

        # Button to set or edit the reminder
        set_reminder_button = ttk.Button(description_window, text="Set/Edit Reminder", command=lambda: set_edit_reminder(task_name, due_date))
        set_reminder_button.pack(pady=10)
        
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
        task_listbox.insert('end', f"{task[0]} {task[1]}")  
  
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

    # Binding the show_task_description function to double-click event for listbox items
    task_listbox.bind("<Double-Button-1>", lambda event: show_task_description())

    # Displaying task description label
    task_description_label = ttk.Label(listbox_frame, text="Task Description: ", font=("Consolas", "11", "bold"),
                                        background="#FAEBD7", foreground="#000000")
    task_description_label.place(x=10, y=350)
      
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
    
    due_date_label = ttk.Label(
    functions_frame,
    text="Due Date:",
    font=("Consolas", "11", "bold"),
    background="#FAEBD7",
    foreground="#000000"
    )
    due_date_label.place(x=30, y=280)

    due_date_entry = ttk.Entry(
    functions_frame,
    font=("Consolas", "12"),
    width=18,
    background="#FFF8DC",
    foreground="#A52A2A"
    )
    due_date_entry.place(x=30, y=320)

  
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
    add_button.place(x = 30, y = 120)  
    del_button.place(x = 30, y = 160)  
    del_all_button.place(x = 30, y = 200)  
    exit_button.place(x = 30, y = 240)  
    
    # calling some functions  
    retrieve_database()  
    list_update()  
    # using the mainloop() method to run the application  
    guiWindow.mainloop()
    # establishing the connection with database  
    the_connection.commit()
    the_cursor.close() 