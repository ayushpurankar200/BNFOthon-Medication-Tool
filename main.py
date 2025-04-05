import tkinter as tk
from tkinter import messagebox
import json
import os

# Dictionary to store user credentials and type (username: {'password': password, 'type': user_type})
users = {}

def load_users():
    """Load user data from file if it exists."""
    global users
    try:
        if os.path.exists('users.json'):
            with open('users.json', 'r') as file:
                users = json.load(file)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load user data: {str(e)}")

def save_users():
    """Save user data to file."""
    try:
        with open('users.json', 'w') as file:
            json.dump(users, file)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save user data: {str(e)}")

def show_frame(frame):
    """Brings the given frame to the front."""
    frame.tkraise()

def login():
    """Checks the entered credentials against stored users."""
    username = username_entry.get()
    password = password_entry.get()
    if username in users and users[username]['password'] == password:
        messagebox.showinfo("Login", "Login Successful!")
        if users[username]['type'] == 'patient':
            show_frame(patient_landing_frame)
        else:
            show_frame(physician_landing_frame)
    else:
        messagebox.showerror("Login", "Invalid credentials. Please try again.")

def go_to_signup():
    """Clears sign-up fields and shows the sign-up frame."""
    signup_username_entry.delete(0, tk.END)
    signup_password_entry.delete(0, tk.END)
    user_type_var.set("")
    show_frame(signup_frame)

def signup():
    """Registers a new user if the username is not taken."""
    username = signup_username_entry.get()
    password = signup_password_entry.get()
    user_type = user_type_var.get()
    
    if not username or not password:
        messagebox.showerror("Sign Up", "Please enter both a username and password.")
    elif not user_type:
        messagebox.showerror("Sign Up", "Please select whether you are a patient or physician.")
    elif username in users:
        messagebox.showerror("Sign Up", "Username already exists!")
    else:
        users[username] = {
            'password': password,
            'type': user_type
        }
        messagebox.showinfo("Sign Up", "Account created successfully!")
        # Clear the sign-up fields and return to login page
        signup_username_entry.delete(0, tk.END)
        signup_password_entry.delete(0, tk.END)
        user_type_var.set("")  # Reset the user type selection
        show_frame(login_frame)

def go_to_login():
    """Clears login fields and shows the login frame."""
    username_entry.delete(0, tk.END)
    password_entry.delete(0, tk.END)
    show_frame(login_frame)

# Create the main window
root = tk.Tk()
root.title("Login Application")

# Load existing user data
load_users()

# Configure grid so frames expand to fill the window
root.rowconfigure(0, weight=1)
root.columnconfigure(0, weight=1)

# Create three frames: one for login, one for sign-up, and one for landing page
login_frame = tk.Frame(root)
signup_frame = tk.Frame(root)
patient_landing_frame = tk.Frame(root)
physician_landing_frame = tk.Frame(root)

for frame in (login_frame, signup_frame, patient_landing_frame, physician_landing_frame):
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

# Add user type selection
tk.Label(signup_frame, text="User Type:").grid(row=3, column=0, padx=10, pady=10, sticky="e")
user_type_var = tk.StringVar()
user_type_frame = tk.Frame(signup_frame)
user_type_frame.grid(row=3, column=1, padx=10, pady=10, sticky="w")
tk.Radiobutton(user_type_frame, text="Patient", variable=user_type_var, value="patient").pack(side="left")
tk.Radiobutton(user_type_frame, text="Physician", variable=user_type_var, value="physician").pack(side="left")

tk.Button(signup_frame, text="Sign Up", command=signup).grid(row=4, column=0, columnspan=2, pady=10)
tk.Button(signup_frame, text="Back to Login", command=go_to_login).grid(row=5, column=0, columnspan=2, pady=10)

# -------------------
# Patient Landing Page Frame Setup
# -------------------
tk.Label(patient_landing_frame, text="Patient Dashboard", font=('Helvetica', 16)).grid(row=0, column=0, columnspan=2, pady=20)

# Patient Information Section
info_frame = tk.LabelFrame(patient_landing_frame, text="Your Information", padx=10, pady=10)
info_frame.grid(row=1, column=0, columnspan=2, padx=20, pady=10, sticky="ew")

tk.Label(info_frame, text="Name:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
name_entry = tk.Entry(info_frame)
name_entry.grid(row=0, column=1, padx=5, pady=5)

tk.Label(info_frame, text="Age:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
age_entry = tk.Entry(info_frame)
age_entry.grid(row=1, column=1, padx=5, pady=5)

tk.Label(info_frame, text="Medical History:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
medical_history_text = tk.Text(info_frame, height=4, width=30)
medical_history_text.grid(row=2, column=1, padx=5, pady=5)

# Buttons Section
button_frame = tk.Frame(patient_landing_frame)
button_frame.grid(row=2, column=0, columnspan=2, pady=20)

tk.Button(button_frame, text="View Appointments", width=15).pack(side="left", padx=5)
tk.Button(button_frame, text="View Prescriptions", width=15).pack(side="left", padx=5)
tk.Button(button_frame, text="View Test Results", width=15).pack(side="left", padx=5)

# Logout Button
tk.Button(patient_landing_frame, text="Logout", 
          command=lambda: [show_frame(login_frame), username_entry.delete(0, tk.END), password_entry.delete(0, tk.END)]
          ).grid(row=3, column=0, columnspan=2, pady=20)

# -------------------
# Physician Landing Page Frame Setup
# -------------------
tk.Label(physician_landing_frame, text="Physician Dashboard", font=('Helvetica', 16)).grid(row=0, column=0, columnspan=2, pady=20)

tk.Label(physician_landing_frame, text="You have successfully logged in as a physician!", font=('Helvetica', 12)).grid(row=1, column=0, columnspan=2, pady=10)

tk.Button(physician_landing_frame, text="Logout", 
          command=lambda: [show_frame(login_frame), username_entry.delete(0, tk.END), password_entry.delete(0, tk.END)]
          ).grid(row=2, column=0, columnspan=2, pady=20)

# Show the login frame first
show_frame(login_frame)

# Start the GUI event loop
root.mainloop()

# Save user data when the application closes
save_users()
