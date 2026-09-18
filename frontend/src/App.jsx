import { useEffect, useRef, useState } from "react";
import "./App.css";

function App() {
  const socketRef = useRef(null);

  const [connection, setConnection] = useState("Disconnected");
  const [telemetry, setTelemetry] = useState(null);
  const [socResult, setSocResult] = useState(null);

  useEffect(() => {
    const socket = new WebSocket("ws://127.0.0.1:8002/ws/telemetry");

    socketRef.current = socket;

    socket.onopen = () => {
      setConnection("Connected");
    };

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);

      setTelemetry(data.security_event?.telemetry || null);
      setSocResult(data);
    };

    socket.onclose = () => {
      setConnection("Disconnected");
    };

    socket.onerror = () => {
      setConnection("Error");
    };

    return () => {
      socket.close();
    };
  }, []);

  const sendTestTelemetry = () => {
    if (!socketRef.current || socketRef.current.readyState !== WebSocket.OPEN) {
      return;
    }

    socketRef.current.send(
      JSON.stringify({
        device_id: "ESP32-001",
        temperature: 75,
        humidity: 60,
        cpu_usage: 95,
        network_activity: "suspicious",
      })
    );
  };

  return (
    <div className="app">
      <header className="topbar">
        <div>
          <h1>Aegis-X</h1>
          <p>AI-Powered Security Operations Center</p>
        </div>

        <div className="connection">
          <span
            className={`status-dot ${
              connection === "Connected" ? "online" : "offline"
            }`}
          ></span>
          {connection}
        </div>
      </header>

      <main className="dashboard">
        <section className="hero">
          <div>
            <h2>Security Overview</h2>
            <p>Real-time IoT telemetry and SOC monitoring</p>
          </div>

          <button onClick={sendTestTelemetry}>
            Send Test Threat
          </button>
        </section>

        <section className="cards">
          <div className="card">
            <span>Device</span>
            <strong>{telemetry?.device_id || "ESP32-001"}</strong>
          </div>

          <div className="card">
            <span>Temperature</span>
            <strong>
              {telemetry?.temperature ?? "--"} °C
            </strong>
          </div>

          <div className="card">
            <span>CPU Usage</span>
            <strong>
              {telemetry?.cpu_usage ?? "--"}%
            </strong>
          </div>

          <div className="card">
            <span>ML Anomaly</span>
            <strong>
              {socResult?.ml_anomaly?.is_anomaly ? "DETECTED" : "--"}
            </strong>
          </div>
        </section>

        <section className="grid">
          <div className="panel">
            <h3>Live Telemetry</h3>

            {telemetry ? (
              <div className="telemetry">
                <div>
                  <span>Device ID</span>
                  <b>{telemetry.device_id}</b>
                </div>

                <div>
                  <span>Temperature</span>
                  <b>{telemetry.temperature} °C</b>
                </div>

                <div>
                  <span>Humidity</span>
                  <b>{telemetry.humidity}%</b>
                </div>

                <div>
                  <span>CPU Usage</span>
                  <b>{telemetry.cpu_usage}%</b>
                </div>

                <div>
                  <span>Network</span>
                  <b>{telemetry.network_activity}</b>
                </div>
              </div>
            ) : (
              <p className="muted">
                Waiting for telemetry...
              </p>
            )}
          </div>

          <div className="panel">
            <h3>SOC Analysis</h3>

            {socResult ? (
              <div className="analysis">
                <p>
                  <span>Event</span>
                  <b>
                    {socResult.security_event?.event_type}
                  </b>
                </p>

                <p>
                  <span>Risk</span>
                  <b>
                    {socResult.soc_pipeline?.security_analysis?.risk_level}
                  </b>
                </p>

                <p>
                  <span>MITRE</span>
                  <b>
                    {
                      socResult.soc_pipeline?.security_analysis
                        ?.mitre_mapping?.technique_id
                    }
                  </b>
                </p>

                <p>
                  <span>Decision</span>
                  <b>
                    {socResult.soc_pipeline?.soc_decision?.decision}
                  </b>
                </p>

                <p>
                  <span>Investigation</span>
                  <b>
                    {
                      socResult.soc_pipeline?.investigation
                        ?.investigation_status
                    }
                  </b>
                </p>
              </div>
            ) : (
              <p className="muted">
                No security event received.
              </p>
            )}
          </div>
        </section>
      </main>
    </div>
  );
}

export default App;