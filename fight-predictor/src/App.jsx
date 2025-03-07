import { useState, useEffect } from 'react';
import axios from "axios";
import './App.css';

function App() {
  const [fighters, setFighters] = useState([]);
  const [redFighter, setRedFighter] = useState("");
  const [blueFighter, setBlueFighter] = useState("");
  const [prediction, setPrediction] = useState("");

  useEffect(() => {
    const fetchFighters = async () => {
      try {
        const response = await axios.get("http://127.0.0.1:5000/fighters");
        const data = typeof response.data === "string" ? JSON.parse(response.data) : response.data;
        if (Array.isArray(data)) {
          setFighters(data);
        } else {
        }
      } catch (error) {
        console.error("Could Not Fetch Fighter Information:", error);
      }
    };

    fetchFighters();
  }, []);

  useEffect(() => {
    console.log("Fighters State:", fighters); 
  }, [fighters]);

  const handlePredict = () => {
    if (!redFighter || !blueFighter) {
      alert("Please Select a Fighter");
      return;
    }
    axios.post("http://127.0.0.1:5000/predict", { 
      red: redFighter, blue: blueFighter 
    })
    .then(response => setPrediction(response.data.winner))
    .catch(error => console.error("Could Not Make Prediction", error));
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-900 text-white p-4">
      <h1 className="text-3xl font-bold mb-6">Fantasy Fight Predictor 🥊</h1>

      <div className="flex space-x-6">
        <div>
          <label className="block text-lg">Red Fighter</label>
          <select 
            className="p-2 rounded bg-gray-800 text-white"
            value={redFighter}
            onChange={(e) => setRedFighter(e.target.value)}
          >
            <option value="">Select Fighter</option>
            {fighters.map(f => (
              <option key={f.id} value={f.name}>{f.name}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-lg">Blue Fighter</label>
          <select 
            className="p-2 rounded bg-gray-800 text-white"
            value={blueFighter}
            onChange={(e) => setBlueFighter(e.target.value)}
          >
            <option value="">Select Fighter</option>
            {fighters.map(f => (
              <option key={f.id} value={f.name}>{f.name}</option>
            ))}
          </select>
        </div>
      </div>

      <button 
        onClick={handlePredict}
        className="mt-6 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-700 transition"
      >
        Predict Fight
      </button>

      {prediction && (
        <div className="mt-6 text-xl font-semibold">
          {prediction}
        </div>
      )}
    </div>
  );
}

export default App;