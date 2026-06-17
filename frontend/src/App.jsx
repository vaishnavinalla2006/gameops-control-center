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

function App() {

  const [metrics, setMetrics] = useState({
  players_in_queue: 0,
  matches_created: 0,
  total_join_requests: 0,
  duplicate_requests_blocked: 0,
  players_removed: 0,
  avg_response_time_ms: 0,
  max_response_time_ms: 0,
  traffic_mode: "Normal",
});

  const [health, setHealth] = useState({
    status: "unknown",
    backend: "unknown",
    redis: "unknown"
  });

  const [history, setHistory] = useState([]);

  const [lastUpdated, setLastUpdated] = useState("");

  const loadMetrics = async () => {

    try {

      const metricsResponse =
        await axios.get(
          "https://gameops-control-center.onrender.com/metrics"
        );

      const healthResponse =
        await axios.get(
          "https://gameops-control-center.onrender.com/health"
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
        ...prev.slice(-19),
        {
          time: new Date().toLocaleTimeString(),
          queue:
            metricsResponse.data.players_in_queue,

          matches:
            metricsResponse.data.matches_created
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

  useEffect(() => {

    loadMetrics();

    const interval = setInterval(
      loadMetrics,
      1000
    );

    return () => clearInterval(interval);

  }, []);

  return (

    <div className="container">

      <h1 className="title">
        🎮 GameOps Control Center
      </h1>
      <p className="subtitle">
        Real-Time Matchmaking Monitoring, Traffic Simulation & Reliability Testing
      </p>

      <p className="timestamp">
        Last Updated: {lastUpdated}
      </p>

      <div className="cards">

        <div className="card health-card">
          <h3>Backend Status</h3>

          <h2>
            {health.backend === "running"
              ? "🟢 Online"
              : "🔴 Offline"}
          </h2>
        </div>

        <div className="card health-card">
          <h3>Redis Status</h3>

          <h2>
            {health.redis === "connected"
              ? "🟢 Connected"
              : "🔴 Disconnected"}
          </h2>
        </div>
        <div className="card">
          <h3>Traffic Mode</h3>

          <h2>
            {metrics.traffic_mode ===
            "Launch Day Surge"
              ? "🔴 Launch Day"

              : metrics.traffic_mode ===
                "Peak Hour"

              ? "🟡 Peak Hour"

              : "🟢 Normal"}
          </h2>
        </div>

        <div className="card">
          <h3>Players In Queue</h3>
          <h1>{metrics.players_in_queue}</h1>
        </div>

        <div className="card">
          <h3>Matches Created</h3>
          <h1>{metrics.matches_created}</h1>
        </div>

        <div className="card">
          <h3>Total Join Requests</h3>
          <h1>{metrics.total_join_requests}</h1>
        </div>

        <div className="card">
          <h3>Duplicates Blocked</h3>
          <h1>{metrics.duplicate_requests_blocked}</h1>
        </div>

        <div className="card">
          <h3>Players Removed</h3>
          <h1>{metrics.players_removed}</h1>
        </div>

        <div className="card">
          <h3>Avg Response Time</h3>
          <h1>
            {metrics.avg_response_time_ms} ms
          </h1>
        </div>

        <div className="card">
          <h3>Max Response Time</h3>
          <h1>
            {metrics.max_response_time_ms} ms
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

            <XAxis dataKey="time" />

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

            <XAxis dataKey="time" />

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