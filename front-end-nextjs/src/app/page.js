"use client";

import { useState } from "react";
import axios from "axios";

export default function Home() {
  const [url, setUrl] = useState("");
  const [qrCodeUrl, setQrCodeUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      // Ensure URL has proper format
      const formattedUrl = url.startsWith("http") ? url : `https://${url}`;

      const response = await axios.post("http://localhost:8000/generate-qr/", {
        url: formattedUrl,
      });

      setQrCodeUrl(response.data.qr_code_url);
    } catch (error) {
      setError("Failed to generate QR code. Please ensure URL is valid.");
      console.error("Error generating QR Code:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.container}>
      <h1 style={styles.title}>QR Code Generator</h1>
      <form onSubmit={handleSubmit} style={styles.form}>
        <input
          type="text"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="Enter URL (e.g., https://example.com)"
          style={styles.input}
          required
        />
        <button type="submit" style={styles.button} disabled={loading}>
          {loading ? "Generating..." : "Generate QR Code"}
        </button>
      </form>

      {error && <p style={styles.error}>{error}</p>}
      {qrCodeUrl && (
        <div style={styles.qrContainer}>
          <img src={qrCodeUrl} alt="Generated QR Code" style={styles.qrCode} />
        </div>
      )}
    </div>
  );
}

const styles = {
  container: {
    padding: "2rem",
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
  },
  title: {
    marginBottom: "2rem",
  },
  form: {
    width: "100%",
    maxWidth: "500px",
    marginBottom: "2rem",
  },
  input: {
    width: "100%",
    padding: "0.5rem",
    marginBottom: "1rem",
  },
  button: {
    width: "100%",
    padding: "0.5rem",
    backgroundColor: "#0070f3",
    color: "white",
    border: "none",
    borderRadius: "4px",
    cursor: "pointer",
  },
  error: {
    color: "red",
    marginBottom: "1rem",
  },
  qrContainer: {
    marginTop: "2rem",
  },
  qrCode: {
    maxWidth: "300px",
  },
};
