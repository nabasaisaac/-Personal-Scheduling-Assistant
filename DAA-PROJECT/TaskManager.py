
import bisect
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sb
sb.set_style("whitegrid")


"""
Initializes the SchedulingAssistant object.
- self.tasks: List to store tasks with details such as start time, end time, type, task name, and priority.
- self.reminders: List to store reminders for tasks, specifically one hour before their deadlines.
"""
class SchedulingAssistant:
    def __init__(self):

        self.tasks = []  # List to store tasks
        self.reminders = []  # List to store reminders

    # The add_task method creates a new task, adds it to the self.task list and sets reminder for it
    def add_task(self, start, end, task_type, task_name, priority):

        # Add the task to the list while maintaining sorted order by start time
        bisect.insort(self.tasks, (start, end, task_type, task_name, priority)) # The bisect.insort adds a new task to the list while maintaining the sorted order of the list
        self.schedule_reminder(end,task_name)  # calls the schedule reminder method to set a reminder for the created task
        print("Task added successfully!")


    # The schedule_reminder method sets a reminder for the created task
    def schedule_reminder(self, deadline, task_name):
        if not isinstance(deadline, datetime) or not isinstance(task_name, str): # validating the deadline and task_name
            print("Invalid reminder data. Reminder not scheduled.")
            return
        reminder_time = deadline - timedelta(hours=1) # Setting the reminder time to be an hour before the deadline time of any task
        self.reminders.append((reminder_time, deadline, task_name)) # Appending the new task's name, deadline and reminder to the self.reminders list
        print(f"Reminder set for task '{task_name}' at {reminder_time.strftime('%Y-%m-%d %H:%M')}")


    """
    Checks and displays the scheduled reminders.
    Displays reminders that are set for tasks one hour before their deadline.
    """
    def check_reminders(self):

        now = datetime.now()  # Get the current time

        # Check reminders that are upcoming
        upcoming_reminders = [reminder for reminder in self.reminders if reminder[0] >= now]

        if not upcoming_reminders:
            print("No upcoming reminders.")
            return

        print("\nUpcoming Reminders:")
        for reminder in upcoming_reminders:
            try:
                # Unpack reminder tuple
                reminder_time, deadline, task_name = reminder  
                print(f"Reminder set for task '{task_name}' due at {deadline.strftime('%Y-%m-%d %H:%M')} "
                    f"at {reminder_time.strftime('%Y-%m-%d %H:%M')}")
            except ValueError:
                print(f"Invalid reminder format: {reminder}")


    # The check deadlines methods Checks for tasks that are missed and upcoming.
    def check_deadlines(self):

        now = datetime.now()  # Current date and time
        # Tasks whose deadlines have passed
        missed_tasks = [task for task in self.tasks if task[1] < now]
        # Tasks with deadlines in the future
        upcoming_tasks = [task for task in self.tasks if task[1] >= now]

        # Print missed tasks
        print("\nMissed Deadlines:")
        for task in missed_tasks:
            print(f"{task[3]} (Deadline: {task[1]})")

        # Print the next 5 upcoming tasks
        print("\nUpcoming Tasks:")
        for task in upcoming_tasks[:5]:  # Limit to the next 5 tasks
            print(f"{task[3]} (Deadline: {task[1]})")


    """
    Finds the optimal schedule of non-overlapping tasks using dynamic programming.
    Ensures the maximum number of tasks are completed without conflicts.
    """
    def prioritize_tasks(self):

        print("\nOptimizing Task Schedule...")
        if not self.tasks:  # If no tasks exist
            print("No tasks to prioritize.")
            return

        # Sort tasks by their end time (earlier deadlines take priority)
        sorted_tasks = merge_sort(self.tasks, key=lambda x: x[1])

        # Initialize dynamic programming arrays
        n = len(sorted_tasks)  # Total number of tasks
        dp = [0] * n  # dp[i]: Maximum tasks that can be scheduled up to index i
        dp_schedule = [[] for _ in range(n)]  # Stores the schedule for dp[i]

        # Iterate over sorted tasks
        for i in range(n):
            # Include the current task
            incl = 1  # Count the current task
            incl_schedule = [sorted_tasks[i]]  # Start with the current task

            # Find the last task that does not overlap using a reverse loop
            for j in range(i - 1, -1, -1):
                if sorted_tasks[j][1] <= sorted_tasks[i][0]:  # Check for non-overlap
                    incl += dp[j]  # Add the max tasks up to the previous non-overlapping task
                    incl_schedule += dp_schedule[j]  # Add its schedule
                    break

            # Exclude the current task
            excl = dp[i - 1] if i > 0 else 0  # Max tasks up to the previous index
            excl_schedule = dp_schedule[i - 1] if i > 0 else []

            # Choose the better option (include or exclude the current task)
            if incl > excl:
                dp[i] = incl
                dp_schedule[i] = incl_schedule
            else:
                dp[i] = excl
                dp_schedule[i] = excl_schedule

        # Display results
        print(f"Maximum non-overlapping tasks: {dp[-1]}")
        print("Optimized Task List:")
        for task in dp_schedule[-1]:
            print(f"Start: {task[0]}, End: {task[1]}, Type: {task[2]}, task_name: {task[3]}, Priority: {task[4]}")

    # The display task method shows all the tasks in self.task
    def display_tasks(self):

        if not self.tasks:
            print("No tasks available.")
            return

        print("\nTasks List:")
        for task in self.tasks:
            print(f"Start: {task[0].strftime('%Y-%m-%d %H:%M')}, "
                f"End: {task[1].strftime('%Y-%m-%d %H:%M')}, "
                f"Type: {task[2]}, "
                f"task_name: {task[3]}, "
                f"Priority: {task[4]}")


    def sort_tasks(self, key='deadline'):
        """
        Sorts tasks based on the specified criteria.
        - key: Sorting criterion ('deadline', 'priority', or 'type').
        """
        if key == 'deadline':
            self.tasks = merge_sort(self.tasks, key=lambda x: x[1])  # Sort by deadline
        elif key == 'priority':
            self.tasks = merge_sort(self.tasks, key=lambda x: -x[4])  # Sort by priority (descending)
        elif key == 'type':
            self.tasks = merge_sort(self.tasks, key=lambda x: x[2])  # Sort by task type
        
        print("\nTasks sorted based on:", key)
        self.display_tasks()  # Display the tasks after sorting

    # Analyzes busy time slots based on task density within specific intervals.
    def analyze_busy_slots(self, interval_minutes=60):

        if not self.tasks:
            print("No tasks available to analyze.")
            return

        # Define the start and end of the day
        start_of_day = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)

        # Generate time intervals
        time_slots = [start_of_day + timedelta(minutes=i) for i in range(0, 1440, interval_minutes)]

        # Count tasks in each time slot
        slot_counts = []
        for i, slot_start in enumerate(time_slots):
            slot_end = slot_start + timedelta(minutes=interval_minutes)
            count = sum(1 for task in self.tasks if task[0] < slot_end and task[1] > slot_start)
            slot_counts.append((slot_start, slot_end, count))

        # Sort slots by task density
        slot_counts.sort(key=lambda x: -x[2])

        # Display results
        print(f"Busy Time Slots (sorted by task density, interval: {interval_minutes} minutes):")
        for slot_start, slot_end, count in slot_counts:
            print(f"From {slot_start.strftime('%H:%M')} to {slot_end.strftime('%H:%M')}: {count} tasks")

    # Generates a Gantt chart to visualize task schedules.
    def plot_gantt_chart(self):

        # Separate personal and academic tasks
        personal_tasks = [(task[0], task[1], task[3]) for task in self.tasks if task[2] == 'personal']
        academic_tasks = [(task[0], task[1], task[3]) for task in self.tasks if task[2] == 'academic']

        fig, ax = plt.subplots(figsize=(15, 10))  # Create a figure for the Gantt chart
        bar_height = 0.4  # Height of each bar in the chart

        # Plot personal tasks
        for i, task in enumerate(personal_tasks, 1):
            duration = (task[1] - task[0]).total_seconds() / 3600  # Task duration in hours
            ax.barh(i, duration, left=task[0].hour, height=bar_height, color='blue', label='Personal' if i == 1 else "")
            # Annotate the task on the bar
            ax.text(task[0].hour + duration / 2, i, f"{task[2]} ({task[0].strftime('%Y-%m-%d')})", ha='center', va='center', color='white', fontsize=8)

        # Plot academic tasks
        for i, task in enumerate(academic_tasks, len(personal_tasks) + 1):
            duration = (task[1] - task[0]).total_seconds() / 3600
            ax.barh(i, duration, left=task[0].hour, height=bar_height, color='green', label='Academic' if i == len(personal_tasks) + 1 else "")
            ax.text(task[0].hour + duration / 2, i, f"{task[2]} ({task[0].strftime('%Y-%m-%d')})", ha='center', va='center', color='white', fontsize=8)

        ax.set_xlabel('Time (Hours)')  # Label the x-axis
        ax.set_ylabel('Tasks')  # Label the y-axis
        ax.set_title('Gantt Chart of Tasks')  # Title of the chart
        ax.legend()  # Add a legend for task types
        plt.show()  # Display the Gantt chart


    def search_task(self, keyword):
        """
        Searches for tasks by a keyword in the task_name.
        - keyword: Search term (string).
        """
        results = [task for task in self.tasks if keyword.lower() in task[3].lower()]
        if results:
            print("\nSearch Results:")
            for task in results:
                print(f"Start: {task[0]}, End: {task[1]}, Type: {task[2]}, task_name: {task[3]}, Priority: {task[4]}")
        else:
            print("No tasks found with that keyword.")

# Sorts data using the merge sort algorithm. and a specific key entered
def merge_sort(data, key=lambda x: x):

    if len(data) <= 1:
        return data
    mid = len(data) // 2
    left = merge_sort(data[:mid], key)
    right = merge_sort(data[mid:], key)
    return merge(left, right, key)

def merge(left, right, key):
    """
    Merges two sorted lists into one sorted list.
    """
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if key(left[i]) <= key(right[j]):
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result


# The main function creates the user interface in the terminal
def main():
    assistant = SchedulingAssistant()

    while True:
        print("\nPersonal Scheduling Assistant")
        print("1. Add Task")
        print("2. Sort Tasks")
        print("3. Check Deadlines")
        print("4. Optimize Task Schedule")
        print("5. Plot Gantt Chart")
        print("6. Check Reminders")
        print("7. Search Task")
        print("8. Analyze Task Density")
        print("9. Exit")

        choice = input("Enter your choice: ")
        if choice == '1':
            start = datetime.strptime(input("Enter start time (YYYY-MM-DD HH:MM): "), "%Y-%m-%d %H:%M")
            end = datetime.strptime(input("Enter end time (YYYY-MM-DD HH:MM): "), "%Y-%m-%d %H:%M")
            task_type = input("Enter task type (personal/academic): ")
            task_name = input("Enter task task_name: ")
            priority = int(input("Enter task priority (1-10): "))
            assistant.add_task(start, end, task_type, task_name, priority)
        elif choice == '2':
            key = input("Sort by (deadline/priority/type): ")
            assistant.sort_tasks(key)
        elif choice == '3':
            assistant.check_deadlines()
        elif choice == '4':
            assistant.prioritize_tasks()
        elif choice == '5':
            assistant.plot_gantt_chart()
        elif choice == '6':
            assistant.check_reminders()
        elif choice == '7':
            keyword = input("Enter keyword to search: ")
            assistant.search_task(keyword)
        elif choice == '8':
            interval_minutes = int(input("Enter time interval in minutes (default 60): ") or 60)
            assistant.analyze_busy_slots(interval_minutes)

        elif choice == '9':
            break
        else:
            print("Invalid choice. Try again!")
        

if __name__ == "__main__":
    main()




