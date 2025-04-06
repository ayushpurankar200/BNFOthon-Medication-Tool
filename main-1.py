import tkinter as tk
from tkinter import messagebox, simpledialog
import json
import os
import time
from patient_management import PatientManagement
from tkinter import ttk, scrolledtext
import uuid
from datetime import datetime, timedelta
from tkcalendar import Calendar
from plyer import notification  # For system notifications

# Initialize global variables
medications = {}  # Dictionary to store patient medications
medication_tracking = {}  # Dictionary to track medication history
medication_check_windows = {}  # Dictionary to track medication check windows
patient_notes = {}  # Dictionary to store patient notes

# Dictionary to store user credentials and type (username: {'password': password, 'type': user_type})
users = {}

# Initialize PatientManagement
patient_manager = PatientManagement()

# Global variables for physician view widgets
modify_patient_var = None
modify_entries = {}
patient_tree = None
patient_select = None
med_patient_select = None
med_patient_var = None
med_tree = None
med_entries = {}
past_notes_text = None
new_note_text = None
search_entry = None
modify_patient_frame = None
medications_text = None
notes_text = None
password_entry = None

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

def save_medication_tracking():
    """Save medication tracking data to file."""
    try:
        with open('medication_tracking.json', 'w') as file:
            json.dump(medication_tracking, file)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save medication tracking: {str(e)}")

def save_medications():
    """Save medications data to file."""
    try:
        with open('medications.json', 'w') as file:
            json.dump(medications, file)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save medications: {str(e)}")

def show_frame(frame):
    """Brings the given frame to the front."""
    frame.tkraise()

def login():
    """Handle user login"""
    username = username_entry.get()
    password = password_entry.get()
    
    if username in users and users[username]['password'] == password:
        if users[username]['type'] == 'patient':
            show_frame(patient_landing_frame)
            setup_patient_view()  # Set up patient view with calendar and theme support
        else:
            show_frame(physician_landing_frame)
            setup_physician_view()
    else:
        messagebox.showerror("Login Failed", "Invalid username or password")

def go_to_signup():
    """Clears sign-up fields and shows the sign-up frame."""
    signup_username_entry.delete(0, tk.END)
    signup_password_entry.delete(0, tk.END)
    user_type_var.set("")
    show_frame(signup_frame)

def signup():
    """Registers a new user and adds patients to the patient management system."""
    username = signup_username_entry.get()
    password = signup_password_entry.get()
    user_type = user_type_var.get()
    
    if not username or not password:
        messagebox.showerror("Sign Up", "Please enter both a username and password.")
        return
    elif not user_type:
        messagebox.showerror("Sign Up", "Please select whether you are a patient or physician.")
        return
    elif username in users:
        messagebox.showerror("Sign Up", "Username already exists!")
        return

    # Get additional information if the user is a patient
    if user_type == "patient":
        # Create a new window for patient details
        patient_details = tk.Toplevel()
        patient_details.title("Patient Details")
        patient_details.geometry("400x300")

        tk.Label(patient_details, text="Please enter your details", font=('Helvetica', 12)).pack(pady=10)

        tk.Label(patient_details, text="Full Name:").pack(pady=5)
        name_entry = tk.Entry(patient_details)
        name_entry.pack(pady=5)

        tk.Label(patient_details, text="Date of Birth (YYYY-MM-DD):").pack(pady=5)
        dob_entry = tk.Entry(patient_details)
        dob_entry.pack(pady=5)

        tk.Label(patient_details, text="Contact Number:").pack(pady=5)
        contact_entry = tk.Entry(patient_details)
        contact_entry.pack(pady=5)

        def save_patient_details():
            name = name_entry.get()
            dob = dob_entry.get()
            contact = contact_entry.get()

            if not all([name, dob, contact]):
                messagebox.showerror("Error", "Please fill in all fields")
                return

            # Generate a unique patient ID
            patient_id = str(uuid.uuid4())[:8]

            # Add user to users dictionary
            users[username] = {
                'password': password,
                'type': user_type,
                'patient_id': patient_id  # Store patient ID in user data
            }

            # Add patient to patient management system
            patient_manager.add_patient(patient_id, name, dob, contact)
            
            save_users()
            messagebox.showinfo("Success", "Account created successfully!")
            patient_details.destroy()
            show_frame(login_frame)

        tk.Button(patient_details, text="Save", command=save_patient_details).pack(pady=20)

    else:
        # For physicians, just create the account normally
        users[username] = {
            'password': password,
            'type': user_type
        }
        save_users()
        messagebox.showinfo("Success", "Account created successfully!")
        show_frame(login_frame)

    # Clear the sign-up fields
    signup_username_entry.delete(0, tk.END)
    signup_password_entry.delete(0, tk.END)
    user_type_var.set("")

def go_to_login():
    """Clears login fields and shows the login frame."""
    username_entry.delete(0, tk.END)
    password_entry.delete(0, tk.END)
    show_frame(login_frame)

def update_patient_list():
    """Refresh the patient list in the tree view"""
    global patient_tree, patient_select
    
    if patient_tree:
        # Clear existing items
        for item in patient_tree.get_children():
            patient_tree.delete(item)
        
        # Get patients from patient manager
        patients = patient_manager.get_all_patients()
        if patients is None:
            patients = {}  # Initialize empty dictionary if None
            
        # Update dropdowns if they exist
        if patient_select:
            # Create list of patient IDs and names
            patient_list = [f"{pid} - {data.get('name', '')}" for pid, data in patients.items()]
            patient_select['values'] = patient_list
        
        # Add patients to tree view
        for patient_id, data in patients.items():
            patient_tree.insert('', 'end', values=(
                patient_id,
                data.get('name', ''),
                data.get('dob', ''),
                data.get('contact', '')
            ))

def save_modified_patient():
    """Save modified patient information."""
    selected = patient_select.get()
    if not selected:
        messagebox.showerror("Error", "Please select a patient")
        return
    
    # Extract patient ID from the selection (format: "ID - Name")
    selected_username = selected.split(' - ')[0]
    
    # Get form data
    password = password_entry.get()
    if not password:
        messagebox.showerror("Error", "Password cannot be empty")
        return
    
    # Update user data
    if selected_username in users:
        users[selected_username]['password'] = password
        users[selected_username]['notes'] = notes_text.get("1.0", tk.END).strip()
        
        # Parse medications
        med_text = medications_text.get("1.0", tk.END).strip()
        if med_text:
            medications = []
            for line in med_text.split('\n'):
                if line.strip():
                    parts = line.split(' - ')
                    if len(parts) == 2:
                        name = parts[0].strip()
                        rest = parts[1].split(' at ')
                        if len(rest) == 2:
                            dosage = rest[0].strip()
                            time = rest[1].strip()
                            medications.append({
                                'name': name,
                                'dosage': dosage,
                                'time': time
                            })
            users[selected_username]['medications'] = medications
        
        messagebox.showinfo("Success", "Patient data updated successfully")
        show_frame(physician_landing_frame)
    else:
        messagebox.showerror("Error", "Patient not found")

def load_patient_data(event=None):
    """Load and display patient data in the modify patient form."""
    selected = patient_select.get()
    if not selected:
        return
    
    # Extract patient ID from the selection (format: "ID - Name")
    selected_username = selected.split(' - ')[0]
    
    if selected_username not in users:
        return
    
    patient_data = users[selected_username]
    
    # Update form fields
    for field, entry in modify_entries.items():
        if field in patient_data:
            entry.delete(0, tk.END)
            entry.insert(0, str(patient_data[field]))
    
    # Update notes
    if past_notes_text:
        past_notes_text.delete("1.0", tk.END)
        past_notes_text.insert("1.0", patient_data.get('notes', ''))
    
    # Update medications
    if medications_text:
        medications_text.delete("1.0", tk.END)
        if 'medications' in patient_data:
            for med in patient_data['medications']:
                medications_text.insert(tk.END, f"{med['name']} - {med['dosage']} at {med['time']}\n")

def save_medical_note():
    """Save a new medical note for the selected patient."""
    selected = patient_select.get()
    if not selected:
        messagebox.showerror("Error", "Please select a patient")
        return
    
    # Extract patient ID from the selection (format: "ID - Name")
    selected_username = selected.split(' - ')[0]
    
    new_note = new_note_text.get("1.0", tk.END).strip()
    if not new_note:
        messagebox.showerror("Error", "Note cannot be empty")
        return
    
    if selected_username in users:
        if 'notes' not in users[selected_username]:
            users[selected_username]['notes'] = ""
        users[selected_username]['notes'] += f"\n{datetime.now().strftime('%Y-%m-%d %H:%M')}: {new_note}"
        new_note_text.delete("1.0", tk.END)
        load_patient_data()
        messagebox.showinfo("Success", "Note saved successfully")
    else:
        messagebox.showerror("Error", "Patient not found")

def load_patient_medications(event=None):
    """Load and display patient medications in the medication management tab."""
    selected_username = med_patient_select.get()
    if not selected_username or selected_username not in users:
        return
    
    # Clear existing items
    for item in med_tree.get_children():
        med_tree.delete(item)
    
    # Add medications to tree view
    if 'medications' in users[selected_username]:
        for med in users[selected_username]['medications']:
            med_tree.insert('', 'end', values=(
                med['name'],
                med['dosage'],
                med['time'],
                'Active',
                datetime.now().strftime('%Y-%m-%d')
            ))

def clear_med_form():
    """Clear all medication form fields."""
    for entry in med_entries.values():
        if isinstance(entry, tk.Entry):
            entry.delete(0, tk.END)
        elif isinstance(entry, ttk.Combobox):
            entry.set('')
        elif isinstance(entry, scrolledtext.ScrolledText):
            entry.delete("1.0", tk.END)

def update_med_patient_list():
    """Update the patient list in the medication management dropdown."""
    if med_patient_select:
        patient_list = [username for username, data in users.items() if data.get('type') == 'patient']
        med_patient_select['values'] = patient_list

def save_medication():
    """Save a new medication for the selected patient."""
    selected_username = med_patient_select.get()
    if not selected_username:
        messagebox.showerror("Error", "Please select a patient")
        return
    
    # Get form data
    name = med_entries['medication_name'].get()
    dosage = med_entries['dose'].get()
    schedule = med_entries['schedule'].get()
    instructions = med_entries['instructions'].get("1.0", tk.END).strip()
    status = med_entries['status'].get()
    
    if not all([name, dosage, schedule]):
        messagebox.showerror("Error", "Please fill in all required fields")
        return
    
    # Create medication entry
    medication = {
        'name': name,
        'dosage': dosage,
        'time': schedule,
        'instructions': instructions,
        'status': status,
        'start_date': datetime.now().strftime('%Y-%m-%d')
    }
    
    # Add to patient's medications
    if selected_username in users:
        if 'medications' not in users[selected_username]:
            users[selected_username]['medications'] = []
        users[selected_username]['medications'].append(medication)
        messagebox.showinfo("Success", "Medication added successfully")
        clear_med_form()
        load_patient_medications()
    else:
        messagebox.showerror("Error", "Patient not found")

def delete_medication():
    """Delete the selected medication from the patient's record."""
    selected_items = med_tree.selection()
    if not selected_items:
        messagebox.showerror("Error", "Please select a medication to delete")
        return
    
    selected_username = med_patient_select.get()
    if not selected_username:
        messagebox.showerror("Error", "Please select a patient")
        return
    
    # Get the medication name from the selected item
    medication_name = med_tree.item(selected_items[0])['values'][0]
    
    # Confirm deletion
    if not messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {medication_name}?"):
        return
    
    # Remove medication from patient's record
    if selected_username in users and 'medications' in users[selected_username]:
        users[selected_username]['medications'] = [
            med for med in users[selected_username]['medications']
            if med['name'] != medication_name
        ]
        messagebox.showinfo("Success", "Medication deleted successfully")
        load_patient_medications()
    else:
        messagebox.showerror("Error", "Patient not found")

def setup_physician_view():
    """Set up the physician's view with tabs for different functionalities."""
    global patient_tree, patient_select, med_patient_select, med_patient_var, med_tree, med_entries
    global past_notes_text, new_note_text, search_entry
    
    # Clear existing widgets in physician_landing_frame
    for widget in physician_landing_frame.winfo_children():
        widget.destroy()
    
    # Create header
    header_frame = create_header_frame(physician_landing_frame, "Physician Dashboard")
    header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=20)
    
    # Create a notebook for tabbed interface
    notebook = ttk.Notebook(physician_landing_frame)
    notebook.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)
    
    # Configure grid weights
    physician_landing_frame.grid_rowconfigure(1, weight=1)
    physician_landing_frame.grid_columnconfigure(0, weight=1)
    
    # Patient List Tab
    patient_list_frame = ttk.Frame(notebook)
    notebook.add(patient_list_frame, text='Patient List')
    
    # Configure patient list frame grid
    patient_list_frame.grid_rowconfigure(1, weight=1)
    patient_list_frame.grid_columnconfigure(0, weight=1)
    
    # Patient tree view
    columns = ('ID', 'Name', 'DOB', 'Contact')
    patient_tree = ttk.Treeview(patient_list_frame, columns=columns, show='headings')
    
    for col in columns:
        patient_tree.heading(col, text=col)
        patient_tree.column(col, width=100)
    
    # Add scrollbars
    tree_scroll = ttk.Scrollbar(patient_list_frame, orient="vertical", command=patient_tree.yview)
    patient_tree.configure(yscrollcommand=tree_scroll.set)
    
    patient_tree.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
    tree_scroll.grid(row=1, column=1, sticky="ns", pady=5)
    
    # Medical Notes Tab
    notes_frame = ttk.Frame(notebook)
    notebook.add(notes_frame, text='Medical Notes')
    
    # Configure notes frame grid
    notes_frame.grid_rowconfigure(2, weight=1)
    notes_frame.grid_columnconfigure(0, weight=1)
    
    # Patient selection
    selection_frame = ttk.Frame(notes_frame)
    selection_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
    selection_frame.grid_columnconfigure(1, weight=1)
    
    ttk.Label(selection_frame, text="Select Patient:").grid(row=0, column=0, padx=5, sticky="w")
    patient_select = ttk.Combobox(selection_frame, width=40)
    patient_select.grid(row=0, column=1, padx=5, sticky="ew")
    
    # Past notes display
    past_notes_label = ttk.Label(notes_frame, text="Past Medical Notes:")
    past_notes_label.grid(row=1, column=0, padx=5, pady=2, sticky="w")
    
    past_notes_text = scrolledtext.ScrolledText(notes_frame, height=10, wrap=tk.WORD)
    past_notes_text.grid(row=2, column=0, sticky="nsew", padx=5, pady=2)
    
    # New note entry
    new_note_label = ttk.Label(notes_frame, text="Add New Note:")
    new_note_label.grid(row=3, column=0, padx=5, pady=2, sticky="w")
    
    new_note_text = scrolledtext.ScrolledText(notes_frame, height=4, wrap=tk.WORD)
    new_note_text.grid(row=4, column=0, sticky="nsew", padx=5, pady=2)
    
    # Add buttons
    button_frame = ttk.Frame(notes_frame)
    button_frame.grid(row=5, column=0, sticky="ew", padx=5, pady=5)
    button_frame.grid_columnconfigure(1, weight=1)
    
    ttk.Button(button_frame, text="Save Note", command=save_medical_note).grid(row=0, column=0, padx=5)
    ttk.Button(button_frame, text="Refresh", 
               command=lambda: [update_patient_list(), load_patient_data()]).grid(row=0, column=1, padx=5, sticky="e")
    
    # Bind events
    patient_select.bind('<<ComboboxSelected>>', load_patient_data)

    # Medication Management Tab
    med_manage_frame = ttk.Frame(notebook)
    notebook.add(med_manage_frame, text='Medication Management')
    
    # Configure medication management frame grid
    med_manage_frame.grid_rowconfigure(2, weight=1)
    med_manage_frame.grid_columnconfigure(0, weight=1)

    # Patient selection at the top
    med_select_frame = ttk.Frame(med_manage_frame)
    med_select_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
    med_select_frame.grid_columnconfigure(1, weight=1)
    
    ttk.Label(med_select_frame, text="Select Patient:").grid(row=0, column=0, padx=5, sticky="w")
    med_patient_var = tk.StringVar()
    med_patient_select = ttk.Combobox(med_select_frame, textvariable=med_patient_var, width=40)
    med_patient_select.grid(row=0, column=1, padx=5, sticky="ew")

    # Split frame for current medications and new medication form
    med_paned = ttk.PanedWindow(med_manage_frame, orient='vertical')
    med_paned.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

    # Current Medications Section
    current_meds_frame = ttk.LabelFrame(med_paned, text="Current Medications")
    med_paned.add(current_meds_frame)
    
    # Configure current medications frame grid
    current_meds_frame.grid_rowconfigure(0, weight=1)
    current_meds_frame.grid_columnconfigure(0, weight=1)
    
    # Create a frame to hold the tree and scrollbar
    tree_frame = ttk.Frame(current_meds_frame)
    tree_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
    tree_frame.grid_rowconfigure(0, weight=1)
    tree_frame.grid_columnconfigure(0, weight=1)

    # Medication list view
    med_columns = ('Medication', 'Dose', 'Schedule', 'Status', 'Start Date')
    med_tree = ttk.Treeview(tree_frame, columns=med_columns, show='headings', height=6)
    
    # Add vertical scrollbar
    tree_scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=med_tree.yview)
    med_tree.configure(yscrollcommand=tree_scroll.set)
    
    # Add horizontal scrollbar
    tree_scroll_h = ttk.Scrollbar(tree_frame, orient="horizontal", command=med_tree.xview)
    med_tree.configure(xscrollcommand=tree_scroll_h.set)

    for col in med_columns:
        med_tree.heading(col, text=col)
        med_tree.column(col, width=100, minwidth=50)
    
    # Grid the tree and scrollbars
    med_tree.grid(row=0, column=0, sticky="nsew")
    tree_scroll.grid(row=0, column=1, sticky="ns")
    tree_scroll_h.grid(row=1, column=0, sticky="ew")

    # Add/Modify Medication Section
    add_med_frame = ttk.LabelFrame(med_paned, text="Add/Modify Medication")
    med_paned.add(add_med_frame)
    
    # Configure add medication frame grid
    add_med_frame.grid_columnconfigure(1, weight=1)

    # Medication form
    med_entries = {}
    med_fields = [
        ('medication_name', 'Medication Name:'),
        ('dose', 'Dose:'),
        ('schedule', 'Schedule (e.g., "Daily 8 AM"):'),
        ('instructions', 'Instructions:')
    ]

    for i, (field, label) in enumerate(med_fields):
        ttk.Label(add_med_frame, text=label, width=20).grid(row=i, column=0, padx=5, pady=2, sticky="e")
        if field == 'instructions':
            entry = scrolledtext.ScrolledText(add_med_frame, height=3, wrap=tk.WORD)
            entry.grid(row=i, column=1, padx=5, pady=2, sticky="ew")
        else:
            entry = ttk.Entry(add_med_frame)
            entry.grid(row=i, column=1, padx=5, pady=2, sticky="ew")
        med_entries[field] = entry

    # Status selection
    ttk.Label(add_med_frame, text="Status:", width=20).grid(row=len(med_fields), column=0, padx=5, pady=2, sticky="e")
    status_var = tk.StringVar(value="Active")
    status_combo = ttk.Combobox(add_med_frame, textvariable=status_var, 
                               values=["Active", "Discontinued", "On Hold"])
    status_combo.grid(row=len(med_fields), column=1, padx=5, pady=2, sticky="ew")
    med_entries['status'] = status_combo

    # Add buttons for medication management
    med_button_frame = ttk.Frame(add_med_frame)
    med_button_frame.grid(row=len(med_fields) + 1, column=0, columnspan=2, pady=5)
    med_button_frame.grid_columnconfigure(3, weight=1)
    
    ttk.Button(med_button_frame, text="Save Medication", 
               command=save_medication).grid(row=0, column=0, padx=5)
    ttk.Button(med_button_frame, text="Modify Selected", 
               command=modify_selected_medication).grid(row=0, column=1, padx=5)
    ttk.Button(med_button_frame, text="Delete Selected", 
               command=delete_medication).grid(row=0, column=2, padx=5)
    ttk.Button(med_button_frame, text="Clear Form", 
               command=clear_med_form).grid(row=0, column=3, padx=5)
    ttk.Button(med_button_frame, text="Refresh", 
               command=lambda: [update_med_patient_list(), load_patient_medications()]).grid(row=0, column=4, padx=5, sticky="e")
    
    # Bind events
    med_patient_select.bind('<<ComboboxSelected>>', load_patient_medications)
    
    # Initialize the patient list after all widgets are created
    update_patient_list()

def create_header_frame(parent, title):
    """Create a header frame with title and logout button."""
    header_frame = tk.Frame(parent)
    header_frame.pack(fill="x", padx=10, pady=5)
    
    # Title
    tk.Label(header_frame, 
            text=title,
            font=("Arial", 16, "bold")).pack(side="left", padx=20)
    
    # Logout button
    tk.Button(header_frame, 
             text="Logout",
             command=go_to_login).pack(side="right", padx=20)
    
    return header_frame

def show_appointments():
    """Show appointments and medications for the selected date."""
    # Clear existing appointments
    for widget in appointments_frame.winfo_children():
        widget.destroy()
    
    # Get selected date
    selected_date = cal.get_date()
    
    # Create label for selected date
    date_label = tk.Label(appointments_frame, 
                         text=f"Schedule for {selected_date}:",
                         font=("Arial", 12, "bold"))
    date_label.pack(pady=10)
    
    # Get current user's medications
    current_user = username_entry.get()
    if current_user in users and 'medications' in users[current_user]:
        medications = users[current_user]['medications']
        
        # Filter medications for selected date
        date_medications = [med for med in medications if med.get('start_date') <= selected_date]
        
        if date_medications:
            # Create label for medications
            med_label = tk.Label(appointments_frame,
                               text="Medications:",
                               font=("Arial", 10, "bold"))
            med_label.pack(pady=5)
            
            # Display each medication
            for med in date_medications:
                med_frame = tk.Frame(appointments_frame)
                med_frame.pack(fill="x", padx=10, pady=2)
                
                # Medication name and dosage
                tk.Label(med_frame,
                        text=f"{med['name']} - {med['dosage']}",
                        font=("Arial", 10)).pack(side="left")
                
                # Time
                tk.Label(med_frame,
                        text=f"at {med['time']}",
                        font=("Arial", 10)).pack(side="left", padx=10)
        else:
            # No medications for this date
            tk.Label(appointments_frame,
                    text="No medications scheduled for this date.",
                    font=("Arial", 10)).pack(pady=10)
    else:
        # No medications prescribed
        tk.Label(appointments_frame,
                text="No medications prescribed.",
                font=("Arial", 10)).pack(pady=10)

def update_patient_medications():
    """Update the medication display for the current patient."""
    # Clear existing medications
    for widget in medication_display.winfo_children():
        widget.destroy()
    
    # Get current user
    current_user = username_entry.get()
    
    # Create medication list frame
    med_list_frame = tk.Frame(medication_display)
    med_list_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Add title
    tk.Label(med_list_frame,
            text="Current Medications",
            font=("Arial", 12, "bold")).grid(row=0, column=0, pady=10)
    
    # Check if user has medications
    if current_user in users and 'medications' in users[current_user]:
        medications = users[current_user]['medications']
        
        # Add each medication
        for i, med in enumerate(medications, 1):
            med_frame = tk.Frame(med_list_frame)
            med_frame.grid(row=i, column=0, sticky="ew", pady=2)
            med_frame.grid_columnconfigure(1, weight=1)
            
            # Medication name and dosage
            tk.Label(med_frame,
                    text=f"{med['name']} - {med['dosage']}",
                    font=("Arial", 10)).grid(row=0, column=0, sticky="w")
            
            # Time
            tk.Label(med_frame,
                    text=f"at {med['time']}",
                    font=("Arial", 10)).grid(row=0, column=1, sticky="w", padx=10)
            
            # Current streak
            streak = med.get('streak', 0)
            streak_text = "🔥" * streak if streak > 0 else "No streak yet"
            tk.Label(med_frame,
                    text=streak_text,
                    font=("Arial", 10)).grid(row=0, column=2, sticky="e")
            
            # Status and take button
            status_frame = tk.Frame(med_frame)
            status_frame.grid(row=1, column=0, columnspan=3, sticky="ew", pady=5)
            
            # Check if it's time to take the medication
            current_time = datetime.now().strftime("%H:%M")
            med_time = datetime.strptime(med['time'], "%H:%M").strftime("%H:%M")
            time_diff = (datetime.strptime(current_time, "%H:%M") - 
                        datetime.strptime(med_time, "%H:%M")).total_seconds() / 3600
            
            if abs(time_diff) <= 1:  # Within 1 hour window
                status = "Time to take medication"
                status_color = "blue"
                
                # Add take button
                tk.Button(status_frame,
                         text="Take Medication",
                         command=lambda m=med: take_medication(m)).pack(side="right")
            else:
                status = "Next dose pending"
                status_color = "black"
            
            tk.Label(status_frame,
                    text=status,
                    fg=status_color,
                    font=("Arial", 10)).pack(side="left")
    else:
        # No medications
        tk.Label(med_list_frame,
                text="No medications prescribed.",
                font=("Arial", 10)).grid(row=1, column=0, pady=10)

def take_medication(medication):
    """Mark a medication as taken and update streak."""
    current_user = username_entry.get()
    current_time = datetime.now()
    
    # Get medication time
    med_time = datetime.strptime(medication['time'], "%H:%M").time()
    current_time_only = current_time.time()
    
    # Calculate time difference in minutes
    time_diff = (current_time_only.hour * 60 + current_time_only.minute) - \
                (med_time.hour * 60 + med_time.minute)
    
    # Update streak based on timing
    if abs(time_diff) <= 30:  # Within 30 minutes is considered on time
        status = "on_time"
        streak_increment = 1
    else:
        status = "late"
        streak_increment = 0
    
    # Update streak in user data
    if current_user in users:
        if 'medications' in users[current_user]:
            for med in users[current_user]['medications']:
                if med['name'] == medication['name']:
                    if 'streak' not in med:
                        med['streak'] = 0
                    med['streak'] = max(0, med['streak'] + streak_increment)
                    
                    # Add history entry
                    if 'history' not in med:
                        med['history'] = []
                    med['history'].append({
                        'date': current_time.strftime("%Y-%m-%d"),
                        'time': current_time.strftime("%H:%M"),
                        'status': status
                    })
                    break
        
        # Save updated data
        save_users()
        
        # Show notification
        try:
            notification.notify(
                title="Medication Taken",
                message=f"Medication {medication['name']} marked as {status}",
                app_icon=None,
                timeout=5
            )
        except Exception as e:
            print(f"Notification error: {e}")
        
        # Update display
        update_patient_medications()
    else:
        messagebox.showerror("Error", "User not found")

def check_medication_reminders():
    """Check for medication reminders and send notifications."""
    while True:
        current_time = datetime.now()
        current_user = username_entry.get()
        
        if current_user in medications:
            for med in medications[current_user]:
                med_time = datetime.strptime(med['time'], "%H:%M").time()
                current_time_only = current_time.time()
                
                # Check if it's time for medication (within 1 minute of scheduled time)
                if (med_time.hour == current_time_only.hour and 
                    abs(med_time.minute - current_time_only.minute) <= 1):
                    
                    # Create 10-minute window for taking medication
                    window_start = current_time
                    window_end = current_time + timedelta(minutes=10)
                    
                    if current_user not in medication_check_windows:
                        medication_check_windows[current_user] = {}
                    
                    # Only create new window if one doesn't exist for this medication
                    if med['name'] not in medication_check_windows[current_user]:
                        medication_check_windows[current_user][med['name']] = {
                            'window_start': window_start.strftime("%Y-%m-%d %H:%M:%S"),
                            'window_end': window_end.strftime("%Y-%m-%d %H:%M:%S")
                        }
                        
                        # Create tracking entry if it doesn't exist
                        if current_user not in medication_tracking:
                            medication_tracking[current_user] = {}
                        if med['name'] not in medication_tracking[current_user]:
                            medication_tracking[current_user][med['name']] = {
                                'streak': 0,
                                'history': []
                            }
                        
                        # Add new tracking entry
                        medication_tracking[current_user][med['name']]['history'].append({
                            'date': current_time.strftime("%Y-%m-%d"),
                            'time': med['time'],
                            'status': 'pending'
                        })
                        save_medication_tracking()
                        
                        # Send notification
                        try:
                            notification.notify(
                                title="Medication Reminder",
                                message=f"Time to take {med['name']} - {med['dosage']}",
                                app_icon=None,
                                timeout=10
                            )
                        except Exception as e:
                            print(f"Notification error: {e}")
                
                # Check for missed medications (10 minutes after window end)
                elif (med_time.hour == current_time_only.hour and 
                      current_time_only.minute == (med_time.minute + 20) % 60):
                    
                    # If there's a pending entry that hasn't been marked, mark it as missed
                    if (current_user in medication_tracking and 
                        med['name'] in medication_tracking[current_user]):
                        
                        for entry in reversed(medication_tracking[current_user][med['name']]['history']):
                            if entry['status'] == 'pending' and entry['date'] == current_time.strftime("%Y-%m-%d"):
                                entry['status'] = 'missed'
                                medication_tracking[current_user][med['name']]['streak'] = 0
                                save_medication_tracking()
                                update_patient_medications()
                                break
        
        time.sleep(30)  # Check every 30 seconds

def update_patient_notes():
    """Update the notes display for the current patient."""
    current_user = username_entry.get()
    if current_user in patient_notes:
        notes_text.delete("1.0", tk.END)
        notes_text.insert("1.0", patient_notes[current_user])
    else:
        notes_text.delete("1.0", tk.END)

def update_physician_patient_view():
    """Update the physician's view of patient information."""
    # Clear existing widgets
    for widget in physician_patient_frame.winfo_children():
        widget.destroy()
    
    # Create header
    header_frame = create_header_frame(physician_patient_frame, "Patient Information")
    header_frame.pack(fill="x", padx=10, pady=5)
    
    # Create main container
    main_frame = tk.Frame(physician_patient_frame)
    main_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Patient selection
    selection_frame = tk.Frame(main_frame)
    selection_frame.pack(fill="x", pady=10)
    
    tk.Label(selection_frame,
            text="Select Patient:",
            font=("Arial", 10)).pack(side="left", padx=5)
    
    # Get list of patients
    patient_list = [user for user, data in users.items() if data.get('type') == 'patient']
    patient_list.sort()
    
    # Create dropdown
    patient_var = tk.StringVar()
    patient_dropdown = ttk.Combobox(selection_frame, textvariable=patient_var, values=patient_list)
    patient_dropdown.pack(side="left", padx=5)
    
    # Load button
    tk.Button(selection_frame,
             text="Load",
             command=lambda: load_patient_data(patient_var.get())).pack(side="left", padx=5)
    
    # Patient information display
    info_frame = tk.LabelFrame(main_frame, text="Patient Details")
    info_frame.pack(fill="both", expand=True, pady=10)
    
    # Create text widget for patient information
    info_text = scrolledtext.ScrolledText(info_frame, wrap=tk.WORD)
    info_text.pack(fill="both", expand=True, padx=10, pady=10)
    
    def load_patient_data(selected_patient):
        """Load and display patient data."""
        global medications_text, notes_text, password_entry
        
        if not selected_patient:
            messagebox.showerror("Error", "Please select a patient")
            return
        
        # Clear existing text
        info_text.delete(1.0, tk.END)
        
        # Get patient data
        if selected_patient in users:
            patient_data = users[selected_patient]
            
            # Display basic information
            info_text.insert(tk.END, f"Patient: {selected_patient}\n\n")
            
            # Display medications
            if 'medications' in patient_data and patient_data['medications']:
                info_text.insert(tk.END, "Current Medications:\n")
                for med in patient_data['medications']:
                    info_text.insert(tk.END, f"- {med['name']} ({med['dosage']}) at {med['time']}\n")
                    if 'schedule' in med:
                        info_text.insert(tk.END, f"  Schedule: {med['schedule']}\n")
                    info_text.insert(tk.END, "\n")
            else:
                info_text.insert(tk.END, "No medications prescribed.\n\n")
            
            # Display notes
            if 'notes' in patient_data and patient_data['notes']:
                info_text.insert(tk.END, "Notes:\n")
                info_text.insert(tk.END, patient_data['notes'])
        else:
            info_text.insert(tk.END, "Patient not found.")
    
    # Add back button
    tk.Button(main_frame,
             text="Back to Dashboard",
             command=lambda: show_frame(physician_landing_frame)).pack(pady=10)

def search_patient():
    patient_username = search_entry.get()
    if patient_username in users and users[patient_username]['type'] == 'patient':
        update_physician_patient_view()
    else:
        messagebox.showerror("Error", "Patient not found")

def add_medication():
    """Add a new medication reminder."""
    # Get patient username
    patient_username = simpledialog.askstring("Add Medication", "Enter patient's username:")
    if not patient_username or patient_username not in users:
        messagebox.showerror("Error", "Invalid patient username")
        return
    
    # Get medication details
    name = simpledialog.askstring("Add Medication", "Enter medication name:")
    if not name:
        return
        
    dosage = simpledialog.askstring("Add Medication", "Enter dosage:")
    if not dosage:
        return
        
    time_str = simpledialog.askstring("Add Medication", "Enter time (HH:MM):")
    if not time_str:
        return
    
    # Create medication entry
    medication = {
        'name': name,
        'dosage': dosage,
        'time': time_str,
        'prescribed_by': username_entry.get()  # Store who prescribed the medication
    }
    
    # Add to medications dictionary
    if patient_username not in medications:
        medications[patient_username] = []
    
    medications[patient_username].append(medication)
    save_medications()
    
    # Initialize tracking for the new medication
    if patient_username not in medication_tracking:
        medication_tracking[patient_username] = {}
    if name not in medication_tracking[patient_username]:
        medication_tracking[patient_username][name] = {
            'streak': 0,
            'history': []
        }
    save_medication_tracking()
    
    # Update display
    if users[username_entry.get()]['type'] == 'physician':
        update_physician_patient_view()
    else:
        update_patient_medications()

def display_patient_medications():
    """Display medications for the current patient."""
    current_user = username_entry.get()
    if current_user not in users or 'medications' not in users[current_user]:
        return
    
    # Clear existing medications
    for widget in medication_display.winfo_children():
        widget.destroy()
    
    # Create medication list frame
    med_list_frame = tk.Frame(medication_display)
    med_list_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Add title
    tk.Label(med_list_frame, 
            text="Your Medications",
            font=("Arial", 12, "bold")).grid(row=0, column=0, pady=10)
    
    # Display each medication
    for i, med in enumerate(users[current_user]['medications'], 1):
        med_frame = tk.Frame(med_list_frame)
        med_frame.grid(row=i, column=0, sticky="ew", pady=2)
        
        # Medication details
        tk.Label(med_frame,
                text=f"{med['name']} - {med['dosage']}",
                font=("Arial", 10)).grid(row=0, column=0, sticky="w")
        
        tk.Label(med_frame,
                text=f"Take at: {med['time']}",
                font=("Arial", 10)).grid(row=1, column=0, sticky="w")
        
        if 'instructions' in med and med['instructions']:
            tk.Label(med_frame,
                    text=f"Instructions: {med['instructions']}",
                    font=("Arial", 10)).grid(row=2, column=0, sticky="w")

def setup_patient_view():
    """Set up the patient's view with calendar and medication display."""
    global cal, appointments_frame, medications_frame, notes_frame, notes_text, medication_display
    
    # Clear existing widgets in patient_landing_frame
    for widget in patient_landing_frame.winfo_children():
        widget.destroy()
    
    # Create header
    header_frame = create_header_frame(patient_landing_frame, "Patient Dashboard")
    header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=20)
    
    # Create main container frame
    main_frame = ttk.Frame(patient_landing_frame)
    main_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)
    
    # Configure grid weights
    patient_landing_frame.grid_rowconfigure(1, weight=1)
    patient_landing_frame.grid_columnconfigure(0, weight=1)
    main_frame.grid_rowconfigure(0, weight=1)
    main_frame.grid_columnconfigure(0, weight=1)
    main_frame.grid_columnconfigure(1, weight=1)
    
    # Calendar Section
    calendar_frame = ttk.LabelFrame(main_frame, text="Calendar")
    calendar_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
    calendar_frame.grid_rowconfigure(1, weight=1)
    calendar_frame.grid_columnconfigure(0, weight=1)
    
    # Create calendar
    cal = Calendar(calendar_frame, selectmode='day')
    cal.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
    
    # Appointments display
    appointments_frame = ttk.Frame(calendar_frame)
    appointments_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
    appointments_frame.grid_rowconfigure(0, weight=1)
    appointments_frame.grid_columnconfigure(0, weight=1)
    
    # Medications Section
    medications_frame = ttk.LabelFrame(main_frame, text="Medications")
    medications_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
    medications_frame.grid_rowconfigure(0, weight=1)
    medications_frame.grid_columnconfigure(0, weight=1)
    
    # Create medication display
    medication_display = ttk.Frame(medications_frame)
    medication_display.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
    medication_display.grid_rowconfigure(0, weight=1)
    medication_display.grid_columnconfigure(0, weight=1)
    
    # Add refresh button for medications
    refresh_button = ttk.Button(medications_frame, text="Refresh Medications", 
                              command=display_patient_medications)
    refresh_button.grid(row=1, column=0, sticky="e", padx=5, pady=5)
    
    # Notes Section
    notes_frame = ttk.LabelFrame(main_frame, text="Notes")
    notes_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
    notes_frame.grid_rowconfigure(0, weight=1)
    notes_frame.grid_columnconfigure(0, weight=1)
    
    # Add scrollable text area for notes
    notes_text = scrolledtext.ScrolledText(notes_frame, wrap=tk.WORD)
    notes_text.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
    
    # Add save button for notes
    notes_button_frame = ttk.Frame(notes_frame)
    notes_button_frame.grid(row=1, column=0, sticky="e", padx=5, pady=5)
    
    def save_notes():
        current_user = username_entry.get()
        if current_user:
            patient_notes[current_user] = notes_text.get("1.0", tk.END).strip()
            messagebox.showinfo("Success", "Notes saved successfully!")
    
    ttk.Button(notes_button_frame, text="Save Notes", command=save_notes).pack(side="right", padx=5)
    
    # Update initial display
    display_patient_medications()
    update_patient_notes()

def modify_selected_medication():
    """Load selected medication into form for editing"""
    selected_items = med_tree.selection()
    if not selected_items:
        messagebox.showwarning("Warning", "Please select a medication to modify")
        return

    # Get values from selected item
    values = med_tree.item(selected_items[0])['values']
    
    # Fill form with selected medication data
    med_entries['medication_name'].delete(0, tk.END)
    med_entries['medication_name'].insert(0, values[0])
    
    med_entries['dose'].delete(0, tk.END)
    med_entries['dose'].insert(0, values[1])
    
    med_entries['schedule'].delete(0, tk.END)
    med_entries['schedule'].insert(0, values[2])
    
    med_entries['status'].set(values[3])

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
physician_patient_frame = tk.Frame(root)

for frame in (login_frame, signup_frame, patient_landing_frame, physician_landing_frame, physician_patient_frame):
    frame.grid(row=0, column=0, sticky='nsew')

# -------------------
# Login Frame Setup
# -------------------

# Center frame container
login_container = tk.Frame(login_frame)
login_container.place(relx=0.5, rely=0.5, anchor="center")

tk.Label(login_container, text="Login", font=('Helvetica', 24, 'bold')).grid(row=0, column=0, columnspan=2, pady=(0,20))

tk.Label(login_container, text="Username:", font=('Helvetica', 12)).grid(row=1, column=0, padx=10, pady=10, sticky="e")
username_entry = tk.Entry(login_container, font=('Helvetica', 12), width=20)
username_entry.grid(row=1, column=1, padx=10, pady=10)

tk.Label(login_container, text="Password:", font=('Helvetica', 12)).grid(row=2, column=0, padx=10, pady=10, sticky="e")
password_entry = tk.Entry(login_container, show="*", font=('Helvetica', 12), width=20)
password_entry.grid(row=2, column=1, padx=10, pady=10)

button_frame = tk.Frame(login_container)
button_frame.grid(row=3, column=0, columnspan=2, pady=20)

tk.Button(button_frame, text="Login", command=login, font=('Helvetica', 12), width=10).pack(side=tk.LEFT, padx=5)
tk.Button(button_frame, text="Sign Up", command=go_to_signup, font=('Helvetica', 12), width=10).pack(side=tk.LEFT, padx=5)

# Configure login frame grid weights
login_frame.grid_rowconfigure(0, weight=1)
login_frame.grid_columnconfigure(0, weight=1)

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

# Show the login frame first
show_frame(login_frame)

# Start the GUI event loop
root.mainloop()

# Save user data when the application closes
save_users()