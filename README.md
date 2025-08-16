# 🍲 Local Food Wastage Management System

[![Hugging Face Spaces](https://img.shields.io/badge/🤗-Hugging%20Face%20Spaces-blue.svg)](https://huggingface.co/spaces/thegyanvirs/Food_Wastage_Management_System_GS)

A **Data Science + Streamlit project** built to address the issue of food wastage by connecting **food providers** (restaurants, individuals, NGOs) with **receivers** (orphanages, shelters, communities).  

This project includes:
- Data cleaning & exploratory data analysis (EDA)
- SQL database creation from raw CSV files
- 16 SQL queries for reporting & insights
- A fully functional **Streamlit web app** deployed on Hugging Face

---

## 🚀 Live Demo
👉 Try the app here: **[Food Wastage Management System on Hugging Face](https://huggingface.co/spaces/thegyanvirs/Food_Wastage_Management_System_GS)**  
No installation needed — open the link and start using it!

---

## 📂 Repository Structure
```
.
├── data/ # SQLite database & schema files
├── claims_data.csv # Raw dataset: claims
├── food_listings_data.csv # Raw dataset: food listings
├── providers_data.csv # Raw dataset: providers
├── receivers_data.csv # Raw dataset: receivers
├── requirements.txt # Python dependencies
├── streamlit_app.py # Main Streamlit app
└── submission_main_notebook.ipynb # Jupyter notebook with data cleaning, EDA, SQL queries
```

---

## 🛠️ Features of the Streamlit App

### 1. 🔎 Browse & Filter
- Filter food listings by **location**, **provider**, and **food type**
- View real-time availability with expiry information

### 2. 📞 Contact Directory
- Search and filter **providers** and **receivers**
- Directly call or email them from within the app

### 3. 📝 CRUD Operations
- Add, update, and delete records for:
  - Providers  
  - Receivers  
  - Food listings  
  - Claims  

### 4. 📊 Reports (SQL Queries)
- Explore **16 predefined SQL reports**, including:
  - Providers & receivers per city  
  - Top provider types & food types  
  - Total available food & donation trends  
  - Claim status breakdown & efficiency metrics  
  - Distribution efficiency per provider  

Each report is interactive, filterable (where applicable), and downloadable as CSV.

---

## 🧑‍💻 How to Run Locally

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/<your-username>/Food-Wastage-Management-System.git
cd Food-Wastage-Management-System
```
### 2️⃣ Create Environment & Install Dependencies
```bash
pip install -r requirements.txt
```
### 3️⃣ Run the Streamlit App
```bash
streamlit run streamlit_app.py
```
### 4️⃣ Open in Browser
```bash
Streamlit will provide a local URL (default: http://localhost:8501).
```
## 📊 SQL & Data
- Four CSVs (providers_data.csv, receivers_data.csv, food_listings_data.csv, claims_data.csv) were used to build the SQLite database (data/food_waste.db).
- SQL queries (Q1–Q16) are implemented both in the Jupyter notebook and Streamlit app.

## 📈 Documentation & Deliverables
- ✅ Data Cleaning & EDA: submission_main_notebook.ipynb
- ✅ SQL Queries (Q1–Q16): Implemented in notebook & app
- ✅ Final Web Application: streamlit_app.py
- ✅ Deployment: Hugging Face Spaces
- ✅ GitHub Repository (this repo)

## 🌐 Deployment

The project is live on Hugging Face Spaces:
👉 [Food Wastage Management System](https://huggingface.co/spaces/thegyanvirs/Food_Wastage_Management_System_GS)
Deployed using the Streamlit SDK with requirements.txt.

## 🏆 Learning Outcomes

- Hands-on experience with data cleaning, SQL, and EDA
- Building an end-to-end ML/data app with Streamlit
- Deployment on Hugging Face Spaces
- Understanding of CRUD operations and SQL-based reporting in real-world systems

## 📜 License

This project is open-source under the MIT License.

# 👨‍💻 Developed by Gyanvir Singh.
