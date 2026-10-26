# Schedule planner
sunday=[]
monday=[]
tuesday=[]
wednesday=[]
thursday=[]
friday=[]
saturday=[]
week=[sunday, monday, tuesday, wednesday, thursday, friday, saturday]


def add_task(day, time, task): #adds a task and time as a list to the list for the requested day
    day.append([time, task])

def remove_task(day, time): #removes the list object at the time the user says to remove
   for i in range(len(day)):
       if day[i][0] == time:
            print("Task,", day[i][1], ", removed successfully.")
            del day[i]
            return True #terrminates loop
       else: #error
            print("Task not found.")
            return False #terrminates loop
def view_schedule(): #prints out the schedule
    print("Your Schedule:")
    days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"] #holds the names of the days
    for i in range(len(week)):
        print(days[i], ":") 
        if len(week[i])>0:
            for j in range(len(week[i])):
                print( week[i][j][0], " - ", week[i][j][1])
            
        

while True: #main loop
    print("Welcome to the schedule planner!")
    print("1. Add a task")
    print("2. remove a task")
    print("3. View schedule")
    print("4. Exit")
    choice = input("Enter your choice: ").lower()

    if choice == "1": #calls Add_task()
        day_choice = input("Enter the day (sunday, monday, tuesday, wednesday, thursday, friday, saturday): ").lower()
        time = input("Enter the time (e.g., 14:00): ")
        task = input("Enter the task: ")

        if day_choice == "sunday" or day_choice == "sun" :
            add_task(sunday, time, task)
        elif day_choice == "monday" or day_choice == "mon" :
            add_task(monday, time, task)
        elif day_choice == "tuesday" or day_choice == "tues":
            add_task(tuesday, time, task)
        elif day_choice == "wednesday" or day_choice == "wed" :
            add_task(wednesday, time, task)
        elif day_choice == "thursday" or day_choice == "thurs":
            add_task(thursday, time, task)
        elif day_choice == "friday" or day_choice == "fri" :
            add_task(friday, time, task)
        elif day_choice == "saturday" or day_choice == "sat" :
            add_task(saturday, time, task)
        else:
            print("Invalid day entered.")

    elif choice == "2": #calls remove_task()
        day_choice = input("Enter the day (sunday, monday, tuesday, wednesday, thursday, friday, saturday): ").lower()
        time = input("Enter the time of the task to remove (e.g., 14:00): ")

        if day_choice == "sunday" or day_choice == "sun" :
            remove_task(sunday, time)
        elif day_choice == "monday" or day_choice == "mon" :
            remove_task(monday, time)
        elif day_choice == "tuesday" or day_choice == "tues":
            remove_task(tuesday, time)
        elif day_choice == "wednesday" or day_choice == "wed" :
            remove_task(wednesday, time)
        elif day_choice == "thursday" or day_choice == "thurs":
            remove_task(thursday, time)
        elif day_choice == "friday" or day_choice == "fri" :
            remove_task(friday, time)
        elif day_choice == "saturday" or day_choice == "sat" :
            remove_task(saturday, time)
        else:
            print("Invalid day entered.")
    elif choice == "3" or choice == "view": #calls view_schedule
        view_schedule()
    elif choice == "4" or choice == "exit" or choice == "Exit" or choice == "quit" or choice == "Quit": #exits the program
        print("Exiting the schedule planner.")
        break

    else: #error for invalid choice
        print("Invalid choice. Please try again.")
