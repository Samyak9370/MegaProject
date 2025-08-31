import React, { useEffect, useRef, useState } from "react";

const TestWebSocket = () => {
    const wsRef = useRef(null);
    const [error, setError] = useState(null);
    const [messages, setMessages] = useState([]);

    useEffect(() => {
        let reconnectTimeout;

        const connectWebSocket = () => {
            if (wsRef.current) return; // Prevent duplicate connections

            const ws = new WebSocket("ws://localhost:8000/ws/audio/test-session");
            wsRef.current = ws;

            ws.onopen = () => {
                console.log("✅ WebSocket Connected");
                setError(null);
                ws.send(JSON.stringify({ type: "test", data: "Hello Server" }));
            };

            ws.onmessage = (e) => {
                try {
                    const msg = JSON.parse(e.data);
                    console.log("📩 Message:", msg);
                    setMessages((prev) => [...prev, msg]);
                } catch (err) {
                    console.error("Invalid JSON:", e.data);
                }
            };

            ws.onerror = (e) => {
                console.error("❌ WebSocket Error:", e);
                setError("WebSocket connection failed");
            };

            ws.onclose = (e) => {
                console.log("🔌 WebSocket Closed:", e.code, e.reason);
                setError(`WebSocket closed (code: ${e.code})`);
                wsRef.current = null;

                // Auto reconnect (only if closed abnormally)
                if (e.code !== 1000) {
                    reconnectTimeout = setTimeout(connectWebSocket, 3000);
                }
            };
        };

        connectWebSocket();

        return () => {
            clearTimeout(reconnectTimeout);
            if (wsRef.current) {
                wsRef.current.close(1000, "Component unmounted");
                wsRef.current = null;
            }
        };
    }, []);

    return (
        <div>
            <h1>🔗 Testing WebSocket...</h1>
            {error && <p style={{ color: "red" }}>{error}</p>}
            <h2>Messages:</h2>
            <ul>
                {messages.map((msg, i) => (
                    <li key={i}>{JSON.stringify(msg)}</li>
                ))}
            </ul>
        </div>
    );
};

export default TestWebSocket;
