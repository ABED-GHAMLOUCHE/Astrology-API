import React, { useState } from "react";
import axios from "axios";
import DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";
import TimePicker from "react-time-picker";
import "react-time-picker/dist/TimePicker.css";

// Google Places API
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
  const [tzOffset, setTzOffset] = useState("");
  const [error, setError] = useState("");
  const [birthChart, setBirthChart] = useState(null);
  const API_URL = "https://astrology-api-au16.onrender.com";

  // Initialize Google Places Autocomplete
  const initAutocomplete = () => {
    const input = document.getElementById("city-input");
    if (!input) return;

    const autocomplete = new window.google.maps.places.Autocomplete(input, {
      types: ["(cities)"],
    });

    autocomplete.addListener("place_changed", () => {
      const place = autocomplete.getPlace();
      setCity(place.formatted_address);
    });
  };

  // Load Google Places API when component mounts
  React.useEffect(() => {
    loadGoogleMapsScript(initAutocomplete);
  }, []);

  const fetchBirthChart = async () => {
    if (!city.trim()) {
      setError("Please select a valid city.");
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
          tz_offset: tzOffset,
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
        <TimePicker
          value={selectedTime}
          onChange={setSelectedTime}
          disableClock={true}
        />
      </div>

      <div>
        <label>Select City:</label>
        <input
          id="city-input"
          type="text"
          placeholder="Enter your birth city"
        />
      </div>

      <div>
        <label>Time Zone Offset:</label>
        <select value={tzOffset} onChange={(e) => setTzOffset(e.target.value)}>
          {[...Array(27)].map((_, i) => {
            const offset = -12 + i;
            return (
              <option key={offset} value={offset}>
                {offset >= 0 ? `+${offset}` : offset}
              </option>
            );
          })}
        </select>
      </div>

      <button onClick={fetchBirthChart}>Get Birth Chart</button>

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