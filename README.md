# Flask Project – Web Application with Authentication
This project was originally developed as part of a Flask course at Alura, where the initial goal was to build a REST API. After completing the course requirements, I extended the project by transforming the API into a full web application using HTML and CSS, integrating frontend templates with the Flask backend.

# Overview
This application implements a CRUD system with authentication using JWT (JSON Web Token) and MongoDB as the database.
The project evolved from a backend-only REST API into a server-rendered web application with user interface integration.

# Technologies
- Python
- HTML/CSS
- Flask (Microframework)
- MongoDB
- JWT (JSON Web Tokens)
- 
# Project Evolution
🔹 *Original Version (course)*
- API REST
- CRUD Endpoints
- Backend structure with Flask
- Testing with Postman and Thunderclient

🔹 *Improvements implemented (By me)*
- Criação de interface em HTML
- Estilização com CSS
- Integração das rotas com templates
- Adaptação da lógica da API para renderização de páginas
- Melhor organização da estrutura do projeto

# What i learned
- Building RESTful APIs with Flask
- Connecting Flask to MongoDB
- Implementing authentication with JWT
- Transition and diference knowledge between API REST and server-rendered web application
- Using templates with Flask
- Backend + frontend integration
- Organizing routes for rendering, not just JSON

# How to run locally
// Clone the repository:  
git clone https://github.com/Thiago-Nagata/flask-project.git

// Enter the project folder:  
cd flask-project

// Create virtual environment:  
python -m venv venv

// Activate environment:  
- Windows:
venv\Scripts\activate
- macOS/Linux:
source venv/bin/activate

// Install dependencies:  
pip install -r requirements.txt

// Run the application:  
python app.py

# Environment Variables Required
Create a **.env** file on the root directory file and define the required environment variables:

- SECRET_KEY=your_secret_key
- MONGO_URI=your_mongodb_connection_string
  
These variables are required for the application to run properly.
You may use a local MongoDB instance or a cloud service like MongoDB Atlas.
