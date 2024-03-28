# Use the Python base image
FROM python:3.9

# Install dependencies for running a VNC server
RUN apt-get update && apt-get install -y \
    xvfb \
    x11vnc \
    fluxbox \
    wmctrl \
    && rm -rf /var/lib/apt/lists/*

# Install Zoom
RUN wget https://zoom.us/client/latest/zoom_amd64.deb && \
    dpkg -i zoom_amd64.deb || true && \
    apt-get install -f -y && \
    rm -f zoom_amd64.deb

# Set up the VNC server
ENV DISPLAY=:1
ENV SCREEN_WIDTH=1280
ENV SCREEN_HEIGHT=720
ENV SCREEN_DEPTH=24
ENV SCREEN_DPI=96

RUN Xvfb $DISPLAY -screen 0 $SCREEN_WIDTHx$SCREEN_HEIGHTx$SCREEN_DEPTH \
    && x11vnc -display $DISPLAY -nopw -listen localhost -xkb -ncache 10 -ncache_cr -forever &

# Set the working directory
WORKDIR /app

# Copy the Python script And Files to the container
COPY . .

RUN pip install --no-cache-dir -r requirements.txt

# Start the Python script
ENTRYPOINT ["zoom"]
CMD ["python3", "main.py"]