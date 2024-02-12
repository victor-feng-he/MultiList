# importing the required modules  
import tkinter as tk                    # importing the tkinter module as tk  
from tkinter import ttk                 # importing the ttk module from the tkinter library  
from tkinter import messagebox          # importing the messagebox module from the tkinter library  
import sqlite3 as sql                   # importing the sqlite3 module as sql  
  
# defining the function to add tasks to the list  
def add_task():  
    global description_entry, task_string, due_date, add_button
    # getting the string from the entry field  
    task_string = task_field.get()  
    due_date = due_date_entry.get()
    
    # checking whether the string is empty or not  
    if len(task_string) == 0:  
        # displaying a message box with 'Empty Field' message  
        messagebox.showinfo('Error', 'Field is Empty.')
    else:
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

# defining the function to finishing the process of adding a task to the list with a task description
def finish_adding_task(description_window, description_entry, task_string, due_date):
    description = description_entry.get()
    tasks.append((task_string, due_date, description, tk.BooleanVar(value=False)))
    the_cursor.execute('insert into tasks (title, due_date, description, completed) values (?, ?, ?, ?)',
                           (task_string, due_date, description, False))
    list_update()
    task_field.delete(0, 'end')
    due_date_entry.delete(0, 'end')
    description_entry.delete(0, 'end')
    description_window.destroy()
        
    # Enable the "Add Task" button after finishing adding the description
    add_button['state'] = 'normal'

# defining function to toggle whether a task has been completed or not
def toggle_completion(task_index):
    tasks[task_index][3].set(not tasks[task_index][3].get())
    list_update()

# defining function to display task description when task item has been clicked on
def show_task_description():
    selected_task_index = task_listbox.curselection()
    if selected_task_index:
        selected_task = tasks[selected_task_index[0]]
        # Retrieve task name and description of selected item
        task_name = selected_task[0]
        description = selected_task[2]

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
        description_window.geometry("300x150")

        description_label = ttk.Label(description_window, text="Task Description:")
        description_label.pack(pady=5)

        description_text = ttk.Label(description_window, text=description, font=("Consolas", "12"))
        description_text.pack(pady=10)
        
# defining the function to update the list  
def list_update():
    # calling the function to clear the list
    clear_list()
    # Sort tasks by due date
    sorted_tasks = sorted(tasks, key=lambda x: x[1])
    # iterating through the strings in the list
    for i, task in enumerate(sorted_tasks):
        checkbox = ttk.Checkbutton(task_listbox, variable=task[3], command=lambda i=i: toggle_completion(i))
        task_listbox.insert('end', f"{task[0]} {task[1]} {'Completed' if task[3].get() else 'Not Completed'}")
        task_listbox.itemconfig(i, {'bg': '#FFFFFF'})  # Set default background color
        if task[3].get():
            task_listbox.itemconfig(i, {'bg': '#98FB98'})  # Light green background for completed tasks  
  
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
  
def toggle_selected_task_completion():
    selected_task_index = task_listbox.curselection()
    if selected_task_index:
        selected_task = tasks[selected_task_index[0]]
        selected_task[3].set(not selected_task[3].get())
        list_update()

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
    the_cursor.execute('drop table if exists tasks')
    the_cursor.execute('create table if not exists tasks (title text, due_date text, description text, completed text)')  
  
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
    
    # Create the Check/Uncheck button
    toggle_button = ttk.Button(
    listbox_frame,
    text="Check/Uncheck",
    width=40,
    command=toggle_selected_task_completion
    )
    toggle_button.place(x=10, y=270)
    
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