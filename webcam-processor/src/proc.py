import cv2
import numpy as np
import base64
from ultralytics import YOLO
import socketio
import eventlet

# Load the YOLOv8 model
model = YOLO("yolov8n.pt")

# Create a Socket.IO server
sio = socketio.Server(cors_allowed_origins='*')
app = socketio.WSGIApp(sio)

@sio.event
def connect(sid, environ):
    print(f'Client connected: {sid}')

@sio.event
def disconnect(sid):
    print(f'Client disconnected: {sid}')

@sio.on('webcam_frame')
def process_frame(sid, data):
    # Decode the base64 image
    img_data = base64.b64decode(data)
    nparr = np.frombuffer(img_data, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # Run YOLOv8 tracking on the frame
    results = model.track(frame, persist=True)

    # Visualize the results on the frame
    annotated_frame = results[0].plot()

    # Encode the processed frame as base64
    _, buffer = cv2.imencode('.jpg', annotated_frame)
    processed_frame = base64.b64encode(buffer).decode('utf-8')

    # Send the processed frame back to the client
    sio.emit('processed_frame', processed_frame, room=sid)

if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('localhost', 8000)), app)