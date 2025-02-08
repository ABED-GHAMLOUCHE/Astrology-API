import logo from './logo.svg';
import './App.css';
import React, { useState } from "react";
import axios from "axios";

function App() {
  const [birthChart, setBirthChart] = useState(null);
  const [year, setYear] = useState("1990");
  const [month, setMonth] = useState("3");
  const [day, setDay] = useState("15");
  const [hour, setHour] = useState("12");
  const [minute, setMinute] = useState("0");
  const [city, setCity] = useState("New York");
  const [tzOffset, setTzOffset] = useState("-5");

  const fetchBirthChart = async () => {
    const url = `https://astrology-api.onrender.com/birth_chart?year=${year}&month=${month}&day=${day}&hour=${hour}&minute=${minute}&city=${encodeURIComponent(city)}&tz_offset=${tzOffset}`;

    console.log("🔍 API Request URL:", url); // Debugging

    try {
        const response = await axios.get(url);
        console.log("✅ API Response:", response.data); // Debugging
        setBirthChart(response.data);
    } catch (error) {
        console.error("❌ Error fetching birth chart:", error);
        alert("Failed to fetch birth chart. Check the console for errors.");
    }
};


  return (
    <div style={{ padding: "20px" }}>
      <h1>Astrology Birth Chart</h1>

      <label>Year:</label>
      <input type="number" value={year} onChange={(e) => setYear(e.target.value)} />

      <label>Month:</label>
      <input type="number" value={month} onChange={(e) => setMonth(e.target.value)} />

      <label>Day:</label>
      <input type="number" value={day} onChange={(e) => setDay(e.target.value)} />

      <label>Hour:</label>
      <input type="number" value={hour} onChange={(e) => setHour(e.target.value)} />

      <label>Minute:</label>
      <input type="number" value={minute} onChange={(e) => setMinute(e.target.value)} />

      <label>City:</label>
      <input type="text" value={city} onChange={(e) => setCity(e.target.value)} />

      <label>Timezone Offset:</label>
      <input type="number" value={tzOffset} onChange={(e) => setTzOffset(e.target.value)} />

      <button onClick={fetchBirthChart}>Get Birth Chart</button>

      {birthChart && (
        <div>
          <h2>Birth Chart Data:</h2>
          <pre>{JSON.stringify(birthChart, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}

export default App;
