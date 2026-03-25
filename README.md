# Tuya 3-Phase Smart Breaker Local Monitor

A local Python application to monitor **3-phase electrical systems** using a Tuya-compatible smart circuit breaker. This project bypasses the cloud for real-time data retrieval, providing a "sticky" dashboard for **Voltage, Current, and Power** across all three phases.

## 📋 Features

- **Local Control:** Communicates directly with the breaker over your home Wi-Fi (no cloud latency).
- **3-Phase Decoding:** Custom Base64/Hex parsing for `dlq` category smart breakers.
- **Persistent Monitoring:** Implements a "Stateful Cache" to handle multiplexed data reporting.
- **Real-time Stats:** Tracks total system load, total current, and individual phase health.
- **Logging:** Errors and events are logged to `monitor.log` and stderr for diagnostics.
- **Graceful Shutdown:** Handles `Ctrl+C` and `SIGTERM` for a clean exit.
- **Secure Configuration:** Device credentials are loaded from a `.env` file (never committed to git).

## 🛠️ Step 1: Tuya Developer Setup

To talk to the breaker locally, you must extract its **Local Key**.

1. **Create an Account:** Sign up at the [Tuya IoT Platform](https://iot.tuya.com/).
2. **Create a Cloud Project:** Go to **Cloud > Development > Create Cloud Project**.
   - **IMPORTANT:** Ensure your Project's Data Center matches your phone's region (e.g., **Western Europe** or **Central Europe** for Egypt).
3. **Link Your App:**
   - In your project, go to **Devices > Link Tuya App Account**.
   - Scan the QR code using your **Tuya Smart** or **Smart Life** app.
4. **Get API Keys:** From the **Overview** tab, copy your Access ID and Access Secret.

## 🔑 Step 2: Extracting the Local Key

1. **Install TinyTuya:**
   ```bash
   pip install tinytuya
   ```
2. **Run the Wizard:**
   ```bash
   python -m tinytuya wizard
   ```
3. Follow the prompts to generate `devices.json`, which contains the `local_key` required for communication.

## 🔌 Step 3: Installation & Hardware

### Prerequisites

- **Static IP:** Assign a static IP (e.g., `192.168.x.x`) to your breaker via your router.
- **Python 3.8+** must be installed on your monitoring machine.

### Hardware Wiring

- Connect **L1**, **L2**, **L3**, and **Neutral (N)**.
- **Neutral (N)** is mandatory; the internal metering chip requires it for voltage sensing on Phase B and C.

## 🚀 Step 4: Application Setup

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/hmostafa17/tuya-3phase-monitor.git
   cd tuya-3phase-monitor
   ```

2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Credentials:**

   Copy the example environment file and fill in your device details:
   ```bash
   cp .env.example .env
   ```

   Edit `.env` with your values:
   ```
   DEVICE_ID=your_device_id
   IP_ADDRESS=your_device_local_ip
   LOCAL_KEY=your_local_key
   ```

4. **Run the Monitor:**
   ```bash
   python monitor.py
   ```

   Press `Ctrl+C` to stop gracefully.

## 🧠 Technical Deep-Dive

### Decoding Logic

The device uses Category **`dlq`** multiplexed reporting. It does not send all data in a single packet; instead, it rotates updates for different phases.

### Base64 Payload Mapping

| **Bytes** | **Measurement**  | **Scaling**      |
| --------- | ---------------- | ---------------- |
| **0-1**   | **Voltage**      | int / 10.0 (V)   |
| **2-4**   | **Current**      | int / 1000.0 (A) |
| **5-7**   | **Active Power** | int / 1.0 (W)    |

Payloads shorter than 8 bytes are rejected with a warning logged.

### State Management

The application implements a **Sticky Memory Cache**. This ensures that even when a packet only contains data for one phase, the dashboard retains and displays the last known values for the other phases to prevent UI flickering.

### Logging

All errors and connection events are written to `monitor.log` (and echoed to stderr). This enables diagnostics when running headless or as a background service.

## 📊 Troubleshooting

- **Scaling:** If the total system current is 10x off, adjust the ID 118 divisor in the script.
- **Network:** Ensure port **6668** is open for Tuya local traffic.
- **Logs:** Check `monitor.log` for connection errors or malformed payloads.

## 📜 License & 🛡️ Disclaimer

- **License:** MIT
- **Disclaimer:** This project is for educational purposes only. Always consult a certified electrician when working with high-voltage 3-phase systems.