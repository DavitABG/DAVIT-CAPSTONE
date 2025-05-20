#  Davit Capstone

An API with FASTAPI

# E-Commerce RFM Analysis and Sales Prediction
## Project Overview
This project implements RFM (Recency, Frequency, Monetary) analysis and predictive modeling for e-commerce sales data. It includes customer segmentation, sales forecasting, and interactive visualizations through a Streamlit dashboard.


## Features
- RFM Analysis for customer segmentation
- Time series forecasting for sales prediction
- Interactive dashboard with Streamlit
- Customer lifetime value (CLV) calculation
- Data visualization and insights

## Analysis Components
- Customer Segmentation using RFM Analysis
- Sales Trend Analysis
- Predictive Analytics
- Customer Behavior Insights
- Interactive Visualizations

## Technologies Used
- Python
- Pandas
- Scikit-learn
- Streamlit
- Prophet
- Plotly
- Poetry



## Setup
Install main dependencies

```shell
poetry install
```

Create `.env` file in `src` and write the `SQLite` database path in it as follows:
```
DB_URL={URL}
```

## Running API

### For running project with uvicorn

```shell
uvicorn src.app.main:app --host 0.0.0.0 --port 8000 
```

### For assigning db_url (example)

```shell
export DB_URL=/Users/nareabgaryan/Desktop/Captone_PyCharm/src/data/client_database.db
```

### For running the dashboard

```shell
streamlit run src/dashboard_streamlit.py
```
### Debug mode with reloading

```shell
uvicorn src.app.main:app --host 0.0.0.0 --port 8000 --reload
```



## Testing

Install testing dependencies

```bash
poetry install --with dev
```

For automatic test detection (-v for verbose -s for printing inside functions)

```shell
pytest -v -s 
```

## Author
Davit Abgaryan
## License
This project is licensed under the MIT License - see the LICENSE file for details.
