# importing the required modules  
import tkinter as tk                    # importing the tkinter module as tk  
from tkinter import ttk                 # importing the ttk module from the tkinter library  
from tkinter import messagebox          # importing the messagebox module from the tkinter library  
import sqlite3 as sql                   # importing the sqlite3 module as sql  
  
# defining the function to add tasks to the list  
def add_task():  
    # getting the string from the entry field  
    task_string = task_field.get()  
    due_date = due_date_entry.get()
    
    # Open a new window for task description
    description_window = tk.Toplevel(guiWindow)
    description_window.title("Task Description")
    description_window.geometry("300x150")
    

    # Entry field for task description
    description_label = ttk.Label(description_window, text="Task Description:")
    description_label.pack(pady=5)
    
    description_entry = ttk.Entry(description_window, font=("Consolas", "12"), width=25)
    description_entry.pack(pady=5)
    
    # checking whether the string is empty or not  
    if len(task_string) == 0:  
        # displaying a message box with 'Empty Field' message  
        messagebox.showinfo('Error', 'Field is Empty.')  
    else:  
        # adding the string to the tasks list  
        tasks.append((task_string, due_date))  
        # using the execute() method to execute a SQL statement  
        the_cursor.execute('insert into tasks (title, due_date) values (?, ?)', (task_string, due_date))  
        # calling the function to update the list  
        list_update()  
        # deleting the entry in the entry field  
        task_field.delete(0, 'end')
        due_date_entry.delete(0, 'end')
        
def finish_adding_task():
        description = description_entry.get()
        if len(task_string) == 0:
            messagebox.showinfo('Error', 'Field is Empty.')
        else:
            tasks.append((task_string, due_date, description))
            the_cursor.execute('insert into tasks (title, due_date, description) values (?, ?, ?)',
                               (task_string, due_date, description))
            list_update()
            task_field.delete(0, 'end')
            due_date_entry.delete(0, 'end')
            description_entry.delete(0, 'end')
            description_window.destroy()

        # Button to finish adding the task
        finish_button = ttk.Button(description_window, text="Finish", command=finish_adding_task)
        finish_button.pack(pady=10)

def on_hover(event):
    selected_task = task_listbox.get(task_listbox.nearest(event.y))
    if selected_task:
        # Get the task details, including the description
        task_details = next(task for task in tasks if f"{task[0]} - Due Date: {task[1]}" in selected_task)
        task_description_label.config(text=f"Task Description: {task_details[2]}")
    else:
        task_description_label.config(text="Task Description: ")
  
# defining the function to update the list  
def list_update():  
    # calling the function to clear the list  
    clear_list()
    # Sort tasks by due date
    sorted_tasks = sorted(tasks, key=lambda x: x[1])
    # iterating through the strings in the list  
    for task in sorted_tasks:  
        # using the insert() method to insert the tasks in the list box  
        task_listbox.insert('end', f"{task[0]} - {task[1]}")  
  
# defining the function to delete a task from the list  
def delete_task():  
    # using the try-except method  
    try:  
        # getting the selected entry from the list box  
        the_value = task_listbox.get(task_listbox.curselection())  
        # checking if the stored value is present in the tasks list  
        if the_value in tasks:  
            # removing the task from the list  
            tasks.remove(the_value)  
            # calling the function to update the list  
            list_update()  
            # using the execute() method to execute a SQL statement  
            the_cursor.execute('delete from tasks where title = ?', (the_value,))  
    except:  
        # displaying the message box with 'No Item Selected' message for an exception  
        messagebox.showinfo('Error', 'No Task Selected. Cannot Delete.')        
  
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
    for row in the_cursor.execute('select title, due_date from tasks'):  
        # using the append() method to insert the titles from the table in the list  
        tasks.append((row[0], row[1]))  

# main function  
if __name__ == "__main__":  
    # creating an object of the Tk() class  
    guiWindow = tk.Tk()  
    # setting the title of the window  
    guiWindow.title("To-Do List Manager")  
    # setting the geometry of the window  
    guiWindow.geometry("500x450+750+250")  
    # disabling the resizable option  
    guiWindow.resizable(0, 0)  
    # setting the background color to #FAEBD7  
    guiWindow.configure(bg = "#FAEBD7")  
  
    # using the connect() method to connect to the database  
    the_connection = sql.connect('listOfTasks.db')  
    # creating the cursor object of the cursor class  
    the_cursor = the_connection.cursor()  
    # using the execute() method to execute a SQL statement  
    the_cursor.execute('create table if not exists tasks (title text, due_date text)')  
  
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
  
    # defining a list box using the tk.Listbox() widget  
    task_listbox = tk.Listbox(  
        listbox_frame,  
        width = 39,  
        height = 13,  
        selectmode = 'SINGLE',  
        background = "#FFFFFF",  
        foreground = "#000000",  
        selectbackground = "#CD853F",  
        selectforeground = "#FFFFFF"  
    )  
    # using the place() method to place the list box in the application  
    task_listbox.place(x = 10, y = 20)  
  
    # calling some functions  
    retrieve_database()  
    list_update()  
    # using the mainloop() method to run the application  
    guiWindow.mainloop()  
    # establishing the connection with database  
    the_connection.commit()  
    the_cursor.close() 
    
    # Binding the on_hover function to the Enter event for listbox items
    task_listbox.bind("<Enter>", on_hover)

    # Displaying task description label
    task_description_label = ttk.Label(listbox_frame, text="Task Description: ", font=("Consolas", "11", "bold"),
                                        background="#FAEBD7", foreground="#000000")
    task_description_label.place(x=10, y=350)