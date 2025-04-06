import json
from datetime import datetime

class PatientManagement:
    def __init__(self):
        self.patients_file = 'patients.json'
        self.patients = self.load_patients()

    def load_patients(self):
        """Load patients from JSON file, create if doesn't exist"""
        try:
            with open(self.patients_file, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            # Create empty patients file
            empty_data = {}
            with open(self.patients_file, 'w') as file:
                json.dump(empty_data, file)
            return empty_data
        except json.JSONDecodeError:
            print("Error reading patients file. Creating new one.")
            empty_data = {}
            with open(self.patients_file, 'w') as file:
                json.dump(empty_data, file)
            return empty_data

    def save_patients(self):
        """Save patients to JSON file"""
        try:
            with open(self.patients_file, 'w') as file:
                json.dump(self.patients, file, indent=4)
            return True
        except Exception as e:
            print(f"Error saving patients: {e}")
            return False

    def add_patient(self, patient_id, name, dob, contact):
        """Add a new patient"""
        if patient_id not in self.patients:
            self.patients[patient_id] = {
                'name': name,
                'dob': dob,
                'contact': contact,
                'medications': [],
                'medical_notes': []
            }
            return self.save_patients()
        return False

    def add_medication_history(self, patient_id, medication):
        if patient_id in self.patients:
            medication['date_prescribed'] = str(datetime.now())
            self.patients[patient_id]['medications'].append(medication)
            self.save_patients()
            return True
        return False

    def get_patient_history(self, patient_id):
        """Get patient history by ID"""
        return self.patients.get(patient_id)

    def get_all_patients(self):
        """Get all patients sorted by name"""
        return self.patients

    def modify_patient(self, patient_id, updated_data):
        """Modify patient information while preserving medical data"""
        if patient_id in self.patients:
            # Preserve medical data
            medical_notes = self.patients[patient_id].get('medical_notes', [])
            medications = self.patients[patient_id].get('medications', [])
            
            # Update patient info
            self.patients[patient_id].update(updated_data)
            
            # Restore medical data
            self.patients[patient_id]['medical_notes'] = medical_notes
            self.patients[patient_id]['medications'] = medications
            
            return self.save_patients()
        return False

    def add_medical_note(self, patient_id, note):
        """Add a medical note to patient record"""
        if patient_id in self.patients:
            if 'medical_notes' not in self.patients[patient_id]:
                self.patients[patient_id]['medical_notes'] = []
            
            new_note = {
                'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'note': note
            }
            
            self.patients[patient_id]['medical_notes'].append(new_note)
            return self.save_patients()
        return False

    def add_medication(self, patient_id, medication_data):
        """Add or update a medication for a patient"""
        if patient_id in self.patients:
            if 'medications' not in self.patients[patient_id]:
                self.patients[patient_id]['medications'] = []
            
            # Check if medication already exists
            existing_med = None
            for i, med in enumerate(self.patients[patient_id]['medications']):
                if med['medication_name'] == medication_data['medication_name']:
                    existing_med = i
                    break
                
            if existing_med is not None:
                # Update existing medication
                self.patients[patient_id]['medications'][existing_med] = medication_data
            else:
                # Add new medication
                self.patients[patient_id]['medications'].append(medication_data)
            
            return self.save_patients()
        return False

    def get_medication_history(self, patient_id):
        if patient_id in self.patients:
            return self.patients[patient_id].get('medications', [])
        return []

    def update_medication_status(self, patient_id, medication_name, new_status):
        if patient_id in self.patients:
            for med in self.patients[patient_id].get('medications', []):
                if med['medication_name'] == medication_name:
                    med['status'] = new_status
                    med['last_modified'] = str(datetime.now())
                    self.save_patients()
                    return True
        return False

    def get_patient_by_name(self, name):
        """Get patient ID by name"""
        for patient_id, data in self.patients.items():
            if data.get('name') == name:
                return patient_id
        return None