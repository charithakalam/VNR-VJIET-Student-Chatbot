# Student Chatbot – College Information Assistant

A web-based Student Chatbot built using Flask, designed based on **VNR VJIET** college data to provide information on transport routes, academic calendars, HOD details, facilities, and campus contacts.  
It can answer queries like **bus routes**, **driver contacts**, **academic calendar (sessionals & end exams)**, **HOD details**, **college address**, and **campus facilities**.

## Features
- Interactive chatbot interface
- Bus routes and transport fare details
- Driver names and contact information
- Academic calendar (sessionals & end exams by semester/year)
- HOD details for different departments
- College contact details and facilities
- Clean, responsive UI built with HTML & CSS

## Tech Stack
- **Backend:** Python, Flask  
- **Frontend:** HTML, CSS, JavaScript  
- **Data Storage:** JSON  
- **Tools:** Git, GitHub  

## 📁 Project Structure
student-chatbot/
│
├── app.py                  # Flask application
├── chatbot.py              # Chatbot logic and query handling
├── requirements.txt        # Project dependencies
├── run.sh                  # Script to run the app locally
├── README.md
│
├── data/
│   └── college_details.json
│
├── static/
│   └── style.css
│
├── templates/
│   └── index.html
