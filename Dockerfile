FROM zauberzeug/nicegui:1.4.9   


#RUN pip install pip install pywebview
#RUN pip install paho-mqtt
#COPY mqtt_led_controller_ui/main.py /app/main.py
COPY requirements.txt ./requirements.txt
RUN pip install -r requirements.txt


