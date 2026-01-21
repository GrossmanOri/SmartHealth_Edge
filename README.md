SmartHealth - Edge Intelligence Component 🩺⚡

Overview

This repository contains the Edge Computing Module of the SmartHealth monitoring system.
The module operates close to the data source and is responsible for reading real time ECG sensor data, performing immediate statistical analysis to detect cardiac anomalies, and transmitting critical alerts to the backend dashboard.

A core feature of this module is its network resilience. When the cloud backend is unavailable, the module stores alerts locally and synchronizes them once connectivity is restored.

⸻

Key Features

Real Time Anomaly Detection

Uses a statistical sliding window algorithm to compute the running mean and standard deviation of recent ECG readings and detect anomalies in real time.

Offline Resilience and Local Buffering

If the backend is unreachable, the module enters offline mode, queues encrypted alerts locally, and automatically synchronizes them when the connection returns.

ECG Simulation Mode

Includes a simulation engine based on the MIT BIH Arrhythmia Database that streams real ECG signals for testing and development.

Modern Tech Stack

Built with Python 3.14.2 and uses updated libraries for data processing, networking, and numerical analysis.

⸻

Architecture Flow

graph TD
    A[ECG Sensor or CSV Simulation] --> B(Pre Processing and Noise Filtering)
    B --> C{Sliding Window Algorithm}
    C -->|Normal| D[Continue Monitoring]
    C -->|Anomaly Detected| E[Generate Alert]
    E --> F{Connection Status}
    F -->|Online| G[Send Alert to Backend]
    F -->|Offline| H[Buffer Alert Locally]
    H -->|Reconnected| G


⸻

Getting Started

Prerequisites
	•	Python 3.14 or higher
	•	Node.js and npm
	•	Git

Installation
	1.	Clone the repository:

git clone https://github.com/GrossmanOri/SmartHealth_Edge.git
cd SmartHealth_Edge

	2.	Create a virtual environment:

python3 -m venv venv
source venv/bin/activate

	3.	Install Python dependencies:

pip install pandas requests numpy

	4.	Verify that the ECG dataset exists:

data/100_ekg.csv


⸻

Running the Simulation

Run the main script to start real time ECG monitoring and anomaly detection:

python3 main.py

During execution you will see:
	•	Normal ECG values printed every second
	•	Alerts printed as (! ) ALERT
	•	Successful transmissions when the backend is online
	•	Automatic buffering when the backend is offline

⸻

Running the Backend Dashboard (Live Alerts)

The backend receives alerts from the Edge module and displays them on a live dashboard in real time.
	1.	Open a new terminal and start the backend:

cd backend
npm install
node server.js

	2.	Open the dashboard in a browser:

http://localhost:3000

The root path automatically redirects to /dashboard.
The dashboard uses Server Sent Events to show each anomaly alert immediately.

⸻

Tech Stack
	•	Python 3.14.2
	•	Pandas and NumPy
	•	Requests (HTTP REST communication)
	•	Node.js and Express for the dashboard backend
	•	Server Sent Events for real time streaming
	•	JetBrains PyCharm for development

⸻

