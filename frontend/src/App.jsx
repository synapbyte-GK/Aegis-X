import { useEffect, useMemo, useRef, useState } from "react";
import "./App.css";

const WS_URL = `ws://${window.location.hostname}:8002/ws/telemetry`;
const API_BASE_URL = `${window.location.protocol}//${window.location.hostname}:8002`;

const navigation = [
  { id: "overview", label: "Overview", icon: "grid" },
  { id: "events", label: "Live Events", icon: "pulse" },
  { id: "devices", label: "Devices", icon: "server" },
  { id: "mitre", label: "MITRE ATT&CK", icon: "target" },
  { id: "investigation", label: "Investigation", icon: "search" },
];

function Icon({ name, size = 18 }) {
  const common = {
    width: size,
    height: size,
    viewBox: "0 0 24 24",
    fill: "none",
    stroke: "currentColor",
    strokeWidth: 1.8,
    strokeLinecap: "round",
    strokeLinejoin: "round",
  };

  const paths = {
    grid: (
      <>
        <rect x="3" y="3" width="7" height="7" rx="1" />
        <rect x="14" y="3" width="7" height="7" rx="1" />
        <rect x="3" y="14" width="7" height="7" rx="1" />
        <rect x="14" y="14" width="7" height="7" rx="1" />
      </>
    ),

    pulse: (
      <path d="M3 12h4l2.2-6 4.2 12 2.2-6H21" />
    ),

    server: (
      <>
        <rect x="3" y="3" width="18" height="7" rx="2" />
        <rect x="3" y="14" width="18" height="7" rx="2" />
        <path d="M7 6.5h.01M7 17.5h.01M11 6.5h6M11 17.5h6" />
      </>
    ),

    target: (
      <>
        <circle cx="12" cy="12" r="8" />
        <circle cx="12" cy="12" r="4" />
        <path d="M12 2v2M12 20v2M2 12h2M20 12h2" />
      </>
    ),

    search: (
      <>
        <circle cx="10.5" cy="10.5" r="6.5" />
        <path d="m16 16 5 5" />
      </>
    ),

    activity: (
      <path d="M4 18V9M9 18V5M14 18v-7M19 18V3" />
    ),

    shield: (
      <>
        <path d="M12 3 19 6v5c0 4.5-2.7 7.8-7 10-4.3-2.2-7-5.5-7-10V6l7-3Z" />
        <path d="m9.2 12 1.8 1.8 3.8-4" />
      </>
    ),

    send: (
      <>
        <path d="m21 3-7.4 18-3.4-7.2L3 10.4 21 3Z" />
        <path d="M10.2 13.8 21 3" />
      </>
    ),

    refresh: (
      <>
        <path d="M20 11a8 8 0 0 0-14.7-4L3 10" />
        <path d="M3 4v6h6" />
        <path d="M4 13a8 8 0 0 0 14.7 4L21 14" />
        <path d="M21 20v-6h-6" />
      </>
    ),

    clock: (
      <>
        <circle cx="12" cy="12" r="9" />
        <path d="M12 7v5l3 2" />
      </>
    ),

    cpu: (
      <>
        <rect x="6" y="6" width="12" height="12" rx="2" />
        <path d="M9 1v3M15 1v3M9 20v3M15 20v3M20 9h3M20 14h3M1 9h3M1 14h3" />
      </>
    ),

    thermometer: (
      <>
        <path d="M14 14.8V5a3 3 0 0 0-6 0v9.8a5 5 0 1 0 6 0Z" />
        <path d="M11 18v-7" />
      </>
    ),

    activity2: (
      <path d="M3 12h5l2-5 4 10 2-5h5" />
    ),
  };

  return <svg {...common}>{paths[name] || paths.grid}</svg>;
}

function MetricCard({
  label,
  value,
  suffix,
  icon,
  tone = "neutral",
  foot,
  onPointerMove,
  onPointerLeave,
}) {
  return (
    <div
      className={`metric-card ${tone}`}
      onPointerMove={onPointerMove}
      onPointerLeave={onPointerLeave}
    >
      <div className="metric-top">
        <span className="metric-label">{label}</span>

        <span className="metric-icon">
          <Icon name={icon} size={17} />
        </span>
      </div>

      <div className="metric-value">
        {value}

        {suffix && <small>{suffix}</small>}
      </div>

      <div className="metric-foot">{foot}</div>
    </div>
  );
}

function StatusPill({ children, tone = "neutral" }) {
  return (
    <span className={`status-pill ${tone}`}>
      {children}
    </span>
  );
}

function MiniChart({ values = [], label }) {
  if (!values.length) {
    return (
      <div className="chart-empty">
        <span>{label}</span>
        <small>Waiting for telemetry</small>
      </div>
    );
  }

  const width = 520;
  const height = 130;
  const padding = 8;

  const min = Math.min(...values);
  const max = Math.max(...values);
  const range = max - min || 1;

  const points = values
    .map((value, index) => {
      const x =
        padding +
        (index / Math.max(values.length - 1, 1)) *
        (width - padding * 2);

      const y =
        height -
        padding -
        ((value - min) / range) *
        (height - padding * 2);

      return `${x},${y}`;
    })
    .join(" ");

  return (
    <div className="chart-wrap">
      <div className="chart-grid" />

      <svg
        className="sparkline"
        viewBox={`0 0 ${width} ${height}`}
      >
        <polyline
          points={points}
          fill="none"
        />
      </svg>

      <div className="chart-caption">
        <span>{label}</span>

        <span>
          {values[values.length - 1]}
        </span>
      </div>
    </div>
  );
}

function App() {
  const socketRef = useRef(null);

  const [activePage, setActivePage] =
    useState("overview");

  const [connection, setConnection] =
    useState("CONNECTING");

  const [telemetry, setTelemetry] =
    useState(null);

  const [latestResult, setLatestResult] =
    useState(null);

  const [events, setEvents] =
    useState([]);

  const [historyEvents, setHistoryEvents] =
    useState([]);

  const [historyIncidents, setHistoryIncidents] =
    useState([]);

  const [temperatureHistory, setTemperatureHistory] =
    useState([]);

  const [cpuHistory, setCpuHistory] =
    useState([]);

  const [lastSync, setLastSync] =
    useState(null);

  const riskLevel =
    latestResult?.soc_pipeline?.security_analysis
      ?.risk_level || "NORMAL";

  const eventType =
    latestResult?.security_event?.event_type || "none";

  const mitreTechnique =
    latestResult?.soc_pipeline?.security_analysis
      ?.mitre_mapping?.technique_id || "—";

  const mitreName =
    latestResult?.soc_pipeline?.security_analysis
      ?.mitre_mapping?.technique_name ||
    "No technique mapped";

  const decision =
    latestResult?.soc_pipeline?.soc_decision
      ?.decision || "MONITOR";

  const investigation =
    latestResult?.soc_pipeline?.investigation
      ?.investigation_status ||
    "NO ACTIVE CASE";

  const anomalyDetected =
    latestResult?.ml_anomaly?.is_anomaly ?? false;

  const uptimeLabel =
    connection === "CONNECTED"
      ? "LIVE TELEMETRY"
      : "OFFLINE";

  // --------------------------------------------------
  // LOAD PERSISTENT SECURITY HISTORY
  // --------------------------------------------------

  useEffect(() => {
    async function loadHistory() {
      try {
        const [eventsResponse, incidentsResponse] =
          await Promise.all([
            fetch(`${API_BASE_URL}/security-events`),
            fetch(`${API_BASE_URL}/incidents`),
          ]);

        if (
          !eventsResponse.ok ||
          !incidentsResponse.ok
        ) {
          throw new Error(
            "Failed to load SOC history"
          );
        }

        const eventsData =
          await eventsResponse.json();

        const incidentsData =
          await incidentsResponse.json();

        setHistoryEvents(
          eventsData.events || []
        );

        setHistoryIncidents(
          incidentsData.incidents || []
        );
      } catch (error) {
        console.error(
          "History load error:",
          error
        );
      }
    }

    loadHistory();
  }, []);

  // --------------------------------------------------
  // CONVERT DATABASE EVENTS FOR DASHBOARD
  // --------------------------------------------------

  useEffect(() => {
    if (!historyEvents.length) {
      return;
    }

    const formattedEvents =
      historyEvents
        .map((event) => ({
          id: event.event_id,
          time: new Date(event.timestamp),
          device: event.device_id,
          type: event.event_type,
          severity: event.severity,
          message: event.message,
          mitre:
            event.mitre_mapping?.technique_id ||
            event.technique_id ||
            "—",
        }))
        .sort(
          (a, b) =>
            b.time.getTime() -
            a.time.getTime()
        )
        .slice(0, 10);

    setEvents(formattedEvents);
  }, [historyEvents]);

  // --------------------------------------------------
  // WEBSOCKET CONNECTION
  // --------------------------------------------------

  useEffect(() => {
    connectSocket();

    return () => {
      socketRef.current?.close();
    };
  }, []);

  function connectSocket() {
    if (socketRef.current) {
      socketRef.current.close();
    }

    const socket = new WebSocket(WS_URL);

    socketRef.current = socket;

    socket.onopen = () => {
      setConnection("CONNECTED");
    };

    socket.onclose = () => {
      setConnection("DISCONNECTED");

      setTimeout(() => {
        if (
          socketRef.current?.readyState !==
          WebSocket.OPEN
        ) {
          connectSocket();
        }
      }, 2500);
    };

    socket.onerror = () => {
      setConnection("ERROR");
    };

    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);

        const incomingTelemetry =
          data.security_event?.telemetry || null;

        setTelemetry(incomingTelemetry);
        setLatestResult(data);
        setLastSync(new Date());

        if (incomingTelemetry) {
          setTemperatureHistory((current) =>
            [
              ...current,
              Number(
                incomingTelemetry.temperature
              ),
            ].slice(-24)
          );

          setCpuHistory((current) =>
            [
              ...current,
              Number(
                incomingTelemetry.cpu_usage
              ),
            ].slice(-24)
          );
        }

        if (
          data.security_event
            ?.security_event_created
        ) {
          const eventData =
            data.security_event;

          const newEvent = {
            id: eventData.event_id,
            time: new Date(),
            device: eventData.device_id,
            type: eventData.event_type,
            severity: eventData.severity,
            message: eventData.message,
            mitre:
              data.soc_pipeline
                ?.security_analysis
                ?.mitre_mapping
                ?.technique_id || "—",
          };

          setEvents((current) => {
            const filtered = current.filter(
              (event) =>
                event.id !== newEvent.id
            );

            return [
              newEvent,
              ...filtered,
            ].slice(0, 10);
          });

          // Refresh persistent history after
          // a new security event is created.
          refreshHistory();
        }
      } catch {
        // Ignore malformed frames
      }
    };
  }

  // --------------------------------------------------
  // REFRESH DATABASE HISTORY
  // --------------------------------------------------

  async function refreshHistory() {
    try {
      const [eventsResponse, incidentsResponse] =
        await Promise.all([
          fetch(`${API_BASE_URL}/security-events`),
          fetch(`${API_BASE_URL}/incidents`),
        ]);

      if (
        !eventsResponse.ok ||
        !incidentsResponse.ok
      ) {
        return;
      }

      const eventsData =
        await eventsResponse.json();

      const incidentsData =
        await incidentsResponse.json();

      setHistoryEvents(
        eventsData.events || []
      );

      setHistoryIncidents(
        incidentsData.incidents || []
      );
    } catch (error) {
      console.error(
        "History refresh error:",
        error
      );
    }
  }

  // --------------------------------------------------
  // SEND TELEMETRY
  // --------------------------------------------------

  function sendTelemetry(payload) {
    if (
      !socketRef.current ||
      socketRef.current.readyState !==
      WebSocket.OPEN
    ) {
      return;
    }

    socketRef.current.send(
      JSON.stringify(payload)
    );
  }

  function sendNormalTelemetry() {
    sendTelemetry({
      device_id: "ESP32-001",
      temperature: 26.8,
      humidity: 52.4,
      cpu_usage: 22.6,
      network_activity: "normal",
    });
  }

  function simulateThreat() {
    sendTelemetry({
      device_id: "ESP32-001",
      temperature: 82.4,
      humidity: 61.2,
      cpu_usage: 94.6,
      network_activity: "suspicious",
    });
  }

  // --------------------------------------------------
  // 3D CARD INTERACTION
  // --------------------------------------------------

  function handleCardPointerMove(event) {
    const element =
      event.currentTarget;

    const rect =
      element.getBoundingClientRect();

    const x =
      event.clientX - rect.left;

    const y =
      event.clientY - rect.top;

    const rotateX =
      ((y / rect.height) - 0.5) * -4;

    const rotateY =
      ((x / rect.width) - 0.5) * 4;

    element.style.setProperty(
      "--mx",
      `${x}px`
    );

    element.style.setProperty(
      "--my",
      `${y}px`
    );

    element.style.setProperty(
      "--rx",
      `${rotateX}deg`
    );

    element.style.setProperty(
      "--ry",
      `${rotateY}deg`
    );
  }

  function handleCardPointerLeave(event) {
    const element =
      event.currentTarget;

    element.style.setProperty(
      "--rx",
      "0deg"
    );

    element.style.setProperty(
      "--ry",
      "0deg"
    );
  }

  const dashboardStats = useMemo(() => {
    const highCount = events.filter(
      (event) =>
        String(event.severity).toLowerCase() ===
        "high"
    ).length;

    return {
      alerts: events.length,
      high: highCount,
      events: events.length,
    };
  }, [events]);

  // --------------------------------------------------
  // OVERVIEW
  // --------------------------------------------------

  function renderOverview() {
    return (
      <>
        <section className="hero-section">
          <div>
            <div className="eyebrow">
              <span className="eyebrow-dot" />
              SECURITY OPERATIONS CENTER
            </div>

            <h1>Command Center</h1>

            <p>
              Real-time IoT telemetry,
              anomaly detection and
              security operations in one
              workspace.
            </p>
          </div>

          <div className="hero-actions">
            <button
              className="btn btn-secondary"
              onClick={sendNormalTelemetry}
            >
              <Icon
                name="send"
                size={16}
              />
              Normal signal
            </button>

            <button
              className="btn btn-danger"
              onClick={simulateThreat}
            >
              <Icon
                name="shield"
                size={16}
              />
              Simulate threat
            </button>
          </div>
        </section>

        <section className="metric-grid">
          <MetricCard
            label="SOC Status"
            value="ACTIVE"
            icon="shield"
            tone="good"
            foot="Decision engine online"
            onPointerMove={handleCardPointerMove}
            onPointerLeave={handleCardPointerLeave}
          />

          <MetricCard
            label="Threat Alerts"
            value={dashboardStats.alerts}
            icon="pulse"
            tone={
              dashboardStats.high
                ? "danger"
                : "neutral"
            }
            foot={`${dashboardStats.high} high severity`}
            onPointerMove={handleCardPointerMove}
            onPointerLeave={handleCardPointerLeave}
          />

          <MetricCard
            label="ML Anomalies"
            value={
              anomalyDetected
                ? "DETECTED"
                : "CLEAR"
            }
            icon="activity2"
            tone={
              anomalyDetected
                ? "danger"
                : "good"
            }
            foot="Isolation Forest + rules"
            onPointerMove={handleCardPointerMove}
            onPointerLeave={handleCardPointerLeave}
          />

          <MetricCard
            label="Device"
            value="ESP32-001"
            icon="server"
            tone="neutral"
            foot={uptimeLabel}
            onPointerMove={handleCardPointerMove}
            onPointerLeave={handleCardPointerLeave}
          />
        </section>

        <section className="content-grid">
          <div
            className="panel wide-panel"
            onPointerMove={handleCardPointerMove}
            onPointerLeave={handleCardPointerLeave}
          >
            <div className="panel-header">
              <div>
                <span className="panel-kicker">
                  TELEMETRY STREAM
                </span>

                <h2>Signal monitor</h2>
              </div>

              <StatusPill
                tone={
                  connection ===
                    "CONNECTED"
                    ? "good"
                    : "danger"
                }
              >
                ● {connection}
              </StatusPill>
            </div>

            <div className="telemetry-grid">
              <div className="telemetry-item">
                <span>Temperature</span>

                <strong>
                  {telemetry?.temperature ??
                    "—"}

                  <small> °C</small>
                </strong>
              </div>

              <div className="telemetry-item">
                <span>Humidity</span>

                <strong>
                  {telemetry?.humidity ??
                    "—"}

                  <small> %</small>
                </strong>
              </div>

              <div className="telemetry-item">
                <span>CPU Usage</span>

                <strong>
                  {telemetry?.cpu_usage ??
                    "—"}

                  <small> %</small>
                </strong>
              </div>

              <div className="telemetry-item">
                <span>Network</span>

                <strong className="capitalize">
                  {telemetry?.network_activity ??
                    "—"}
                </strong>
              </div>
            </div>

            <div className="charts-row">
              <div className="chart-card">
                <div className="chart-title">
                  <span>
                    Temperature trend
                  </span>

                  <Icon
                    name="thermometer"
                    size={16}
                  />
                </div>

                <MiniChart
                  values={temperatureHistory}
                  label="°C"
                />
              </div>

              <div className="chart-card">
                <div className="chart-title">
                  <span>
                    CPU utilization
                  </span>

                  <Icon
                    name="cpu"
                    size={16}
                  />
                </div>

                <MiniChart
                  values={cpuHistory}
                  label="%"
                />
              </div>
            </div>
          </div>

          <div
            className="panel"
            onPointerMove={handleCardPointerMove}
            onPointerLeave={handleCardPointerLeave}
          >
            <div className="panel-header">
              <div>
                <span className="panel-kicker">
                  SOC VERDICT
                </span>

                <h2>
                  Current assessment
                </h2>
              </div>
            </div>

            <div className="verdict">
              <div
                className={`verdict-icon ${riskLevel === "HIGH"
                  ? "critical"
                  : "safe"
                  }`}
              >
                <Icon
                  name={
                    riskLevel === "HIGH"
                      ? "target"
                      : "shield"
                  }
                  size={28}
                />
              </div>

              <div>
                <div className="verdict-title">
                  {riskLevel === "HIGH"
                    ? "Security event detected"
                    : "System operating normally"}
                </div>

                <div className="verdict-subtitle">
                  {eventType === "none"
                    ? "No active security event"
                    : `${eventType} activity detected`}
                </div>
              </div>
            </div>

            <div className="detail-list">
              <div>
                <span>Risk level</span>

                <StatusPill
                  tone={
                    riskLevel === "HIGH"
                      ? "danger"
                      : "good"
                  }
                >
                  {riskLevel}
                </StatusPill>
              </div>

              <div>
                <span>MITRE</span>

                <strong>
                  {mitreTechnique}
                </strong>
              </div>

              <div>
                <span>Decision</span>

                <strong>
                  {decision}
                </strong>
              </div>

              <div>
                <span>
                  Investigation
                </span>

                <strong>
                  {investigation}
                </strong>
              </div>
            </div>
          </div>
        </section>

        <section
          className="panel"
          onPointerMove={handleCardPointerMove}
          onPointerLeave={handleCardPointerLeave}
        >
          <div className="panel-header">
            <div>
              <span className="panel-kicker">
                SECURITY FEED
              </span>

              <h2>Recent events</h2>
            </div>

            <button
              className="icon-button"
              onClick={() => {
                setEvents([]);
                setHistoryEvents([]);
              }}
              title="Clear session events"
            >
              <Icon
                name="refresh"
                size={17}
              />
            </button>
          </div>

          <EventTable
            events={events}
          />
        </section>
      </>
    );
  }

  // --------------------------------------------------
  // EVENTS
  // --------------------------------------------------

  function renderEvents() {
    return (
      <section
        className="panel full-page-panel"
        onPointerMove={handleCardPointerMove}
        onPointerLeave={handleCardPointerLeave}
      >
        <div className="panel-header">
          <div>
            <span className="panel-kicker">
              LIVE EVENTS
            </span>

            <h2>
              Security event stream
            </h2>
          </div>

          <button
            className="btn btn-danger"
            onClick={simulateThreat}
          >
            <Icon
              name="shield"
              size={16}
            />
            Generate event
          </button>
        </div>

        <EventTable
          events={events}
          large
        />
      </section>
    );
  }

  // --------------------------------------------------
  // DEVICES
  // --------------------------------------------------

  function renderDevices() {
    return (
      <section
        className="panel full-page-panel"
        onPointerMove={handleCardPointerMove}
        onPointerLeave={handleCardPointerLeave}
      >
        <div className="panel-header">
          <div>
            <span className="panel-kicker">
              DEVICE MONITORING
            </span>

            <h2>
              Connected assets
            </h2>
          </div>
        </div>

        <div className="device-card">
          <div className="device-main">
            <div className="device-avatar">
              <Icon
                name="server"
                size={24}
              />
            </div>

            <div>
              <h3>ESP32-001</h3>

              <p>
                IoT telemetry endpoint
              </p>
            </div>
          </div>

          <StatusPill
            tone={
              connection === "CONNECTED"
                ? "good"
                : "danger"
            }
          >
            {connection === "CONNECTED"
              ? "ONLINE"
              : "OFFLINE"}
          </StatusPill>
        </div>

        <div className="device-details">
          <div>
            <span>
              Temperature
            </span>

            <strong>
              {telemetry?.temperature ??
                "—"}{" "}
              °C
            </strong>
          </div>

          <div>
            <span>CPU</span>

            <strong>
              {telemetry?.cpu_usage ??
                "—"}%
            </strong>
          </div>

          <div>
            <span>Humidity</span>

            <strong>
              {telemetry?.humidity ??
                "—"}%
            </strong>
          </div>

          <div>
            <span>Network</span>

            <strong className="capitalize">
              {telemetry?.network_activity ??
                "—"}
            </strong>
          </div>
        </div>
      </section>
    );
  }

  // --------------------------------------------------
  // MITRE
  // --------------------------------------------------

  function renderMitre() {
    return (
      <section
        className="panel full-page-panel"
        onPointerMove={handleCardPointerMove}
        onPointerLeave={handleCardPointerLeave}
      >
        <div className="panel-header">
          <div>
            <span className="panel-kicker">
              THREAT INTELLIGENCE
            </span>

            <h2>
              MITRE ATT&CK mapping
            </h2>
          </div>
        </div>

        <div className="mitre-feature">
          <div className="mitre-id">
            {mitreTechnique}
          </div>

          <div className="mitre-copy">
            <span>
              Mapped technique
            </span>

            <h3>{mitreName}</h3>

            <p>
              The SOC pipeline maps the
              observed security event to
              an ATT&CK technique for
              investigation context.
            </p>
          </div>
        </div>

        <div className="info-grid">
          <div>
            <span>
              Observed event
            </span>

            <strong>
              {eventType}
            </strong>
          </div>

          <div>
            <span>Risk level</span>

            <strong>
              {riskLevel}
            </strong>
          </div>

          <div>
            <span>SOC decision</span>

            <strong>
              {decision}
            </strong>
          </div>
        </div>
      </section>
    );
  }

  // --------------------------------------------------
  // INVESTIGATION
  // --------------------------------------------------

  function renderInvestigation() {
    const findings =
      latestResult?.soc_pipeline
        ?.investigation?.findings || [];

    return (
      <section
        className="panel full-page-panel"
        onPointerMove={handleCardPointerMove}
        onPointerLeave={handleCardPointerLeave}
      >
        <div className="panel-header">
          <div>
            <span className="panel-kicker">
              INCIDENT RESPONSE
            </span>

            <h2>
              Investigation workspace
            </h2>
          </div>

          <StatusPill
            tone={
              riskLevel === "HIGH"
                ? "danger"
                : "good"
            }
          >
            {investigation}
          </StatusPill>
        </div>

        <div className="investigation-layout">
          <div className="investigation-card">
            <span className="panel-kicker">
              DECISION
            </span>

            <strong>
              {decision}
            </strong>

            <p>
              {latestResult?.soc_pipeline
                ?.response
                ?.recommended_action ||
                "No response action is currently active."}
            </p>
          </div>

          <div className="investigation-card">
            <span className="panel-kicker">
              FINDINGS
            </span>

            {findings.length ? (
              <div className="finding-list">
                {findings.map(
                  (finding, index) => (
                    <div
                      className="finding"
                      key={index}
                    >
                      <span>
                        {String(
                          index + 1
                        ).padStart(2, "0")}
                      </span>

                      <p>{finding}</p>
                    </div>
                  )
                )}
              </div>
            ) : (
              <p className="muted">
                No active investigation
                findings.
              </p>
            )}
          </div>
        </div>
        <div className="incident-history">
          <div className="panel-header">
            <div>
              <span className="panel-kicker">
                INCIDENT HISTORY
              </span>

              <h2>Stored incidents</h2>
            </div>

            <StatusPill tone="neutral">
              {historyIncidents.length} TOTAL
            </StatusPill>
          </div>

          <IncidentTable
            incidents={historyIncidents}
          />
        </div>
      </section>
    );
  }

  // --------------------------------------------------
  // MAIN APP
  // --------------------------------------------------

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">
            <span />
            <span />
            <span />
          </div>

          <div>
            <div className="brand-name">
              AEGIS-X
            </div>

            <div className="brand-sub">
              SOC ENGINE
            </div>
          </div>
        </div>

        <div className="side-label">
          OPERATIONS
        </div>

        <nav className="nav-list">
          {navigation.map((item) => (
            <button
              key={item.id}
              className={`nav-item ${activePage === item.id
                ? "active"
                : ""
                }`}
              onClick={() =>
                setActivePage(item.id)
              }
            >
              <Icon
                name={item.icon}
                size={18}
              />

              <span>
                {item.label}
              </span>
            </button>
          ))}
        </nav>

        <div className="sidebar-bottom">
          <div className="engine-box">
            <div className="engine-status">
              <span className="live-dot" />

              <span>
                Detection engine
              </span>
            </div>

            <strong>
              OPERATIONAL
            </strong>

            <small>
              ML + rule based analysis
            </small>
          </div>

          <div className="side-footer">
            <span>
              AEGIS-X v1.0
            </span>

            <span>
              LOCAL SOC
            </span>
          </div>
        </div>
      </aside>

      <main className="main-area">
        <header className="topbar">
          <div className="breadcrumb">
            <span>Aegis-X</span>

            <b>/</b>

            <strong>
              {
                navigation.find(
                  (item) =>
                    item.id === activePage
                )?.label
              }
            </strong>
          </div>

          <div className="topbar-right">
            <div className="sync-time">
              <Icon
                name="clock"
                size={15}
              />

              <span>
                {lastSync
                  ? `Last sync ${lastSync.toLocaleTimeString()}`
                  : "Awaiting telemetry"}
              </span>
            </div>

            <StatusPill
              tone={
                connection ===
                  "CONNECTED"
                  ? "good"
                  : "danger"
              }
            >
              <span className="live-dot small" />

              {connection}
            </StatusPill>

            <button
              className="icon-button"
              onClick={connectSocket}
              title="Reconnect"
            >
              <Icon
                name="refresh"
                size={17}
              />
            </button>
          </div>
        </header>

        <div className="page-content">
          {activePage === "overview" &&
            renderOverview()}

          {activePage === "events" &&
            renderEvents()}

          {activePage === "devices" &&
            renderDevices()}

          {activePage === "mitre" &&
            renderMitre()}

          {activePage ===
            "investigation" &&
            renderInvestigation()}
        </div>
      </main>
    </div>
  );
}

// --------------------------------------------------
// EVENT TABLE
// --------------------------------------------------
function IncidentTable({
  incidents = [],
}) {
  if (!incidents.length) {
    return (
      <div className="empty-state">
        <div className="empty-icon">
          <Icon
            name="shield"
            size={22}
          />
        </div>

        <h3>
          No stored incidents
        </h3>

        <p>
          Threat incidents created by
          the SOC pipeline will appear
          here.
        </p>
      </div>
    );
  }

  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>INCIDENT</th>
            <th>DEVICE</th>
            <th>TITLE</th>
            <th>SEVERITY</th>
            <th>RISK</th>
            <th>STATUS</th>
            <th>CREATED</th>
          </tr>
        </thead>

        <tbody>
          {incidents.map((incident) => {
            const createdAt =
              new Date(
                incident.created_at
              );

            const status =
              String(
                incident.status || ""
              ).toUpperCase();

            let statusTone = "neutral";

            if (status === "OPEN") {
              statusTone = "danger";
            }

            if (status === "RESOLVED") {
              statusTone = "good";
            }

            return (
              <tr
                key={incident.incident_id}
              >
                <td>
                  <span className="mono">
                    {incident.incident_id}
                  </span>
                </td>

                <td>
                  <strong>
                    {incident.device_id}
                  </strong>
                </td>

                <td className="message-cell">
                  {incident.title}
                </td>

                <td>
                  <StatusPill
                    tone={
                      String(
                        incident.severity
                      ).toLowerCase() ===
                        "high"
                        ? "danger"
                        : "neutral"
                    }
                  >
                    {String(
                      incident.severity
                    ).toUpperCase()}
                  </StatusPill>
                </td>

                <td>
                  <StatusPill
                    tone={
                      String(
                        incident.risk_level
                      ).toUpperCase() ===
                        "HIGH"
                        ? "danger"
                        : "neutral"
                    }
                  >
                    {String(
                      incident.risk_level
                    ).toUpperCase()}
                  </StatusPill>
                </td>

                <td>
                  <StatusPill tone={statusTone}>
                    {status}
                  </StatusPill>
                </td>

                <td>
                  {Number.isNaN(
                    createdAt.getTime()
                  )
                    ? "—"
                    : createdAt.toLocaleString()}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
function EventTable({
  events,
  large = false,
}) {
  if (!events.length) {
    return (
      <div
        className={`empty-state ${large ? "large" : ""
          }`}
      >
        <div className="empty-icon">
          <Icon
            name="pulse"
            size={22}
          />
        </div>

        <h3>
          No security events in this
          session
        </h3>

        <p>
          Use “Simulate threat” or send
          telemetry from the IoT
          simulator to populate the
          security feed.
        </p>
      </div>
    );
  }

  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>TIME</th>
            <th>DEVICE</th>
            <th>EVENT</th>
            <th>SEVERITY</th>
            <th>MITRE</th>
            <th>MESSAGE</th>
          </tr>
        </thead>

        <tbody>
          {events.map((event) => (
            <tr key={event.id}>
              <td>
                {event.time instanceof Date &&
                  !Number.isNaN(
                    event.time.getTime()
                  )
                  ? event.time.toLocaleTimeString()
                  : "—"}
              </td>

              <td>
                <strong>
                  {event.device}
                </strong>
              </td>

              <td>
                <span className="event-name">
                  {event.type}
                </span>
              </td>

              <td>
                <StatusPill
                  tone={
                    String(
                      event.severity
                    ).toLowerCase() ===
                      "high"
                      ? "danger"
                      : "neutral"
                  }
                >
                  {String(
                    event.severity
                  ).toUpperCase()}
                </StatusPill>
              </td>

              <td>
                <span className="mono">
                  {event.mitre}
                </span>
              </td>

              <td className="message-cell">
                {event.message}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default App;