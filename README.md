# Real-Time Stock Market Intelligence System (Big Data + LSTM)

## 🧠 Overview

This project is a **Real-Time Stock Market Intelligence System** that uses Big Data technologies and Machine Learning to analyze and predict stock prices.

## 🎯 Objective

Build an end-to-end system that:
- Collects stock market data (real-time + historical)
- Processes it using big data tools
- Predicts future prices using LSTM/regression
- Generates buy/sell signals
- Visualizes insights in a dashboard

## 👥 Target Users

- Retail investors
- Data science learners
- Financial analysts

## ⚡ Features

- Real-time stock data streaming
- LSTM-based price prediction
- Regression baseline for comparison
- Buy/Sell signal generation
- Interactive dashboard

## 🏗️ System Architecture

`Data Source → Kafka → Storage (S3/HDFS/Local) → Spark → ML Model → MongoDB → Dashboard`

## ⚙️ Tech Stack

| Layer | Technology |
|---|---|
| Data Source | yfinance API |
| Streaming | Apache Kafka |
| Storage | S3 / Local |
| Processing | Apache Spark |
| ML | TensorFlow / Keras, scikit-learn |
| Database | MongoDB |
| Backend API | Flask |
| Frontend | React / Power BI |

## 📊 Success Metrics

- Model accuracy (RMSE)
- Real-time data latency
- Dashboard responsiveness

## 🏗️ Project Structure

```text
Real-Time-Stock-Market-Intelligence-System/
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── output/
├── model/
│   ├── artifacts/
│   └── lstm_model.py
├── kafka/
│   ├── producer.py
│   └── consumer.py
├── spark/
│   └── process_data.py
├── api/
│   └── app.py
├── dashboard/
│   ├── public/
│   └── src/
├── requirements.txt
└── README.md
```

## ⚙️ Installation

### 1. Clone Repo

```bash
git clone https://github.com/chaitanya-maddala-236/Real-Time-Stock-Market-Intelligence-System.git
cd Real-Time-Stock-Market-Intelligence-System
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Start Kafka

```bash
# start zookeeper
bin/zookeeper-server-start.sh config/zookeeper.properties

# start kafka
bin/kafka-server-start.sh config/server.properties
```

### 4. Run Data Producer

```bash
python kafka/producer.py --ticker AAPL --max-messages 60
```

### 5. Run Consumer + Processing

```bash
python kafka/consumer.py --max-messages 60
python spark/process_data.py
```

### 6. Train Model

```bash
python model/lstm_model.py
```

### 7. Start API

```bash
python api/app.py
```

Available API endpoints:

- `GET /health`
- `GET /predictions`
- `GET /signals`
- `GET /metrics`
- `GET /latest`

### 8. Run Dashboard

```bash
cd dashboard
npm install
npm start
```

Optional API URL override:

```bash
REACT_APP_API_BASE=http://localhost:5000 npm start
```

## 📈 Output

- Predicted stock prices
- Buy/Sell signals
- Visual charts

## 🔮 Future Improvements

- Add news sentiment analysis
- Improve model with transformers
- Deploy on cloud

## 🔥 Pro Tips

- Keep README clean — recruiters read this first
- Add screenshots of dashboard
- Add a demo video
- Explain the pipeline clearly
