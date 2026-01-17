import statistics
import requests
import uuid
import time


class EdgeModule:
    def __init__(self, device_id, patient_id, window_size=5, threshold_k=2):
        self.device_id = device_id
        self.patient_id = patient_id
        self.window_size = window_size  # [cite: 37, 235]
        self.threshold_k = threshold_k  # [cite: 49, 101]
        self.window_values = []  # [cite: 34, 436]
        self.is_online = True  # [cite: 74, 438]
        self.buffer = []  # [cite: 75, 437]

    def preprocess(self, value):
        try:
            val = float(value)
            # Basic noise filtering and range validation [cite: 25-29, 232]
            if val < -10 or val > 10:
                return None
            return val
        except ValueError:
            return None

    def detect_anomaly(self, current_value):
        if len(self.window_values) < self.window_size:
            return False, 0

        # Calculate sliding window statistics [cite: 44-46, 552-554]
        mu = statistics.mean(self.window_values)
        sigma = statistics.stdev(self.window_values)

        # Condition: |value - mu| > k * sigma [cite: 47-49, 542]
        deviation = abs(current_value - mu)
        is_anomaly = deviation > (self.threshold_k * sigma)

        return is_anomaly, deviation

    def send_alert(self, reading, deviation):
        # Construct AnomalyEvent JSON payload [cite: 62-69, 85-94, 188-197]
        event = {
            "eventId": str(uuid.uuid4()),  # [cite: 88, 192]
            "deviceId": self.device_id,  # [cite: 89, 193]
            "patientId": self.patient_id,  # Anonymized [cite: 90, 129]
            "sensorType": reading['sensorType'],
            "measuredValue": reading['value'],  # [cite: 92, 196]
            "deviationScore": round(deviation, 2),  # [cite: 93, 197]
            "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(reading['timestamp']))
        }

        success = self._transmit(event)

        if success:
            # Log successful transmission for demo and debugging
            print("Alert sent to backend successfully!")
            # If back online, check if there are buffered events to sync [cite: 76, 283, 530]
            if not self.is_online:
                print("--- Connection Restored. Syncing Buffer... ---")
                self.is_online = True
                self.flush_buffer()
        else:
            # Network failure: switch to OFFLINE mode [cite: 75, 114-115, 272-273]
            self.is_online = False
            if len(self.buffer) < 1000:  # Prevent memory exhaustion [cite: 71, 116-117]
                self.buffer.append(event)
            print(f"OFFLINE: Event buffered. Queue size: {len(self.buffer)}")

    def _transmit(self, event):
        """Internal method to handle HTTPS POST [cite: 60-61, 265]"""
        try:
            # Updated endpoint for local demo backend (Node.js)
            # url = "http://localhost:5000/api/v1/alerts/new"  # [cite: 290]
            url = "http://localhost:3000/alert"
            response = requests.post(url, json=event, timeout=2)
            return response.status_code in [200, 201]
        except Exception:
            return False

    def flush_buffer(self):
        """RECOVERY Mode: Transmit buffered events [cite: 76, 283, 530]"""
        while self.buffer:
            buffered_event = self.buffer[0]
            if self._transmit(buffered_event):
                self.buffer.pop(0)  # Remove oldest [cite: 117]
                print(f"Synced event: {buffered_event['eventId']}")
            else:
                print("Sync failed. Back to OFFLINE mode.")
                self.is_online = False
                break