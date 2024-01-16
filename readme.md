# MQTT LED Controller UI

## Overview

This project is a user interface for controlling LEDs using MQTT (Message Queuing Telemetry Transport) protocol. It allows users to remotely control the state and color of LEDs connected to an MQTT broker.

This project is designed to work with the following ESP-32 LED controller:
[https://github.com/GitSoks/esp32_led_strip_mqtt_client](https://github.com/GitSoks/esp32_led_strip_mqtt_client)

## Table of Contents

* [Introduction](#introduction)
* [Features](#features)
* [Installation](#installation)
    * [Option 1: Using Docker with an included MQTT Broker](#option-1-using-docker-with-an-included-mqtt-broker)
    * [Option 2: Using a local python environment with a custom MQTT broker](#option-2-using-a-local-python-environment-with-a-custom-mqtt-broker)
* [Usage](#usage)
* [Configuration](#configuration)
* [Used third party Python packages](#used-third-party-python-packages)
* [Contact](#contact)
* [Acknowledgments](#acknowledgments)


## Introduction

The MQTT LED Controller UI is a web-based application built with Python. It provides a user-friendly interface for controlling LEDs connected to an MQTT broker.

<img src="media/gui_readme_showcase.png" alt="menuconfig" width="70%">

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Features

- Connect to an MQTT broker and subscribe to LED control topics.
- Display the current state and color of the LEDs.
- Allow users to toggle the state of the LEDs (on/off).
- Allow users to change the color of the LEDs using a color picker.
- Publish MQTT messages to control the LEDs.
- 
<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Installation


### Option 1: Using Docker with an included MQTT Broker 
( skip this step if you want the use the GUI in a local python environment )

1. Clone the repository:

    ```bash
    git clone https://github.com/your-username/mqtt-led-controller-ui.git
    ```


2. install docke on you machine

3. compose up the docker compose file (docker-compose.yaml):

    ```bash
    docker compose up
    ```

4. Open the application in your web browser:

    ```
    http://localhost:8080
    ```

### Option 2: Using a local python environment with a custom MQTT broker

1. Clone the repository:

    ```bash
    git clone https://github.com/your-username/mqtt-led-controller-ui.git
    ```


2. install python (>= 3.10)


3. Install all python dependencies

    ```python
    pip install -r requirements.txt
    ```


4. Start the application:

    ```python
    python mqtt_led_controller_ui/main.py
    ```

5. Open the application in your web browser:

    ```
    http://localhost:8080
    ```
<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Usage

1. Launch the application in your web browser.

2. Connect to the MQTT broker by entering the required credentials.

3. Once connected, the application will display the current state and color of the LEDs.

4. Toggle the state of the LEDs by clicking the "On" or "Off" button.

5. Change the color of the LEDs by selecting a color from the color picker.

6. The application will publish MQTT messages to control the LEDs based on user actions.

<p align="right">(<a href="#readme-top">back to top</a>)</p>


## Configuration

The MQTT LED Controller UI can be configured by modifying the `settings.py` file. This file contains the following settings:

- `mqttBrokerUrl`: The URL of the MQTT broker.
- `mqttUsername`: The username for connecting to the MQTT broker (optional).
- `mqttPassword`: The password for connecting to the MQTT broker (optional).
- `ledStateTopic`: The MQTT topic for subscribing to LED state updates.
- `ledColorTopic`: The MQTT topic for subscribing to LED color updates.
- `ledControlTopic`: The MQTT topic for publishing LED control messages.
<p align="right">(<a href="#readme-top">back to top</a>)</p>


## Used third party Python packages

* [NiceGui](https://nicegui.io/) - A Python library for building web-based GUIs.
* [Paho MQTT](https://pypi.org/project/paho-mqtt/) - A Python MQTT client library.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



## Contact
David - [GitSoks on Github](Github.com/GitSoks)

Project Link: [https://github.com/GitSoks/mqtt-led-controller-ui](https://github.com/GitSoks/mqtt-led-controller-ui)


<p align="right">(<a href="#readme-top">back to top</a>)</p>



## Acknowledgments
Here are some resources that I found helpful while working on this project:

* [NiceGui](https://nicegui.io/) - A Python library for building web-based GUIs.
* [MQTT Explorer](http://mqtt-explorer.com/) - A useful tool for exploring MQTT brokers.
* [MQTT Essentials](https://www.hivemq.com/mqtt-essentials/) - A great introduction to MQTT.
* [Paho MQTT](https://pypi.org/project/paho-mqtt/) - A Python MQTT client library.



<p align="right">(<a href="#readme-top">back to top</a>)</p>