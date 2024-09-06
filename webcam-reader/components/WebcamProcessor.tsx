import React, { useRef, useEffect, useState } from 'react';
import Webcam from 'react-webcam';
import io from 'socket.io-client';

const WebcamProcessor: React.FC = () => {
  const webcamRef = useRef<Webcam>(null);
  const [processedImage, setProcessedImage] = useState<string | null>(null);

  useEffect(() => {
    const socket = io('http://localhost:8000');

    socket.on('connect', () => {
      console.log('Connected to server');
    });

    socket.on('processed_frame', (data) => {
      setProcessedImage(`data:image/jpeg;base64,${data}`);
    });

    const interval = setInterval(() => {
      const imageSrc = webcamRef.current?.getScreenshot();
      if (imageSrc) {
        socket.emit('webcam_frame', imageSrc.split(',')[1]);
      }
    }, 100);

    return () => {
      clearInterval(interval);
      socket.disconnect();
    };
  }, []);

  return (
    <div className="flex justify-center items-center h-screen">
      <div className="relative">
        <Webcam
          audio={false}
          ref={webcamRef}
          screenshotFormat="image/jpeg"
          className="rounded-lg"
        />
        {processedImage && (
          <img
            src={processedImage}
            alt="Processed"
            className="absolute top-0 left-0 rounded-lg"
          />
        )}
      </div>
    </div>
  );
};

export default WebcamProcessor;