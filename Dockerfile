FROM python:3.11-slim

WORKDIR /app

COPY Pipfile* ./

RUN pip install pipenv && pipenv install --system --deploy || true

# 🔥 Install missing dashboard libraries
RUN pip install streamlit plotly pandas numpy matplotlib seaborn

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "dashboard_final.py", "--server.address=0.0.0.0", "--server.port=8501"]
