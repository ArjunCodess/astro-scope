## 🧠 Product Requirements Document (PRD)

**AstroScope: NASA Asteroid Dashboard (NeoWs Edition)**

**Objective:**
Develop an interactive web application using Streamlit to visualize and analyze near-Earth asteroid data from NASA's NeoWs API. The application will provide insights into asteroid sizes, velocities, miss distances, and potential hazards, enabling users to assess planetary risk.

---

### 📁 File Structure

```
astro_scope/
│
├── app.py                    # Streamlit entry point
├── requirements.txt          # All dependencies
├── README.md                 # Project intro + usage
│
├── /data/                    # Data storage
│   ├── asteroids_raw.json
│   └── asteroids_clean.csv
│
├── /libs/                    # Core logic modules
│   ├── data_fetcher.py       # Handles API calls
│   ├── data_cleaner.py       # Normalizes + processes raw data
│   ├── feature_engineer.py   # Risk scoring, z-scores, stats
│   └── visualizer.py         # Generates matplotlib plots
│
├── /assets/                  # Logo, images, icons
│   └── logo.png
```

---

### 📦 Dependencies

* `streamlit` – for building the interactive web application.
* `requests` – for making HTTP requests to the NeoWs API.
* `pandas` – for data manipulation and analysis.
* `matplotlib` – for data visualization.
* `plotly` – for interactive charts.
* `python-dotenv` – for loading environment variables.
* `messagebird` – for sending SMS notifications.

---

### 🔑 API Integration

**Endpoint:**
`https://api.nasa.gov/neo/rest/v1/feed`

**Parameters:**

* `start_date`: Start date for the data range (e.g., `2025-08-01`).
* `end_date`: End date for the data range (e.g., `2025-08-04`).
* `api_key`: Your NASA API key.

**Response:**

* `near_earth_objects`: Dictionary containing asteroid data keyed by date.

  * Each asteroid entry includes:

    * `name`: Name of the asteroid.
    * `id`: NASA JPL Small Body ID.
    * `close_approach_data`: List of approach data.

      * `close_approach_date`: Date of closest approach.
      * `miss_distance`: Distance from Earth in kilometers.
      * `relative_velocity`: Velocity relative to Earth in kilometers per hour.
      * `estimated_diameter`: Estimated diameter in kilometers.
      * `is_potentially_hazardous_asteroid`: Boolean indicating if the asteroid is potentially hazardous.

---

### 📊 Data Processing & Analysis

1. **Data Fetching:**

   * Use the `requests` library to fetch data from the NeoWs API.
   * Store the JSON response in a variable for further processing.

2. **Data Normalization:**

   * Flatten the JSON response to create a structured dataset.
   * Convert the dataset into a pandas DataFrame for easier manipulation.

3. **Data Cleaning:**

   * Handle missing or null values appropriately.
   * Convert data types to ensure consistency (e.g., `miss_distance` to float).

4. **Feature Engineering:**

   * Calculate additional metrics such as:

     * `miss_distance_km`: Distance from Earth in kilometers.
     * `relative_velocity_km_s`: Velocity in kilometers per second.
     * `diameter_mean_km`: Average estimated diameter in kilometers.
     * `diameter_max_km`: Maximum estimated diameter in kilometers.
     * `diameter_min_km`: Minimum estimated diameter in kilometers.
     * `hazardous`: Boolean indicating if the asteroid is potentially hazardous.

5. **Risk Scoring:**

   * Implement a risk scoring algorithm based on:

     * Velocity (`relative_velocity_km_s`).
     * Size (`diameter_mean_km`).
     * Miss distance (`miss_distance_km`).
   * Normalize the risk scores to identify high-risk asteroids.

---

### 📈 Data Visualization

1. **Time-Series Analysis:**

   * Plot the number of asteroids approaching Earth over time.
   * Visualize trends in asteroid sizes and velocities.

2. **Risk Distribution:**

   * Create histograms to show the distribution of:

     * Asteroid sizes.
     * Velocities.
     * Miss distances.
     * Risk scores.

3. **Scatter Plots:**

   * Plot `miss_distance_km` vs. `relative_velocity_km_s` to identify patterns.
   * Use color coding to indicate risk levels.

4. **Top 10 Risky Asteroids:**

   * Display a table of the top 10 asteroids with the highest risk scores.
   * Include details such as name, size, velocity, and miss distance.

---

### 🖥️ Streamlit Application

**File:** `app.py`

1. **App Layout:**

   * Use `st.title()` to display the application title.
   * Use `st.sidebar` for user inputs such as date range selection.
   * Display visualizations using `st.pyplot()` for Matplotlib charts.
   * Use `st.dataframe()` to display data tables.

2. **User Inputs:**

   * Implement date range selectors using `st.date_input()`.
   * Allow users to filter data based on asteroid size, velocity, and risk score.

3. **Dynamic Updates:**

   * Use Streamlit's reactivity to update visualizations based on user inputs.
   * Ensure that data fetching and processing are efficient to provide a smooth user experience.

---

### 🧪 Testing & Validation

1. **Unit Tests:**

   * Write tests for data fetching functions to ensure they handle API responses correctly.
   * Test data processing functions for accuracy and robustness.

2. **Integration Tests:**

   * Test the integration between the API, data processing, and visualization components.
   * Ensure that the Streamlit app updates correctly based on user inputs.

3. **Performance Testing:**

   * Monitor the performance of the application, especially during data fetching and processing.
   * Optimize code to handle large datasets efficiently.

---

### 📦 Deployment

1. **Local Deployment:**

   * Run the application locally using `streamlit run app.py` for development and testing.

2. **Cloud Deployment:**

   * Deploy the application to a cloud platform such as Heroku, AWS, or Streamlit Sharing for public access.

3. **Version Control:**

   * Use Git for version control and GitHub for repository hosting.
   * Maintain a clear commit history and use branches for feature development.

---

### 📄 Documentation (README.md)

* Provide an overview of the project, its objectives, and how to run the application.
* Include instructions for setting up the environment and installing dependencies.

---

### **Phase 1: API Integration & Data Acquisition**

**Goal:**
Hook into NASA’s NeoWs API, pull raw asteroid data, and save it for processing.

**What you do:**

* Get your NASA API key.
* Understand the NeoWs feed API parameters and limits.
* Build a function to fetch data in 7-day chunks (due to API constraints).
* Collect data for the last 90 days (or user-selected range).
* Save raw JSON or CSV for backup.

**Output:**

* `data_fetcher.py` (or module) with reusable API call functions.
* Raw dataset saved as `/data/asteroids_data_raw.json` or CSV.

---

### **Phase 2: Data Cleaning & Structuring**

**Goal:**
Turn messy API JSON into a clean, structured, usable pandas DataFrame.

**What you do:**

* Flatten JSON using `pd.json_normalize`.
* Extract relevant columns: name, date, miss distance, velocity, diameter, hazard flag.
* Convert types properly (`float`, `datetime`, `bool`).
* Handle missing or malformed data (drop or impute).
* Set datetime as index.
* Store cleaned data as CSV for easy reload.

**Output:**

* `data_processing.py` module for cleaning pipeline.
* Cleaned data saved as `/data/asteroids_data_clean.csv`.

---

### **Phase 3: Analysis & Feature Engineering**

**Goal:**
Crunch numbers with Pandas to generate meaningful metrics and risk scores.

**What you do:**

* Calculate average diameter, velocity in km/s, and miss distance in km.
* Create normalized risk scores combining velocity, size, and miss distance.
* Compute z-scores for risk to flag anomalies.
* Generate rolling averages or moving windows for time-series smoothing.
* Summarize key statistics (max, min, mean, counts).
* Prepare data subsets for different visualizations.

**Output:**

* `analysis.py` module with risk scoring and aggregation functions.
* DataFrames ready for visualization.

---

### **Phase 4: Visualization & Dashboard UI**

**Goal:**
Design and build an interactive Streamlit dashboard that tells the asteroid risk story visually and clearly.

**What you do:**

* Create UI skeleton in `app.py` with title, sidebar filters (date range, risk threshold).
* Integrate matplotlib plots:

  * Time series of asteroid counts & average risk.
  * Histograms for size, velocity, miss distance.
  * Scatter plot of miss distance vs velocity with risk coloring.
  * Table of top 10 risky asteroids.
* Add dynamic filtering and reactive updates based on user input.
* Optimize plot layout for clarity and impact.
* Add tooltips, legends, and axis labels.

**Output:**

* Fully working Streamlit app `app.py`.
* Intuitive UI with all charts and tables.

---

### **Phase 5: Testing, Optimization & Deployment**

**Goal:**
Ensure the app works reliably, loads fast, and is shareable with the world.

**What you do:**

* Test data fetching and processing edge cases (API errors, empty data).
* Validate risk score calculations against known examples.
* Profile app performance; optimize slow parts (e.g., caching API calls).
* Document installation, usage, and deployment steps in README.md.
* Deploy to Streamlit Cloud or another cloud service.
* Add version control with Git, push code to GitHub repo.

**Output:**

* Stable, polished app with docs.
* Publicly accessible deployed dashboard.
* Source code repo with clean commits and branches.

---

### 📌 Notes

* Ensure that the application is responsive and user-friendly.
* Prioritize data accuracy and clarity in visualizations.
* Consider adding features such as email notifications for high-risk asteroids.
* Explore additional data sources for enriched analysis.