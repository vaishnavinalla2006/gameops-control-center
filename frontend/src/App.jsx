import { useEffect, useState } from "react";
import axios from "axios";

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ResponsiveContainer
} from "recharts";

import "./App.css";

const API_URL =
  "https://gameops-control-center.onrender.com";

function App() {

  const [metrics, setMetrics] = useState({
    players_in_queue: 0,
    matches_created: 0,
    total_join_requests: 0,
    duplicate_requests_blocked: 0,
    players_removed: 0,
    avg_response_time_ms: 0,
    max_response_time_ms: 0,
    traffic_mode: "NORMAL",
  });

  const [health, setHealth] = useState({
    status: "unknown",
    backend: "unknown",
    redis: "unknown"
  });

  const [history, setHistory] = useState([]);

  const [lastUpdated, setLastUpdated] =
    useState("");

  const loadMetrics = async () => {

    try {

      const metricsResponse =
        await axios.get(
          `${API_URL}/metrics`
        );

      const healthResponse =
        await axios.get(
          `${API_URL}/health`
        );

      setMetrics(
        metricsResponse.data
      );

      setHealth(
        healthResponse.data
      );

      setLastUpdated(
        new Date().toLocaleTimeString()
      );

      setHistory((prev) => [

        ...prev.slice(-29),

        {
          time:
            new Date().toLocaleTimeString(),

          queue:
            metricsResponse.data
              .players_in_queue,

          matches:
            metricsResponse.data
              .matches_created
        }

      ]);

    } catch (error) {

      console.error(error);

      setHealth({
        status: "unhealthy",
        backend: "offline",
        redis: "disconnected"
      });

    }
  };

  const startSimulation = async () => {

  try {

    await axios.post(
      `${API_URL}/start_simulation`
    );

  } catch (error) {

    console.error(error);

  }
};

const stopSimulation = async () => {

  try {

    await axios.post(
      `${API_URL}/stop_simulation`
    );

  } catch (error) {

    console.error(error);

  }
};

  const changeTrafficMode =
    async (mode) => {

      try {

        await axios.post(
          `${API_URL}/traffic_mode`,
          {
            mode: mode
          }
        );

        setHistory([]);

        loadMetrics();

      } catch (error) {

        console.error(error);

      }
    };

  const resetSystem =
    async () => {

      try {

        await axios.post(
          `${API_URL}/reset`
        );

        loadMetrics();

      } catch (error) {

        console.error(error);

      }
    };

  useEffect(() => {

    loadMetrics();

    const interval =
      setInterval(
        loadMetrics,
        1000
      );

    return () =>
      clearInterval(interval);

  }, []);

  return (

    <div className="container">

      <h1 className="title">
        🎮 GameOps Control Center
      </h1>

      <p className="subtitle">
        Real-Time Matchmaking Monitoring,
        Traffic Simulation &
        Reliability Testing
      </p>

      <p className="timestamp">
        Last Updated:
        {" "}
        {lastUpdated}
      </p>

      {/* TRAFFIC CONTROL */}

      <div className="traffic-panel">

        <h2>
          🎛 Traffic Control Center
        </h2>

        <div className="traffic-buttons">

          <button
            onClick={() =>
              changeTrafficMode(
                "NORMAL"
              )
            }
          >
            🟢 Normal Day
          </button>

          <button
            onClick={() =>
              changeTrafficMode(
                "PEAK"
              )
            }
          >
            🟡 Peak Hour
          </button>

          <button
            onClick={() =>
              changeTrafficMode(
                "LAUNCH"
              )
            }
          >
            🔴 Launch Day
          </button>

          <button
            onClick={() =>
              changeTrafficMode(
                "STREAMER"
              )
            }
          >
            🎥 Streamer Event
          </button>

          <button
            onClick={() =>
              changeTrafficMode(
                "TOURNAMENT"
              )
            }
          >
            🏆 Tournament
          </button>

          <button
            onClick={() =>
              changeTrafficMode(
                "DDOS"
              )
            }
          >
            ⚫ DDOS Test
          </button>

          <button
            onClick={resetSystem}
          >
            🧹 Reset System
          </button>

          <button
            onClick={startSimulation}
          >
            ▶ Start Simulation
          </button>

          <button
            onClick={stopSimulation}
          >
            ⏹ Stop Simulation
          </button>

        </div>

      </div>

      <div className="cards">

        <div className="card health-card">

          <h3>
            Backend Status
          </h3>

          <h2>
            {health.backend ===
            "running"
              ? "🟢 Online"
              : "🔴 Offline"}
          </h2>

        </div>

        <div className="card health-card">

          <h3>
            Redis Status
          </h3>

          <h2>
            {health.redis ===
            "connected"
              ? "🟢 Connected"
              : "🔴 Offline"}
          </h2>

        </div>

        <div className="card">

          <h3>
            Traffic Mode
          </h3>

          <h2>
            {metrics.traffic_mode}
          </h2>

        </div>

        <div className="card">
          <h3>Players In Queue</h3>
          <h1>
            {metrics.players_in_queue}
          </h1>
        </div>

        <div className="card">
          <h3>Matches Created</h3>
          <h1>
            {metrics.matches_created}
          </h1>
        </div>

        <div className="card">
          <h3>Total Requests</h3>
          <h1>
            {metrics.total_join_requests}
          </h1>
        </div>

        <div className="card">
          <h3>Duplicates</h3>
          <h1>
            {
              metrics
                .duplicate_requests_blocked
            }
          </h1>
        </div>

        <div className="card">
          <h3>Players Removed</h3>
          <h1>
            {metrics.players_removed}
          </h1>
        </div>

        <div className="card">
          <h3>Avg Response</h3>
          <h1>
            {
              metrics
                .avg_response_time_ms
            }
            ms
          </h1>
        </div>

        <div className="card">
          <h3>Max Response</h3>
          <h1>
            {
              metrics
                .max_response_time_ms
            }
            ms
          </h1>
        </div>

      </div>

      <div className="chart-container">

        <h2 className="chart-title">
          Queue Size Over Time
        </h2>

        <ResponsiveContainer
          width="100%"
          height={350}
        >

          <LineChart data={history}>

            <CartesianGrid
              strokeDasharray="3 3"
            />

            <XAxis
              dataKey="time"
            />

            <YAxis />

            <Tooltip />

            <Line
              type="monotone"
              dataKey="queue"
              stroke="#38bdf8"
              strokeWidth={3}
            />

          </LineChart>

        </ResponsiveContainer>

      </div>

      <div className="chart-container">

        <h2 className="chart-title">
          Matches Created Over Time
        </h2>

        <ResponsiveContainer
          width="100%"
          height={350}
        >

          <LineChart data={history}>

            <CartesianGrid
              strokeDasharray="3 3"
            />

            <XAxis
              dataKey="time"
            />

            <YAxis />

            <Tooltip />

            <Line
              type="monotone"
              dataKey="matches"
              stroke="#22c55e"
              strokeWidth={3}
            />

          </LineChart>

        </ResponsiveContainer>

      </div>

    </div>
  );
}

export default App;