# Smart Sensor and Control System

This project implements a smart sensor and control system using Raspberry Pi GPIO for various sensors and actuators. The system consists of multiple connected components that communicate over TCP/IP sockets.

## Components

### 1. Ultrasonic Distance Measurement System
- **ultra_server.c**: Server that reads from ultrasonic distance sensors
- **ultra_client.c**: Client that controls motors based on distance measurements

### 2. Water and Motion Detection System
- **water_server.c**: Server that monitors water and motion sensors
- **water_client.c**: Client that controls a water pump based on sensor readings

## Features
- Real-time distance measurement using ultrasonic sensors
- Water level detection
- Motion detection
- PWM motor control
- TCP/IP communication between sensor and actuator nodes

## Hardware Requirements
- Raspberry Pi (2 or newer recommended)
- Ultrasonic distance sensors
- Water level sensors
- Motion sensors
- Servo/DC motors
- Water pump
- Appropriate wiring and circuitry

## Installation

1. Clone the repository:
```bash
git clone https://github.com/pileuszu/sensor-actuator-network.git
cd sensor-actuator-network
```

2. Compile the server and client programs:
```bash
gcc -o ultra_server ultra_server.c -lpthread
gcc -o ultra_client ultra_client.c -lpthread
gcc -o water_server water_server.c -lpthread
gcc -o water_client water_client.c -lpthread
```

## Usage

### Ultrasonic System
1. On the server Raspberry Pi:
```bash
./ultra_server 9090
```

2. On the client Raspberry Pi:
```bash
./ultra_client 127.0.0.1 9090
```
(Replace 127.0.0.1 with the server's IP address if running on different devices)

### Water & Motion System
1. On the server Raspberry Pi:
```bash
./water_server 9091
```

2. On the client Raspberry Pi:
```bash
./water_client 127.0.0.1 9091
```
(Replace 127.0.0.1 with the server's IP address if running on different devices)

## GPIO Pin Configuration

### Ultrasonic Server
- Ultrasonic Sensor 1: Trigger=GPIO23, Echo=GPIO24
- Ultrasonic Sensor 2: Trigger=GPIO5, Echo=GPIO6

### Water Server
- Water Sensor: GPIO23
- Motion Sensor: GPIO26

### Ultrasonic Client
- Button Input: GPIO20
- Motor Output: GPIO21 (PWM)

### Water Client
- Button Input: GPIO20
- Water Pump Output: GPIO21
- Additional Output: GPIO24

## System Architecture
The system follows a client-server architecture:
- Servers read data from sensors and send the measurements to clients
- Clients control actuators based on the received sensor data
- Communication happens over TCP/IP sockets
- Each component runs in a separate thread for concurrent operation

## License
[MIT License](LICENSE) 