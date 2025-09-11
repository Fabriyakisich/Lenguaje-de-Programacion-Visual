# Fernando Arréllaga 4695843
import tkinter as tk
from tkinter import ttk

# Importing tkinter library

# Create the main application window
root = tk.Tk()
root.title("Tkinter Widgets Example")
# Set the dimensions of the main application window
root.geometry("400x400")

# Label: Used to display text or images
label = tk.Label(root, text="This is a Label widget")
label.pack(pady=5)


# Entry: Used to take single-line text input from the user
entry = tk.Entry(root)
entry.pack(pady=4)

# Button: Used to perform an action when clicked
def on_button_click():
    print("Button clicked!")
    print(entry.get())

button = tk.Button(root, text="Click Me", command=on_button_click)
button.pack()

# Text: Used to take multi-line text input from the user
text = tk.Text(root, height=5, width=30)
text.pack()

# Checkbutton: Used to toggle between two states (checked/unchecked)
check_var = tk.BooleanVar()
checkbutton = tk.Checkbutton(root, text="Check Me", variable=check_var)
checkbutton.pack()

# Radiobutton: Used to select one option from a group
radio_var = tk.StringVar(value="Option1")
radiobutton1 = tk.Radiobutton(root, text="Option 1", variable=radio_var, value="Option1")
radiobutton2 = tk.Radiobutton(root, text="Option 2", variable=radio_var, value="Option2")
radiobutton1.pack()
radiobutton2.pack()

# Listbox: Used to display a list of items
listbox = tk.Listbox(root)
listbox.insert(1, "Item 1")
listbox.insert(2, "Item 2")
listbox.insert(3, "Item 3")
listbox.pack()

# Combobox: Dropdown menu (requires ttk module)
combobox = ttk.Combobox(root, values=["Option 1", "Option 2", "Option 3"])
combobox.set("Select an option")
combobox.pack()

# Run the application
root.mainloop()