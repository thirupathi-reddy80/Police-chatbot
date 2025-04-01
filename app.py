from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import json
import random
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a random secret key

# Load user data from JSON file
def load_users(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            return json.load(file)
    return {}

# Save user data to JSON file
def save_users(file_path, users):
    with open(file_path, 'w') as file:
        json.dump(users, file)

# Load structured data from JSON file
def load_data(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

# Route for the home page
@app.route('/')
def home():
    return render_template('index1.html')  # Show login page

# Route for login page
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data['email']
    password = data['password']
    
    # Load users from JSON file
    users = load_users('users.json')
    
    if email in users and users[email]['password'] == password:
        session['username'] = email
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

# Route for registration page
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data['email']
    password = data['password']
    names = data['names']
    surnames = data['surnames']
    phone= data['phone']
    address = data['address']
        
    # Load existing users
    users = load_users('users.json')
    
    if email in users:
        return jsonify({'success': False, 'message': 'User  already exists'}), 400
    
    # Save new user
    users[email] = {
        'names': names,
        'surnames': surnames,
        'password': password  # In a real application, hash the password
    }
    save_users('users.json', users)
    
    return jsonify({'success': True})

# Route to handle chatbot queries
@app.route('/ask', methods=['POST'])
def ask():
    user_input = request.json['user_input'].lower()
    data = load_data('police_data.json')  # Load your existing police data
    ipc_data = load_data('police_section.json')  # Load the IPC sections data

    # General conversation
    if any(word in user_input for word in ["hi", "hello", "hey"]):
        response = [random.choice(data['general_conversation']['greetings'])]
    elif any(word in user_input for word in ["who are you", "what are you"]):
        response = [random.choice(data['general_conversation']['introduction'])]
    elif any(word in user_input for word in ["bye", "goodbye"]):
        response = [random.choice(data['general_conversation']['farewell'])]
    elif any(word in user_input for word in ["thank you", "thanks"]):
        response = [random.choice(data['general_conversation']['thanks'])]
    elif any(word in user_input for word in ["available", "24/7"]):
        response = [random.choice(data['general_conversation']['availability'])]
    elif any(word in user_input for word in ["what can you do", "capabilities"]):
        response = [random.choice(data['general_conversation']['capabilities'])]
    
    # FIR Filing
    elif any(word in user_input for word in ["fir", "complaint", "file a report"]):
        response = [
            "To file an FIR (First Information Report), follow these steps:",
            "1. Visit the Nearest Police Station: Go to the police station closest to where the incident occurred.",
            "2. Provide Incident Details: Clearly explain the incident, including date, time, location, and any other relevant information.",
            "3. Submit Identification Proof: Provide a valid ID proof (e.g., Aadhar Card, Passport, or Driving License).",
            "4. Obtain FIR Copy: Once the FIR is registered, ensure you receive a signed copy for your records.",
            "Note: In some states, you can file an FIR online for non-emergency cases. Check your state police website for details."
        ]
    
    # Emergency Contacts
    elif any(word in user_input for word in ["emergency", "contact", "helpline", "number"]):
        state_found = False
        for state in data['emergency_contacts']['state_specific']:
            if state in user_input:
                state_found = True
                if any(word in user_input for word in ["women", "women helpline"]):
                    response = [f"Women Helpline Number for {state.replace('_', ' ').title()}: {data['emergency_contacts']['state_specific'][state]['women_helpline']}"]
                elif any(word in user_input for word in ["police", "police number"]):
                    response = [f"Police Control Room Number for {state.replace('_', ' ').title()}: {data['emergency_contacts']['state_specific'][state]['police_control_room']}"]
                else:
                    response = [
                        f"Here are the emergency contact numbers for {state.replace('_', ' ').title()}:",
                        f"- Police: {data['emergency_contacts']['state_specific'][state]['police_control_room']}",
                        f"- Women Helpline: {data['emergency_contacts']['state_specific'][state]['women_helpline']}",
                        f"- Traffic Helpline: {data['emergency_contacts']['state_specific'][state]['traffic_helpline']}"
                    ]
                break
        
        if not state_found:
            response = [
                "Here are the national emergency contact numbers:",
                "- Police: 100",
                "- Ambulance: 102",
                "- Fire Brigade: 101",
                "- Women Helpline: 1091",
                "- Child Helpline: 1098",
                "For state-specific contacts, please specify your state (e.g., 'emergency contacts for state name')."
            ]
    
    # Police Investigation Procedures
    elif any(word in user_input for word in ["procedure", "investigation", "police process"]):
        response = [
            "The police investigation process involves the following steps:",
            "1. FIR Registration: The FIR is filed based on the complaint.",
            "2. Evidence Collection: Police gather evidence, such as CCTV footage, witness statements, and forensic reports.",
            "3. Witness Interviews: Witnesses are interviewed to gather additional information.",
            "4. Case Presentation: The case is presented in court with all collected evidence."
        ]
    elif any(word in user_input for word in ["accused", "rights"]):
        response = [
            "Rights of the Accused:",
            "- Right to remain silent.",
            "- Right to legal representation.",
            "- Right to a fair trial.",
            "- Right to be informed of the charges against them."
        ]
    elif any(word in user_input for word in ["victim"]):
        response = [
            "Rights of the Victim:",
            "- Right to file a complaint.",
            "- Right to protection.",
            "- Right to compensation.",
            "- Right to be heard in court proceedings."
        ]

    # Retrieve specific section details from IPC
    elif "section" in user_input:
        section_number = None
        for word in user_input.split():
            if word.isdigit():
                section_number = int(word)
                break
        
        if section_number is not None:
            section_found = False
            for chapter in ipc_data['chapters']:
                for section in chapter['sections']:
                    if section['section'] == section_number:
                        section_found = True
                        if "punishment" in user_input:
                            response = [f"Punishment for Section {section_number}: {section['punishment']}"]
                        else:
                            response = [
                                f"Section {section_number}: {section['offense']}",
                                f"Punishment: {section['punishment']}"
                            ]
                        break
                if section_found:
                    break
            
            if not section_found:
                response = [f"Section {section_number} not found in the IPC. Please check the section number and try again."]
        else:
            response = ["IPC contains Section 511 and 23 chapters and instructs users to enter queries in the format: 'what is the section (section number)'"]

    # If no specific information is found, provide related information
    else:
        related_info = [
            "You can ask about the following topics:",
            "- FIR filing procedures",
            "- Emergency contact numbers",
            "- Police investigation procedures",
            "- Legal provisions and punishments",
            "- Rights of victims and accused"
        ]
        response = related_info

    return jsonify({'response': response})

# Route for chat page
@app.route('/chat')
def chat():
    return render_template('/chatbox.html')

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)