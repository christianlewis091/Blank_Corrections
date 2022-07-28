# Program to make a simple, entry and return screen.

import tkinter as tk

root = tk.Tk()

# setting the windows size
root.geometry("600x400")

# declaring string variable
# for storing name and password
name_var = tk.StringVar()
age_var = tk.StringVar()

# defining a function that will
# get the name and password and
# print them on the screen
def submit():
    name = name_var.get()
    age = age_var.get()

    print(f"my name is {name}, and I am {age} years old")


name_label = tk.Label(root, text='name')  # create the USERNAME label
age_label = tk.Label(root, text='age')  # create the PASSWORD label

name_entry = tk.Entry(root, textvariable=name_var)  # create the entry field for the name, text variable grabs the variable
age_entry = tk.Entry(root, textvariable=age_var)  # create the entry field for the password

sub_btn = tk.Button(root, text='Submit', command=submit)  # this button calls the function

# placing the label and entry in
# the required position using grid
# method
name_label.grid(row=0, column=0)
name_entry.grid(row=0, column=1)
age_label.grid(row=1, column=0)
age_entry.grid(row=1, column=1)
sub_btn.grid(row=2, column=1)

# performing an infinite loop
# for the window to display
root.mainloop()
