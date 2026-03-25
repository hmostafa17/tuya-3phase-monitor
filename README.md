**Tuya 3-Phase Smart Breaker Local Monitor**

An authentic local Python application to monitor **3-phase electrical systems** using a Tuya-compatible smart circuit breaker. This project bypasses the cloud for real-time data retrieval, providing a "sticky" dashboard for **Voltage, Current, and Power** across all three phases.

**📋 Features**

- **Local Control:** Communicates directly with the breaker over your home Wi-Fi (No cloud latency).
- **3-Phase Decoding:** Custom Base64/Hex parsing for dlq category smart breakers.
- **Persistent Monitoring:** Implements a "Stateful Cache" to handle multiplexed data reporting.
- **Real-time Stats:** Tracks total system load, total current, and individual phase health.

**🛠️ Step 1: Tuya Developer Setup**

To talk to the breaker locally, you must extract its **Local Key**.

- **Create an Account:** Sign up at the [Tuya IoT Platform](https://iot.tuya.com/).
- **Create a Cloud Project:** Go to **Cloud > Development > Create Cloud Project**.
  - **IMPORTANT:** Ensure your Project's Data Center matches your phone's region (e.g., **Western Europe** or **Central Europe** for Egypt).
- **Link Your App:**
  - In your project, go to **Devices > Link Tuya App Account**.
  - Scan the QR code using your **Tuya Smart** or **Smart Life** app.
- **Get API Keys:** From the **Overview** tab, copy your Access ID and Access Secret.

**🔑 Step 2: Extracting the Local Key**

- **Install TinyTuya:**
- pip install tinytuya
- **Run the Wizard:**
- python -m tinytuya wizard
- **Note:** Follow the prompts to generate devices.json, which contains the local_key required for communication.

**🔌 Step 3: Installation & Hardware**

**Prerequisites**

- **Static IP:** Assign a static IP (e.g., 192.168.100.33) to your breaker via your router.
- **Python 3.8+** must be installed on your monitoring machine.

**Hardware Wiring**

- Connect L1, L2, L3, and Neutral (N).
- **Neutral (N)** is mandatory; the internal metering chip requires it for voltage sensing on Phase B and C.

**🚀 Step 4: Application Setup**

- **Clone the Repository:**
- git clone \[<https://github.com/hmostafa17/tuya-3phase-monitor.git\>](<https://github.com/hmostafa17/tuya-3phase-monitor.git>)
- cd tuya-3phase-monitor
- **Configure monitor.py:** Update the following variables in the script:
  - DEVICE_ID
  - IP_ADDRESS
  - LOCAL_KEY
- **Run the Monitor:**
- python monitor.py

**🧠 Technical Deep-Dive**

**Decoding Logic**

The device uses Category **'dlq'** multiplexed reporting. It does not send all data in a single packet; instead, it rotates updates for different phases.

**Base64 Payload Mapping**

| **Bytes** | **Measurement**  | **Scaling**      |
| --------- | ---------------- | ---------------- |
| **0-1**   | **Voltage**      | int / 10.0 (V)   |
| **2-4**   | **Current**      | int / 1000.0 (A) |
| **5-7**   | **Active Power** | int / 1.0 (W)    |

**State Management**

The application implements a **Sticky Memory Cache**. This ensures that even when a packet only contains data for one phase, the dashboard retains and displays the last known values for the other phases to prevent UI flickering.

**📊 Troubleshooting**

- **Scaling:** If the total system current is 10x off, adjust the ID 118 divisor in the script.
- **Network:** Ensure port 6668 is open for Tuya local traffic.
- **Git:** If you encounter CAfile errors, run: git config --global --unset http.sslcainfo.

**📜 License & 🛡️ Disclaimer**

- **License:** MIT
- **Disclaimer:** This project is for educational purposes only. Always consult a certified electrician when working with high-voltage 3-phase systems.