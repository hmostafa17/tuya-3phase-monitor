import tinytuya
import time
import base64
import signal
import sys
import logging
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration
DEVICE_ID = os.environ['DEVICE_ID']
IP_ADDRESS = os.environ['IP_ADDRESS']
LOCAL_KEY = os.environ['LOCAL_KEY']

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.FileHandler('monitor.log'), logging.StreamHandler(sys.stderr)]
)
logger = logging.getLogger(__name__)

# Graceful shutdown
running = True

def shutdown(signum, frame):
    global running
    logger.info("Shutting down...")
    running = False

signal.signal(signal.SIGINT, shutdown)
signal.signal(signal.SIGTERM, shutdown)

d = tinytuya.OutletDevice(DEVICE_ID, IP_ADDRESS, LOCAL_KEY)
d.set_version(3.5)
d.set_socketPersistent(True)

memory = {
    'phases': {
        '6': {'v': 0.0, 'i': 0.0, 'p': 0.0},
        '7': {'v': 0.0, 'i': 0.0, 'p': 0.0},
        '8': {'v': 0.0, 'i': 0.0, 'p': 0.0}
    },
    'total_power': 0.0,
    'reported_current': 0.0
}

REQUIRED_PAYLOAD_BYTES = 8

def decode_dlq(b64_str):
    if not b64_str or len(b64_str) < 10:
        return None
    try:
        raw = base64.b64decode(b64_str)
        if len(raw) < REQUIRED_PAYLOAD_BYTES:
            logger.warning("Short payload: expected %d bytes, got %d", REQUIRED_PAYLOAD_BYTES, len(raw))
            return None
        return {
            'v': int.from_bytes(raw[0:2], 'big') / 10.0,
            'i': int.from_bytes(raw[2:5], 'big') / 1000.0,
            'p': int.from_bytes(raw[5:8], 'big')
        }
    except (ValueError, base64.binascii.Error) as e:
        logger.warning("Failed to decode DLQ payload: %s", e)
        return None

while running:
    try:
        payload = d.generate_payload(tinytuya.UPDATEDPS, ['6', '7', '8', '111', '118'])
        d.send(payload)
        data = d.receive()
        
        if data and 'dps' in data:
            dps = data['dps']
            for dp_id in ['6', '7', '8']:
                new_data = decode_dlq(dps.get(dp_id))
                if new_data and new_data['v'] > 50:
                    memory['phases'][dp_id] = new_data
            
            if '111' in dps: memory['total_power'] = dps['111']
            if '118' in dps: memory['reported_current'] = dps['118'] / 10.0  # Adjusted scaling

            # UI Refresh
            print("\033[H\033[J", end="") 
            print(f"--- 3-PHASE LOCAL MONITOR (LIVE) ---")
            calc_total_i = 0
            for i, dp_id in enumerate(['6', '7', '8']):
                p = memory['phases'][dp_id]
                calc_total_i += p['i']
                print(f"L{i+1}: {p['v']:6.1f}V | {p['i']:6.3f}A | {p['p']:4}W")
            print(f"------------------------------------")
            print(f"TOTAL SYSTEM LOAD:    {memory['total_power']:7.1f} W")
            print(f"SUM OF CURRENTS:      {calc_total_i:7.3f} A")
            print(f"RAW ID 118 SENSOR:    {memory['reported_current']:7.2f}")
            
    except ConnectionError as e:
        logger.error("Connection lost: %s. Retrying...", e)
    except Exception as e:
        logger.error("Unexpected error: %s", e)
    time.sleep(1)

logger.info("Monitor stopped.")