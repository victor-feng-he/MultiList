# notification_handler.py
from plyer import notification
from datetime import datetime, timedelta

def notify_task_due(task_name, due_date, description, days_before=0):
    today_date = datetime.today().strftime('%Y-%m-%d')
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