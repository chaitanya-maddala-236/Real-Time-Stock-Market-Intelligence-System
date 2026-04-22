import React, { useEffect, useState } from "react";

const API_BASE = process.env.REACT_APP_API_BASE || "http://localhost:5000";

function App() {
  const [data, setData] = useState(null);
  const [error, setError] = useState("");

  const load = async () => {
    try {
      const response = await fetch(`${API_BASE}/latest`);
      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }
      const payload = await response.json();
      setData(payload);
      setError("");
    } catch (err) {
      setError(err.message);
    }
  };

  useEffect(() => {
    load();
    const id = setInterval(load, 15000);
    return () => clearInterval(id);
  }, []);

  return (
    <div style={{ fontFamily: "Arial, sans-serif", margin: "2rem" }}>
      <h1>Real-Time Stock Market Intelligence</h1>
      <p>API: {API_BASE}</p>
      {error && <p style={{ color: "red" }}>{error}</p>}
      {!data && !error && <p>Loading...</p>}

      {data && (
        <>
          <h2>Latest Prediction</h2>
          <ul>
            <li>Last Close: {data.predictions?.last_close}</li>
            <li>Regression Next Close: {data.predictions?.regression_next_close}</li>
            <li>LSTM Next Close: {data.predictions?.lstm_next_close}</li>
            <li>Chosen Model: {data.predictions?.chosen_model}</li>
          </ul>

          <h2>Signal</h2>
          <p style={{ fontWeight: "bold" }}>{data.signal?.signal || "N/A"}</p>

          <h2>Model Metrics</h2>
          <pre>{JSON.stringify(data.metrics, null, 2)}</pre>
        </>
      )}
    </div>
  );
}

export default App;
