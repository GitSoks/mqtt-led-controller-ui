FROM zauberzeug/nicegui:latest
RUN pip install pip install pywebview
RUN pip install paho-mqtt

COPY requirements.txt /opt/app/requirements.txt
WORKDIR /opt/app
RUN pip install -r requirements.txt


