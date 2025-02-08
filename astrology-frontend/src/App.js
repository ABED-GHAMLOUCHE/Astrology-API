import React, { useState } from "react";
import axios from "axios";
import DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";
import TimePicker from "react-time-picker";
import "react-time-picker/dist/TimePicker.css";

// Google Places API Loader
const loadGoogleMapsScript = (callback) => {
  if (window.google) {
    callback();
    return;
  }
  const script = document.createElement("script");
  script.src = `https://maps.googleapis.com/maps/api/js?key=AIzaSyBudSMdB3eiI1x0spYtQHcXCv7uOikaBAw&libraries=places`;
  script.async = true;
  script.defer = true;
  script.onload = callback;
  document.head.appendChild(script);
};

const App = () => {
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [selectedTime, setSelectedTime] = useState("12:00");
  const [city, setCity] = useState("");
  const [tzOffset, setTzOffset] = useState(null);
  const [error, setError] = useState("");
  const [birthChart, setBirthChart] = useState(null);
  const API_URL = "https://astrology-api-au16.onrender.com";

  // Fetch Timezone Offset from Google Time Zone API
  const getTimeZoneOffset = async (latitude, longitude) => {
    const API_KEY = "AIzaSyBudSMdB3eiI1x0spYtQHcXCv7uOikaBAw"; // Replace with your actual key
    const timestamp = Math.floor(Date.now() / 1000); // Current time in seconds
    const url = `https://maps.googleapis.com/maps/api/timezone/json?location=${latitude},${longitude}&timestamp=${timestamp}&key=${API_KEY}`;

    try {
      const response = await axios.get(url);
      console.log("🛰️ Timezone API Response:", response.data);
  
      if (response.data.status === "OK") {
        const offsetHours = response.data.rawOffset / 3600; // Convert from seconds to hours
        return offsetHours;
      } else {
        console.error("❌ Error fetching timezone:", response.data.status, response.data.errorMessage);
        return null;
      }
    } catch (error) {
      console.error("❌ Timezone API Request Failed:", error);
      return null;
    }
  };

  // Initialize Google Places Autocomplete
  const initAutocomplete = () => {
    const input = document.getElementById("city-input");
    if (!input) return;
  
    const autocomplete = new window.google.maps.places.Autocomplete(input, {
      types: ["(cities)"],
    });
  
    autocomplete.addListener("place_changed", async () => {
      const place = autocomplete.getPlace();
      if (!place.geometry) return;
  
      const { lat, lng } = place.geometry.location;
      const latitude = lat();
      const longitude = lng();
  
      setCity(place.formatted_address);
  
      // 🔹 Get and Set Timezone Automatically
      const offset = await getTimezoneOffset(latitude, longitude);
      if (offset !== null) {
        setTzOffset(offset);
        console.log(`⏳ Auto-Detected Timezone Offset: ${offset} hours`);
      }
    });
  };
  

  // Load Google Maps API when component mounts
  React.useEffect(() => {
    loadGoogleMapsScript(initAutocomplete);
  }, []);

  // Fetch Birth Chart from API
  const fetchBirthChart = async () => {
    if (!city.trim()) {
      setError("Please select a valid city.");
      return;
    }

    if (tzOffset === null) {
      setError("Fetching timezone... Please wait.");
      return;
    }

    try {
      const date = selectedDate.toISOString().split("T")[0].split("-");
      const time = selectedTime.split(":");

      const response = await axios.get(`${API_URL}/birth_chart`, {
        params: {
          year: date[0],
          month: date[1],
          day: date[2],
          hour: time[0],
          minute: time[1],
          city,
        },
      });

      setBirthChart(response.data);
      setError("");
    } catch (err) {
      setError(err.response?.data?.error || "An error occurred while fetching the birth chart.");
    }
  };

  return (
    <div style={{ textAlign: "center", marginTop: "20px" }}>
      <h1>Astrology Birth Chart</h1>

      <div>
        <label>Select Date of Birth:</label>
        <DatePicker
          selected={selectedDate}
          onChange={(date) => setSelectedDate(date)}
          dateFormat="yyyy-MM-dd"
          maxDate={new Date()}
          showYearDropdown
          scrollableYearDropdown
        />
      </div>

      <div>
        <label>Select Time of Birth:</label>
        <TimePicker value={selectedTime} onChange={setSelectedTime} disableClock={true} />
      </div>

      <div>
        <label>Select City:</label>
        <input id="city-input" type="text" placeholder="Enter your birth city" />
      </div>

      {tzOffset !== null && <p>🌍 Time Zone Offset: {tzOffset >= 0 ? `+${tzOffset}` : tzOffset} hours</p>}

      <button onClick={fetchBirthChart} disabled={tzOffset === null}>
        Get Birth Chart
      </button>

      {error && <p style={{ color: "red" }}>{error}</p>}

      {birthChart && (
        <div>
          <h2>Birth Chart Data:</h2>
          <pre>{JSON.stringify(birthChart, null, 2)}</pre>
        </div>
      )}
    </div>
  );
};

export default App;