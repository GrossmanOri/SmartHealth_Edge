import pandas as pd
import time
from edge_module import EdgeModule


def run_simulation():
    # 1. Initialize the module as defined in the LLD
    edge = EdgeModule(device_id="dev_01", patient_id="patient_100")

    # 2. Load the MIT-BIH EKG data
    try:
        df = pd.read_csv('data/100_ekg.csv')
        data_col = df.columns[1]  # Using the 'MLII' signal
    except FileNotFoundError:
        print("Error: CSV file not found in data/ folder.")
        return

    print("--- Starting SmartHealth Edge Simulation ---")

    for index, row in df.iterrows():
        raw_val = row[data_col]

        # 3. Pre-processing
        clean_val = edge.preprocess(raw_val)

        if clean_val is not None:
            # Prepare reading object for the alert system
            reading = {
                "sensorType": "ECG",
                "value": clean_val,
                "timestamp": time.time()  # Current simulation time
            }

            # 4. Anomaly Detection
            is_anomaly, deviation = edge.detect_anomaly(clean_val)

            # Update the 5-second sliding window
            edge.window_values.append(clean_val)
            if len(edge.window_values) > edge.window_size:
                edge.window_values.pop(0)

            # 5. Handle Anomaly Detection
            if is_anomaly:
                print(f"(!) ALERT: Anomaly Detected! Value: {clean_val:.2f}")
                # This calls the transmission/buffer logic we just added
                edge.send_alert(reading, deviation)
            else:
                print(f"Status: Normal | Value: {clean_val:.2f}")

        # Real-time simulation delay (1 second per reading)
        time.sleep(1)


if __name__ == "__main__":
    run_simulation()