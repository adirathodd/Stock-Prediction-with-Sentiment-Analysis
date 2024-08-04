import React, { useState, useEffect } from "react";
import { ProgressBar } from "react-bootstrap";
import "bootstrap/dist/css/bootstrap.min.css";
import "./App.css";

function App() {
  const [ticker, setTicker] = useState("");
  const [data, setData] = useState(null);
  const [prediction, setPrediction] = useState(null);
  const [progress, setProgress] = useState(0);
  const [message, setMessage] = useState("");

  useEffect(() => {
    const socket = new WebSocket("ws://localhost:8000/ws");

    socket.onmessage = (event) => {
      const response = JSON.parse(event.data);
      if (response.progress !== undefined) {
        setProgress(response.progress);
        setMessage(response.message);
      } else {
        const formattedData = response.data.map(row => ({
          ...row,
          Date: new Date(row.Date).toISOString().split('T')[0],
          Close: row.Close.toFixed(2),
          Volume: row.Volume.toLocaleString(),
          'Moving Average': (typeof row['Moving Average'] === 'number' ? row['Moving Average'].toFixed(2) : 'N/A'), // Format Moving Average
          RSI: row.RSI.toFixed(2)
        }));
        setData(formattedData);
        setPrediction(parseFloat(response.prediction).toFixed(2));
      }
    };

    return () => {
      socket.close();
    };
  }, []);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setProgress(0);
    setMessage("");

    const socket = new WebSocket("ws://localhost:8000/ws");
    socket.onopen = () => {
      const requestData = { ticker: ticker };
      try {
        socket.send(JSON.stringify(requestData));
      } catch (error) {
        console.error("Error serializing requestData:", error);
      }
    };

    socket.onmessage = (event) => {
      const response = JSON.parse(event.data);
      if (response.progress !== undefined) {
        setProgress(response.progress);
        setMessage(response.message);
      } else {
        const formattedData = response.data.map(row => ({
          ...row,
          Date: new Date(row.Date).toISOString().split('T')[0],
          Close: row.Close.toFixed(2),
          Volume: row.Volume.toLocaleString(),
          'Moving Average': (typeof row['Moving Average'] === 'number' ? row['Moving Average'].toFixed(2) : 'N/A'), // Format Moving Average
          RSI: row.RSI.toFixed(2)
        }));
        setData(formattedData);
        setPrediction(parseFloat(response.prediction).toFixed(2));
      }
    };

    socket.onerror = (error) => {
      console.error("WebSocket error:", error);
    };

    socket.onclose = () => {
      console.log("WebSocket connection closed");
    };
  };

  return (
    <div className="App">
      <h1>Stock Prediction</h1>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={ticker}
          onChange={(e) => setTicker(e.target.value)}
          placeholder="Enter stock ticker"
        />
        <button type="submit">Predict</button>
      </form>
      {message && <p>{message}</p>}
      <div className="progress-container">
        <ProgressBar now={progress} label={`${progress}%`} animated={progress < 100} />
      </div>
      {data && (
        <div>
          <h2>Data</h2>
          <table>
            <thead>
              <tr>
                {data.length > 0 && Object.keys(data[0]).map((key) => (
                  <th key={key}>{key}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {data.map((row, index) => (
                <tr key={index}>
                  {Object.values(row).map((value, i) => (
                    <td key={i}>{value}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      {prediction && (
        <div>
          <h2>Predicted next day's price: {prediction}</h2>
        </div>
      )}
    </div>
  );
}

export default App;
