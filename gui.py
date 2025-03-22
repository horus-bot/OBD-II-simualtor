from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox, QTextEdit, QSlider, QGroupBox, QScrollArea
)
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QFont
import random
import sys

# Sample Data with Additional Fault Codes
Faults = {
    "P0217 - Engine Over Temperature": ["Engine Overheating", "Coolant Leak", "Radiator Fan Failure"],
    "P0128 - Coolant Thermostat Malfunction": ["Thermostat Stuck Open", "Engine Overheating"],
    "P0087 - Fuel Rail/System Pressure Too Low": ["Low Fuel Pressure", "Fuel Pump Failure"],
    "P0193 - Fuel Rail Pressure Sensor High Input": ["Fuel Pressure Sensor Fault"],
    "P0300 - Random/Multiple Cylinder Misfire Detected": ["Random/Multiple Misfire", "Ignition Coil Failure"],
    "P0135 - O2 Sensor Heater Circuit Malfunction (Bank 1 Sensor 1)": ["O2 Sensor Malfunction"],
    "P0420 - Catalyst System Efficiency Below Threshold (Bank 1)": ["Catalyst Efficiency Below Threshold"],
    "P0401 - Exhaust Gas Recirculation Flow Insufficient Detected": ["EGR Flow Insufficient"],
    "P0171 - System Too Lean (Bank 1)": ["System Too Lean"],
    "P0172 - System Too Rich (Bank 1)": ["System Too Rich"],
    "P0455 - Evaporative Emission System Leak Detected (Gross Leak)": ["Evaporative Emission System Leak"],
    "P0700 - Transmission Control System Malfunction": ["Transmission Overheating"],
    "P0460 - Fuel Level Sensor Circuit Malfunction": ["Low Fuel Level"],
    "P0113 - Intake Air Temperature Circuit High Input": ["Ambient Air Temperature Sensor Fault"],
    "P0520 - Engine Oil Pressure Sensor/Switch Circuit Malfunction": ["Oil Pressure Out of Range"],
    "P0570 - Brake Pedal Position Sensor Circuit Malfunction": ["Brake Pedal Position Out of Range"],
    "P1600 - Steering Angle Sensor Circuit Malfunction": ["Steering Angle Out of Range"],
    "P1601 - Tire Pressure Sensor Circuit Malfunction": ["Tire Pressure Out of Range"],
    "P1602 - Alternator Output Circuit Malfunction": ["Alternator Output Out of Range"],
    "P1603 - Fuel Injector Pulse Width Out of Range": ["Fuel Injector Pulse Width Out of Range"],
    "P1604 - Knock Sensor Voltage Out of Range": ["Knock Sensor Voltage Out of Range"],
    "P1605 - Wheel Speed Sensor Circuit Malfunction": ["Wheel Speed Out of Range"],
    "P1606 - Clutch Pedal Position Sensor Circuit Malfunction": ["Clutch Pedal Position Out of Range"],
    "P1607 - Exhaust Gas Temperature Sensor Circuit Malfunction": ["Exhaust Gas Temperature Out of Range"],
    "No Faults Detected": ["Normal Driving"],
}

DrivingScenarios = {
    "City Road": {"speed_range": (0, 60), "rpm_range": (600, 3000)},
    "Highway": {"speed_range": (60, 120), "rpm_range": (2000, 4000)},
    "Off-Road": {"speed_range": (0, 40), "rpm_range": (1000, 3500)},
}

class OBDSimulator(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.sensor_data = self.generate_initial_data()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_sensor_data)
        self.is_running = False
        self.car_on = False
        self.ac_on = False
        self.brake_applied = False
        self.speed = 0
        self.selected_scenario = "City Road"

    def initUI(self):
        self.setWindowTitle("Enhanced OBD-II Simulator (Dark Theme)")
        self.setGeometry(100, 100, 800, 600)

        # Create a scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)  # Allow the widget to resize

        # Create a container widget for the main layout
        container = QWidget()
        scroll_area.setWidget(container)

        # Main layout for the container
        main_layout = QVBoxLayout(container)

        # Title
        title = QLabel("Enhanced OBD-II Diagnostic Simulator")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #88C0D0;")
        main_layout.addWidget(title)

        # Situation Simulation Section
        situation_group = QGroupBox("Situation Simulation")
        situation_group.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        situation_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #4C566A;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                color: #88C0D0;
            }
        """)
        situation_layout = QVBoxLayout()

        # Fault Code Dropdown
        fault_layout = QHBoxLayout()
        fault_label = QLabel("Select Fault Code:")
        fault_label.setFont(QFont("Arial", 12))
        self.fault_select = QComboBox()
        self.fault_select.addItems(Faults.keys())
        self.fault_select.setFont(QFont("Arial", 12))
        self.fault_select.setStyleSheet("""
            QComboBox {
                background-color: #4C566A;
                color: #ECEFF4;
                border: 1px solid #4C566A;
                padding: 5px;
                border-radius: 3px;
            }
        """)
        self.fault_select.currentIndexChanged.connect(self.update_situations)
        fault_layout.addWidget(fault_label)
        fault_layout.addWidget(self.fault_select)
        situation_layout.addLayout(fault_layout)

        # Situation Dropdown
        situation_label = QLabel("Select Situation:")
        situation_label.setFont(QFont("Arial", 12))
        self.situation_select = QComboBox()
        self.situation_select.setFont(QFont("Arial", 12))
        self.situation_select.setStyleSheet("""
            QComboBox {
                background-color: #4C566A;
                color: #ECEFF4;
                border: 1px solid #4C566A;
                padding: 5px;
                border-radius: 3px;
            }
        """)
        self.situation_select.currentIndexChanged.connect(self.update_fault_code)
        situation_layout.addWidget(situation_label)
        situation_layout.addWidget(self.situation_select)

        situation_group.setLayout(situation_layout)
        main_layout.addWidget(situation_group)

        # Car Controls Section
        controls_group = QGroupBox("Car Controls")
        controls_group.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        controls_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #4C566A;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                color: #88C0D0;
            }
        """)
        controls_layout = QVBoxLayout()

        # Start/Stop Car Button
        self.start_button = QPushButton("Start Car")
        self.start_button.setFont(QFont("Arial", 12))
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #5E81AC;
                color: #ECEFF4;
                border: none;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #81A1C1;
            }
        """)
        self.start_button.clicked.connect(self.toggle_car)
        controls_layout.addWidget(self.start_button)

        # AC Button
        self.ac_button = QPushButton("Turn AC On")
        self.ac_button.setFont(QFont("Arial", 12))
        self.ac_button.setStyleSheet("""
            QPushButton {
                background-color: #5E81AC;
                color: #ECEFF4;
                border: none;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #81A1C1;
            }
        """)
        self.ac_button.clicked.connect(self.toggle_ac)
        controls_layout.addWidget(self.ac_button)

        # Brake Button
        self.brake_button = QPushButton("Apply Brake")
        self.brake_button.setFont(QFont("Arial", 12))
        self.brake_button.setStyleSheet("""
            QPushButton {
                background-color: #BF616A;
                color: #ECEFF4;
                border: none;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #D08770;
            }
        """)
        self.brake_button.clicked.connect(self.toggle_brake)
        controls_layout.addWidget(self.brake_button)

        # Speed Slider
        speed_layout = QHBoxLayout()
        speed_label = QLabel("Speed (km/h):")
        speed_label.setFont(QFont("Arial", 12))
        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setMinimum(0)
        self.speed_slider.setMaximum(150)
        self.speed_slider.setValue(0)
        self.speed_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                background-color: #4C566A;
                height: 8px;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background-color: #88C0D0;
                width: 20px;
                height: 20px;
                margin: -6px 0;
                border-radius: 10px;
            }
        """)
        self.speed_slider.valueChanged.connect(self.update_speed)
        speed_layout.addWidget(speed_label)
        speed_layout.addWidget(self.speed_slider)
        controls_layout.addLayout(speed_layout)

        controls_group.setLayout(controls_layout)
        main_layout.addWidget(controls_group)

        # Driving Scenario Section
        scenario_group = QGroupBox("Driving Scenario")
        scenario_group.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        scenario_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #4C566A;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                color: #88C0D0;
            }
        """)
        scenario_layout = QVBoxLayout()

        scenario_label = QLabel("Select Driving Scenario:")
        scenario_label.setFont(QFont("Arial", 12))
        self.scenario_select = QComboBox()
        self.scenario_select.addItems(DrivingScenarios.keys())
        self.scenario_select.setFont(QFont("Arial", 12))
        self.scenario_select.setStyleSheet("""
            QComboBox {
                background-color: #4C566A;
                color: #ECEFF4;
                border: 1px solid #4C566A;
                padding: 5px;
                border-radius: 3px;
            }
        """)
        self.scenario_select.currentIndexChanged.connect(self.update_scenario)
        scenario_layout.addWidget(scenario_label)
        scenario_layout.addWidget(self.scenario_select)

        scenario_group.setLayout(scenario_layout)
        main_layout.addWidget(scenario_group)

        # OBD Data Display
        self.result_display = QTextEdit()
        self.result_display.setReadOnly(True)
        self.result_display.setFont(QFont("Arial", 12))
        self.result_display.setStyleSheet("""
            QTextEdit {
                background-color: #3B4252;
                color: #ECEFF4;
                border: 1px solid #4C566A;
                padding: 10px;
                border-radius: 5px;
                                          min-height: 300px;
            }
        """)
        main_layout.addWidget(QLabel("OBD-II Data:"))
        main_layout.addWidget(self.result_display)

        # Start/Stop Simulation
        sim_controls_layout = QHBoxLayout()
        self.start_sim_button = QPushButton("Start Simulation")
        self.start_sim_button.setFont(QFont("Arial", 12))
        self.start_sim_button.setStyleSheet("""
            QPushButton {
                background-color: #5E81AC;
                color: #ECEFF4;
                border: none;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #81A1C1;
            }
        """)
        self.start_sim_button.clicked.connect(self.start_simulation)
        sim_controls_layout.addWidget(self.start_sim_button)

        self.stop_sim_button = QPushButton("Stop Simulation")
        self.stop_sim_button.setFont(QFont("Arial", 12))
        self.stop_sim_button.setStyleSheet("""
            QPushButton {
                background-color: #BF616A;
                color: #ECEFF4;
                border: none;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #D08770;
            }
        """)
        self.stop_sim_button.clicked.connect(self.stop_simulation)
        self.stop_sim_button.setEnabled(False)
        sim_controls_layout.addWidget(self.stop_sim_button)

        main_layout.addLayout(sim_controls_layout)

        # Set the scroll area as the main widget
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(scroll_area)

        self.update_situations()

    def generate_initial_data(self):
        """Generate initial sensor data"""
        return {
            "Engine RPM": 0,
            "Coolant Temp (°C)": random.randint(70, 120),
            "Fuel Pressure (kPa)": random.randint(200, 4000),
            "O2 Sensor Voltage (V)": round(random.uniform(0.1, 0.9), 2),
            "Catalyst Temp (°C)": random.randint(400, 800),
            "EGR Flow (%)": round(random.uniform(0, 20), 2),
            "Short Term Fuel Trim (%)": round(random.uniform(-10, 10), 2),
            "Long Term Fuel Trim (%)": round(random.uniform(-5, 5), 2),
            "Evap System Vapor Pressure (kPa)": round(random.uniform(-5, 5), 2),
            "Transmission Temp (°C)": random.randint(70, 110),
            "Fuel Level (%)": round(random.uniform(0, 100), 2),
            "Ambient Air Temp (°C)": random.randint(-20, 40),  # Realistic range
            "Oil Pressure (psi)": round(random.uniform(20, 60), 2),
            "Brake Pedal Position (%)": 0,
            "Steering Angle (°)": round(random.uniform(-180, 180), 2),
            "Tire Pressure (psi)": round(random.uniform(28, 35), 2),
            "Alternator Output (V)": round(random.uniform(13, 15), 2),
            "Fuel Injector Pulse Width (ms)": round(random.uniform(1, 10), 2),
            "Knock Sensor Voltage (V)": round(random.uniform(0, 5), 2),
            "Wheel Speed (km/h)": 0,
            "Clutch Pedal Position (%)": 0,
            "Exhaust Gas Temp (°C)": random.randint(200, 1000),
            "Fault Code": "No Faults Detected"
        }

    def update_sensor_data(self):
        """Update sensor data dynamically"""
        selected_fault = self.fault_select.currentText()
        selected_situation = self.situation_select.currentText()
        self.sensor_data["Fault Code"] = selected_fault

        # Simulate small random changes in sensor values
        for key in self.sensor_data:
            if key == "Fault Code":
                continue
            if key == "Ambient Air Temp (°C)":
                # Ensure ambient temperature stays within a realistic range
                self.sensor_data[key] += random.randint(-1, 1)  # Small fluctuations
                self.sensor_data[key] = max(-20, min(40, self.sensor_data[key]))  # Clamp to range
            elif isinstance(self.sensor_data[key], int):
                self.sensor_data[key] += random.randint(-10, 10)
            elif isinstance(self.sensor_data[key], float):
                self.sensor_data[key] += round(random.uniform(-0.5, 0.5), 2)

        # Apply car state adjustments
        if self.car_on:
            # Car is on: simulate normal operation
            self.sensor_data["Engine RPM"] = max(600, min(5000, self.sensor_data["Engine RPM"]))
            self.sensor_data["Wheel Speed (km/h)"] = self.speed
            self.sensor_data["Fuel Pressure (kPa)"] = random.randint(200, 4000)
            self.sensor_data["O2 Sensor Voltage (V)"] = round(random.uniform(0.1, 0.9), 2)
        else:
            # Car is off: set engine RPM, wheel speed, and fuel pressure to zero
            self.sensor_data["Engine RPM"] = 0
            self.sensor_data["Wheel Speed (km/h)"] = 0
            self.sensor_data["Fuel Pressure (kPa)"] = 0

        # Apply AC state adjustments
        if self.ac_on:
            self.sensor_data["Alternator Output (V)"] = max(13, min(15, self.sensor_data["Alternator Output (V)"]))
        else:
            self.sensor_data["Alternator Output (V)"] = random.uniform(12.5, 13.5)

        # Apply brake state adjustments
        if self.brake_applied:
            self.sensor_data["Brake Pedal Position (%)"] = 100
        else:
            self.sensor_data["Brake Pedal Position (%)"] = 0

        # Ensure values stay within realistic ranges
        self.sensor_data["Coolant Temp (°C)"] = max(70, min(120, self.sensor_data["Coolant Temp (°C)"]))
        self.sensor_data["Catalyst Temp (°C)"] = max(400, min(800, self.sensor_data["Catalyst Temp (°C)"]))
        self.sensor_data["EGR Flow (%)"] = max(0, min(20, self.sensor_data["EGR Flow (%)"]))
        self.sensor_data["Short Term Fuel Trim (%)"] = max(-10, min(10, self.sensor_data["Short Term Fuel Trim (%)"]))
        self.sensor_data["Long Term Fuel Trim (%)"] = max(-5, min(5, self.sensor_data["Long Term Fuel Trim (%)"]))
        self.sensor_data["Evap System Vapor Pressure (kPa)"] = max(-5, min(5, self.sensor_data["Evap System Vapor Pressure (kPa)"]))
        self.sensor_data["Transmission Temp (°C)"] = max(70, min(110, self.sensor_data["Transmission Temp (°C)"]))
        self.sensor_data["Fuel Level (%)"] = max(0, min(100, self.sensor_data["Fuel Level (%)"]))
        self.sensor_data["Oil Pressure (psi)"] = max(20, min(60, self.sensor_data["Oil Pressure (psi)"]))
        self.sensor_data["Steering Angle (°)"] = max(-180, min(180, self.sensor_data["Steering Angle (°)"]))
        self.sensor_data["Tire Pressure (psi)"] = max(28, min(35, self.sensor_data["Tire Pressure (psi)"]))
        self.sensor_data["Fuel Injector Pulse Width (ms)"] = max(1, min(10, self.sensor_data["Fuel Injector Pulse Width (ms)"]))
        self.sensor_data["Knock Sensor Voltage (V)"] = max(0, min(5, self.sensor_data["Knock Sensor Voltage (V)"]))
        self.sensor_data["Clutch Pedal Position (%)"] = max(0, min(100, self.sensor_data["Clutch Pedal Position (%)"]))
        self.sensor_data["Exhaust Gas Temp (°C)"] = max(200, min(1000, self.sensor_data["Exhaust Gas Temp (°C)"]))

        # Update the display
        display_text = "\n".join([f"{key}: {value}" for key, value in self.sensor_data.items()])
        self.result_display.setText(display_text)

    def update_situations(self):
        """Update the list of possible situations based on the selected fault"""
        selected_fault = self.fault_select.currentText()
        situations = Faults[selected_fault]
        self.situation_select.clear()
        self.situation_select.addItems(situations)

    def update_fault_code(self):
        """Update the fault code based on the selected situation"""
        selected_situation = self.situation_select.currentText()
        for fault, situations in Faults.items():
            if selected_situation in situations:
                self.fault_select.setCurrentText(fault)
                break

    def update_scenario(self):
        """Update the driving scenario"""
        self.selected_scenario = self.scenario_select.currentText()

    def toggle_car(self):
        """Toggle car on/off"""
        self.car_on = not self.car_on
        self.start_button.setText("Stop Car" if self.car_on else "Start Car")
        self.speed_slider.setEnabled(self.car_on)
        if not self.car_on:
            self.speed = 0
            self.speed_slider.setValue(0)

    def toggle_ac(self):
        """Toggle AC on/off"""
        self.ac_on = not self.ac_on
        self.ac_button.setText("Turn AC Off" if self.ac_on else "Turn AC On")

    def toggle_brake(self):
        """Toggle brake on/off"""
        self.brake_applied = not self.brake_applied
        self.brake_button.setText("Release Brake" if self.brake_applied else "Apply Brake")

    def update_speed(self):
        """Update car speed based on slider value"""
        self.speed = self.speed_slider.value()

    def start_simulation(self):
        """Start the dynamic simulation"""
        if not self.is_running:
            self.timer.start(5000)  # Update every 5 seconds
            self.is_running = True
            self.start_sim_button.setEnabled(False)
            self.stop_sim_button.setEnabled(True)

    def stop_simulation(self):
        """Stop the dynamic simulation"""
        if self.is_running:
            self.timer.stop()
            self.is_running = False
            self.start_sim_button.setEnabled(True)
            self.stop_sim_button.setEnabled(False)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = OBDSimulator()
    window.show()
    sys.exit(app.exec())