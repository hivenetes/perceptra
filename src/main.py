import argparse
import logging
import os
import threading
import time
from pathlib import Path
from typing import Optional, Union

import anthropic
import riva.client.audio_io
import riva.client.argparse_utils
from asr_service import ASRService
from tts_service import TTSService

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

class PerceptraAgent:
    """
    A speech-based interactive agent using ASR, TTS, and Anthropic's AI.
    
    Manages speech-to-text, AI interaction, and text-to-speech functionalities.
    """
    
    SHUTDOWN_COMMANDS = {
        "shut down", "shutdown", "exit", "close", "switch off"
    }
    
    def __init__(self, args: Optional[argparse.Namespace] = None):
        """
        Initialize Perceptra Agent with optional configuration arguments.
        
        Args:
            args (Optional[argparse.Namespace]): Configuration arguments for services.
        """
        self.args = args or self._parse_args()
        self._validate_config()
        
        self.asr_service = ASRService(self.args)
        self.tts_service = TTSService(self.args)
        self.anthropic_client = self._initialize_anthropic_client()
        
        self.stop_event = threading.Event()
    
    @staticmethod
    def _parse_args() -> argparse.Namespace:
        """
        Parse command-line arguments with comprehensive configuration options.
        
        Returns:
            argparse.Namespace: Parsed configuration arguments
        """
        parser = argparse.ArgumentParser(
            description="End-to-end speech agent with ASR and TTS",
            formatter_class=argparse.ArgumentDefaultsHelpFormatter
        )
        
        # Add ASR, TTS, and connection parameters
        parser = riva.client.argparse_utils.add_asr_config_argparse_parameters(parser)
        parser = riva.client.argparse_utils.add_connection_argparse_parameters(parser)
        
        # ASR parameters
        parser.add_argument("--asr-server", default="localhost:50051", help="ASR server endpoint")
        parser.add_argument("--tts-server", default="localhost:50052", help="TTS server endpoint")
        parser.add_argument("--input-device", type=int, help="Input audio device")
        parser.add_argument("--sample-rate-hz", type=int, default=16000, help="Audio sample rate")
        parser.add_argument("--file-streaming-chunk", type=int, default=1600, help="Audio chunk size")
        
        # TTS parameters
        parser.add_argument("--voice", help="Voice name for TTS")
        parser.add_argument("--list-devices", action="store_true", help="List output audio devices")
        parser.add_argument("--output-device", type=int, help="Output audio device")
        parser.add_argument("--stream", action="store_true", help="Enable streaming synthesis")
        parser.add_argument("--audio-prompt-file", type=Path, help="Zero-shot audio prompt file")
        parser.add_argument("--quality", type=int, help="Decoder runs for audio quality")
        parser.add_argument("--custom-dictionary", type=str, help="User dictionary file path")
        
        return parser.parse_args()
    
    def _validate_config(self):
        """
        Validate configuration and ensure required environment variables are set.
        """
        if not os.environ.get("ANTHROPIC_API_KEY"):
            raise ValueError("ANTHROPIC_API_KEY environment variable is not set")
    
    def _initialize_anthropic_client(self) -> anthropic.Anthropic:
        """
        Initialize Anthropic client with default configuration.
        
        Returns:
            anthropic.Anthropic: Configured Anthropic client
        """
        return anthropic.Anthropic()
    
    def _interact_with_anthropic(self, transcript: str) -> str:
        """
        Send transcript to Anthropic and retrieve AI response.
        
        Args:
            transcript (str): Transcribed speech input
        
        Returns:
            str: AI-generated response
        """
        # Limit the transcript to 100 characters if it's longer
        limited_transcript = transcript[:100] if len(transcript) > 100 else transcript
        
        try:
            with self.anthropic_client.messages.stream(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
                system="You are a seasoned and a smart voice assistant. Do not perform any action without be specifically requested for",
                messages=[{"role": "user", "content": limited_transcript}]
            ) as stream:
                return "".join(stream.text_stream)
        except Exception as e:
            logger.error(f"Anthropic interaction error: {e}")
            return "I'm sorry, I encountered an error processing your request."
    
    def _is_shutdown_command(self, transcript: str) -> bool:
        """
        Check if the transcript contains a shutdown command.
               Args:
            transcript (str): Transcribed speech input
        
        Returns:
            bool: Whether a shutdown command was detected
        """
        return transcript.strip().lower() in self.SHUTDOWN_COMMANDS
    
    def run(self) -> Union[None, Exception]:
        """
        Main speech processing loop with error handling and graceful shutdown.
        
        Returns:
            Optional exception if shutdown is requested
        """
        logger.info("Perceptra: I'm listening!")
        
        while not self.stop_event.is_set():
            try:
                transcript = self.asr_service.record_and_transcribe(duration=5)
                
                if not transcript:
                    continue
                
                logger.info(f"Transcript: {transcript}")
                
                if self._is_shutdown_command(transcript):
                    logger.info("Shutdown command received. Exiting...")
                    return None
                
                response_text = self._interact_with_anthropic(transcript)
                self.tts_service.synthesize_speech(response_text)
            
            except KeyboardInterrupt:
                logger.info("Recording stopped by user")
                return None
            except Exception as e:
                logger.error(f"Speech processing error: {e}")
                time.sleep(1)
    
    def shutdown(self):
        """
        Gracefully stop the agent and release resources.
        """
        self.stop_event.set()
        logger.info("Perceptra shutting down...")

def main():
    """
    Main entry point for the Perceptra Speech Agent.
    """
    try:
        agent = PerceptraAgent()
        agent.run()
    except Exception as e:
        logger.error(f"Fatal error in Perceptra: {e}")

if __name__ == "__main__":
    main()