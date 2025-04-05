import tkinter as tk
from tkinter import messagebox

# Dictionary to store user credentials (username: password)
users = {}

def show_frame(frame):
    """Brings the given frame to the front."""
    frame.tkraise()

def login():
    """Checks the entered credentials against stored users."""
    username = username_entry.get()
    password = password_entry.get()
    if username in users and users[username] == password:
        messagebox.showinfo("Login", "Login Successful!")
    else:
        messagebox.showerror("Login", "Invalid credentials. Please try again.")

def go_to_signup():
    """Clears sign-up fields and shows the sign-up frame."""
    signup_username_entry.delete(0, tk.END)
    signup_password_entry.delete(0, tk.END)
    show_frame(signup_frame)

def signup():
    """Registers a new user if the username is not taken."""
    username = signup_username_entry.get()
    password = signup_password_entry.get()
    if not username or not password:
        messagebox.showerror("Sign Up", "Please enter both a username and password.")
    elif username in users:
        messagebox.showerror("Sign Up", "Username already exists!")
    else:
        users[username] = password
        messagebox.showinfo("Sign Up", "Account created successfully!")
        # Clear the sign-up fields and return to login page
        signup_username_entry.delete(0, tk.END)
        signup_password_entry.delete(0, tk.END)
        show_frame(login_frame)

def go_to_login():
    """Clears login fields and shows the login frame."""
    username_entry.delete(0, tk.END)
    password_entry.delete(0, tk.END)
    show_frame(login_frame)

# Create the main window
root = tk.Tk()
root.title("Login Application")

# Configure grid so frames expand to fill the window
root.rowconfigure(0, weight=1)
root.columnconfigure(0, weight=1)

# Create two frames: one for login and one for sign-up
login_frame = tk.Frame(root)
signup_frame = tk.Frame(root)

for frame in (login_frame, signup_frame):
    frame.grid(row=0, column=0, sticky='nsew')

# -------------------
# Login Frame Setup
# -------------------
tk.Label(login_frame, text="Login", font=('Helvetica', 16)).grid(row=0, column=0, columnspan=2, pady=10)

tk.Label(login_frame, text="Username:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
username_entry = tk.Entry(login_frame)
username_entry.grid(row=1, column=1, padx=10, pady=10)

tk.Label(login_frame, text="Password:").grid(row=2, column=0, padx=10, pady=10, sticky="e")
password_entry = tk.Entry(login_frame, show="*")
password_entry.grid(row=2, column=1, padx=10, pady=10)

tk.Button(login_frame, text="Login", command=login).grid(row=3, column=0, columnspan=2, pady=10)
tk.Button(login_frame, text="Sign Up", command=go_to_signup).grid(row=4, column=0, columnspan=2, pady=10)

# -------------------
# Sign-up Frame Setup
# -------------------
tk.Label(signup_frame, text="Sign Up", font=('Helvetica', 16)).grid(row=0, column=0, columnspan=2, pady=10)

tk.Label(signup_frame, text="Username:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
signup_username_entry = tk.Entry(signup_frame)
signup_username_entry.grid(row=1, column=1, padx=10, pady=10)

tk.Label(signup_frame, text="Password:").grid(row=2, column=0, padx=10, pady=10, sticky="e")
signup_password_entry = tk.Entry(signup_frame, show="*")
signup_password_entry.grid(row=2, column=1, padx=10, pady=10)

tk.Button(signup_frame, text="Sign Up", command=signup).grid(row=3, column=0, columnspan=2, pady=10)
tk.Button(signup_frame, text="Back to Login", command=go_to_login).grid(row=4, column=0, columnspan=2, pady=10)

# Show the login frame first
show_frame(login_frame)

# Start the GUI event loop
root.mainloop()
