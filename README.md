# MultiList
## About The Project
![image](https://github.com/user-attachments/assets/28dc3e19-863a-40f9-9246-f7e1208e593f)

MultiList is a to-do list manager app built using python and the Visual Studio Community IDE. The app uses various python libraries and APIs to provide a multi-functional to-do list app with desktop notifications, color customization, and more. This README will guide you through the setup process, as well as provide insights into the technologies used and how to contribute to the project.

## Table of Contents
* [Project Overview](https://github.com/victor-feng-he/MultiList/blob/main/README.md#project-overview)
* [Features](https://github.com/victor-feng-he/MultiList/blob/main/README.md#features)
* [Technologies](https://github.com/victor-feng-he/MultiList/blob/main/README.md#technologies)
* [Installation](https://github.com/victor-feng-he/MultiList/blob/main/README.md#installation)
* [Usage](https://github.com/victor-feng-he/MultiList/blob/main/README.md#usage)
* [Contributing](https://github.com/victor-feng-he/MultiList/blob/main/README.md#contributing)
* [License](https://github.com/victor-feng-he/MultiList/blob/main/README.md#license)

## Project Overview
MultiList is a to-do list manager app in which users can add tasks to the sqlite3 listOfTasks database, delete tasks, check them off as complete/incomplete, and other managerial features. With a variety of options in managing task items and customization options, the to-do list app is an easy-to-use application suitable for anyone who needs to keep track of their tasks.

## Features
* Intuitive UI: All buttons are properly labeled with their respective functions, making the app easy to use.
* Color Customization: Users can pick from a variety of colors to change the appearance of the app. The colors are also saved in-between sessions.
* Notification System: Using the Plyer library, users can receive a desktop notification when the system time aligns with the due date of a task item.
* Task Management: Users can edit the due dates of tasks that have already been added to the task list, delete all tasks at once, add descriptions to tasks upon their creation, and indicate the completion status of specific tasks.

## Technologies
The project is built using Python, utilizing the following major libraries and modules:

### Python Libraries:

* tkinter: Python library for creating Graphical User Interfaces (GUIs), elements of which include windows, buttons, text fields, etc.
* datetime: Used for manipulating dates as well as for use by the Plyer API.

### Python Modules:

* re: used for manipulating strings based on matching patterns (error validation for improper inputs in text fields).
* Plyer: A platform-independent Python API to implement desktop notification functionality.
* sqlite3: Allows for creation of listOfTasks database using Python code; db used for managing tasks.

### Development Tools:

* Visual Studio for writing the Python code of the project.

## Installation

1. Clone the repository (or download zip file):
```
git clone https://github.com/yourusername/multilist.git
```
2. Open the Multilist project file:

* Go to Dist file.
* Look for this: ![image](https://github.com/user-attachments/assets/e074449f-7c05-469d-8419-2fa0f2f56f49)


3. Run the app:

Double-click on the todo_app application

## Usage
1. Buttons:

* Add Task button functions as the enter button once the user has at least filled out the first text field with a task name (datetime field is optional).
* Delete Task button will delete the task selected by the user in the list, indicated by the highlighting.
* Delete All Tasks button deletes all the tasks in the listOfTask db.
* Pick Header Frame Color, Pick Functions Frame Color, and Pick Listbox Frame Color buttons will change the color of the top, left, and right portions of the app respectively.
* Reset to Default button resets all colors to default.
* Exit button will exit the app. Color changes and task(s) info is preserved.

## Contributing
Feel free to make any changes or additions to MultiList! If you'd like to add new features, fix bugs, or improve performance, please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Commit your changes.
4. Push your changes to your fork and submit a pull request.

You can directly edit the source file by opening the todo_app Python source file: ![image](https://github.com/user-attachments/assets/384e1afe-aa3c-47cc-ab0f-4a006a59932f)

## License
This project is licensed under the Personal License.
