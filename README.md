# Insurance Guidelines Engine Impact Analysis

## Setup & Run the Application

1. **Build the Docker image**:
   ```sh
   docker build --no-cache -t simulation .
   ```
2. **Run the container**:
   ```sh
   docker run -p 8000:8000 simulation
   ```
3. **Run migrations** (inside the container's Exec command prompt):
   ```sh
   python manage.py migrate
   ```

## API Endpoints

### 1. Get Guidelines
   - **Guidelines:** `http://localhost:8000/api/guidelines`

### 2. Get Submissions
   - **Submissions:** `http://localhost:8000/api/submissions`

### 3. Simulation API
   - Endpoint: `http://localhost:8000/api/simulation`
   - If `id` is provided but not found, that counts as invalid data.
   - If `id` is omitted, the guideline is treated as new.
   - **Payload Example:**
     ```json
     {
       "id": "b37b172a-3d9e-4492-89ae-23723c95975d",
       "name": "Russo, Ferrell and Morales Underwriting Policy",
       "conditions": {
         "logic": "any",
         "conditions": [
           { "field": "risk_profile.risk_factors", "operator": "contains_at_least", "value": { "items": ["cyber_threats"], "threshold": 3 } },
           { "field": "financials.revenue", "operator": "<=", "value": 1000 },
           { "field": "company_data.industry", "operator": "equals", "value": "construction" }
         ]
       },
       "action": "REVIEW",
       "priority": 9,
       "effective_date": "2020-07-14",
       "version": 1,
       "coverage_types": ["cyber"]
     }
     ```
   - **Response Example:**
     ```json
     {
          "total_submissions": 1000,
          "outcome_changes": 106,
          "outcome_change_percentage": 10.6,
          "breakdown_by_industry": {
              "construction": 106
          },
          "breakdown_by_risk_factor": {
              "regulatory_changes": 30,
              "environmental": 31,
              "economic_downturn": 30,
              "supply_chain": 31,
              "workplace_safety": 33,
              "reputation_risk": 29,
              "cyber_threats": 24,
              "pandemic": 32,
              "natural_disasters": 29
          },
          "breakdown_by_company_size": {
              "large": 45,
              "small": 43,
              "medium": 18
          },
          "breakdown_by_location": {
              "MI": 8,
              "PA": 14,
              "GA": 9,
              "IL": 12,
              "NY": 11,
              "OH": 9,
              "FL": 9,
              "CA": 12,
              "NC": 10,
              "TX": 12
          },
          "time_impact": {
              "immediate": 23,
              "gradual": 83
          },
          "financial_impact": 3029600000.0,
          "near_miss_submissions": []
      }
     ```

### 4. Graph API
   - Endpoint: `http://localhost:8000/api/graphs`
   - In order to graph results from Simulation API, you will paste your results into this API's payload.
   - Includes base64-encoded chart images and textual summaries.
   - Convert images back using: [Base64 Guru](https://base64.guru/converter/decode/image)
   - **Payload Example:**
     ```json
     {
          "total_submissions": 1000,
          "outcome_changes": 106,
          "outcome_change_percentage": 10.6,
          "breakdown_by_industry": {
              "construction": 106
          },
          "breakdown_by_risk_factor": {
              "regulatory_changes": 30,
              "environmental": 31,
              "economic_downturn": 30,
              "supply_chain": 31,
              "workplace_safety": 33,
              "reputation_risk": 29,
              "cyber_threats": 24,
              "pandemic": 32,
              "natural_disasters": 29
          },
          "breakdown_by_company_size": {
              "large": 45,
              "small": 43,
              "medium": 18
          },
          "breakdown_by_location": {
              "MI": 8,
              "PA": 14,
              "GA": 9,
              "IL": 12,
              "NY": 11,
              "OH": 9,
              "FL": 9,
              "CA": 12,
              "NC": 10,
              "TX": 12
          },
          "time_impact": {
              "immediate": 23,
              "gradual": 83
          },
          "financial_impact": 3029600000.0,
          "near_miss_submissions": []
      }
     ```
   - **Response Example:**
     - Response Example:
     ```json
     {
       "charts": {
         "industry_chart": "data:image/png;base64,+tp77x07uurqrmIv69rWXhcbtrWtvffuuhbsX…",
         "risk_factor_chart": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAlgAAAGQCAYAAA…",
         "company_size_chart": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAlgAAAGQCAYAAAB…",
         "location_chart": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAlgAAAGQCAYAAABy…",
         "time_impact_chart": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAlgAAAGQCAYAAAByN…"
       },
       "summaries": {
         "industry_summary": "Out of 1000 submissions, 237 (23.7%) showed changes. The industry most impacted is transportation.",
         "risk_factor_summary": "The dominant risk factor is workplace_safety, which plays a key role in the outcome differences.",
         "company_size_summary": "Small companies are most affected, with 117 impacted submissions.",
         "location_summary": "Geographically, IL exhibits the highest impact.",
         "time_impact_summary": "Immediate changes affected 44 submissions, while gradual changes impacted 193, suggesting that future renewals may follow these patterns.",
         "financial_summary": "The projected financial impact is approximately $5,087,600,000.00, indicating significant economic implications."
       }
     }
     ```

## Running Tests
To run tests, use:
```sh
python manage.py test simulation.tests
```

---

This README provides essential instructions for setup, usage, and testing of the application.

