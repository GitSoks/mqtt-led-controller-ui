FROM zauberzeug/nicegui:latest
RUN pip install pip install pywebview
#RUN pip install paho-mqtt

#COPY mqtt_led_controller_ui/main.py /app/main.py
COPY requirements.txt ./requirements.txt
#WORKDIR /opt/app
RUN pip install -r requirements.txt


