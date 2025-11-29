# 🛒 LocalLens: Hyper-Local Inventory Intelligence Engine

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-red)
![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-336791)
![Prophet](https://img.shields.io/badge/ML-Facebook%20Prophet-orange)
![spaCy](https://img.shields.io/badge/NLP-spaCy-green)

**LocalLens** is an end-to-end data science application designed to bridge the gap between local grocers and modern consumers. It serves as a dual-sided platform: a **Smart Recipe Finder** for consumers and a **AI-Powered Operating System** for shopkeepers.

---

## 📸 Screenshots

*(Add screenshots here later! Drag and drop your images of the Dashboard, Deep Dive, and POS pages here)*

| **Triage Dashboard** | **Deep Dive Analytics** |
|:---:|:---:|
| ![Dashboard Preview](link_to_dashboard_image) | ![Deep Dive Preview](link_to_deep_dive_image) |

---

## 🚀 Key Features

### 🏢 For The Business (The Shopkeeper OS)
* **🧠 Automated Demand Triage:** Runs 150+ time-series models (Prophet) daily to identify items at risk of stockouts.
* **📈 Deep Dive Analytics:** Visualizes daily sales forecasts, identifying trends vs. seasonality.
* **💰 Digital Point-of-Sale (POS):** A functional cash register interface that records real-time sales and updates inventory instantly.
* **📦 Smart Inventory Management:** Purchase Order (PO) generator that calculates safety stock and suggests reorder quantities automatically.

### 🛒 For The Consumer
* **🍳 NLP Recipe Parser:** Paste any URL from *Food.com* or *Allrecipes*. A custom-trained **spaCy NER model** extracts ingredients (ignoring quantities/prep instructions) and finds them in local stock.
* **🔍 Fuzzy Search Engine:** Uses SQL fuzzy matching to link complex recipe ingredients (e.g., "finely chopped organic spinach") to store inventory ("Frozen Spinach").

---

## 🛠️ The Tech Stack

* **Database:** PostgreSQL (Relational Data Warehousing)
* **Backend & App Logic:** Python, Pandas, NumPy
* **Machine Learning (Forecasting):**
    * **Library:** Facebook Prophet
    * **Features:** Seasonality, Indian Holidays, External Regressors (Google Trends data), Promotional events ("On Sale" flags).
* **Natural Language Processing (NLP):**
    * **Library:** spaCy (Custom trained NER model)
    * **Task:** Named Entity Recognition for ingredient extraction.
* **Frontend:** Streamlit (Multi-page application framework)
* **Visualization:** Plotly & Altair (Interactive charts)

---

## ⚙️ How to Run Locally

### Prerequisites
* Python 3.10+
* PostgreSQL installed and running locally.

### Installation

1.  **Clone the Repository**
    ```bash
    git clone [https://github.com/sdiv0503/Local-Lens.git](https://github.com/sdiv0503/Local-Lens.git)
    cd Local-Lens
    ```

2.  **Set up Virtual Environment**
    ```bash
    python -m venv venv
    # Windows:
    .\venv\Scripts\activate
    # Mac/Linux:
    source venv/bin/activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Database Setup**
    * Create a PostgreSQL database named `local_lens_db`.
    * Update `db.py` with your database password.
    * Run the setup scripts to seed the DB with synthetic data:
    ```bash
    # 1. Create Tables
    # (Manually run content of schema.sql in your SQL tool)
    
    # 2. Populate Stores & Products
    python populate_db.py
    
    # 3. Generate Fake Trends & Simulation Data
    python create_fake_trends.py
    python simulate_sales.py
    
    # 4. Train the ML Models
    python train_all_models.py
    ```

5.  **Run the App**
    ```bash
    streamlit run app.py
    ```

---

## 📊 Data Science Methodology

### 1. Synthetic Data Generation
Since real-world retail data is private, I built a robust **Data Simulator** (`simulate_sales.py`) that generates 5 years of daily sales history.
* **Logic:** `Sales = Base_Demand + Seasonality (Sine Wave) + Trend_Influence + Promotions + Noise`.
* This ensures the ML models have realistic patterns (like Mango spikes in summer) to learn from.

### 2. Custom NLP Training
Standard NLP models fail on recipe text (e.g., confusing "can" the noun vs "can" the verb).
* **Solution:** Manually labeled 100+ recipe strings.
* **Outcome:** A custom spaCy model that achieves high accuracy in extracting the core *buyable* ingredient from complex text.

### 3. Forecasting at Scale
Instead of one model, the system trains **150+ individual models** (one per product).
* **Optimization:** Models are trained in batch (`train_all_models.py`) and serialized to JSON.
* **Inference:** The dashboard loads these lightweight JSONs for instant, on-demand forecasting.

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.

---

**Built with ❤️ by Divyansh Sharma**