import wave
import time
import riva.client
import riva.client.audio_io
import os
import anthropic
from dotenv import load_dotenv
from shared_logging import setup_logger
from agent.state import State  # Ensure the import is complete

logger = setup_logger()


class TTSService:
    def __init__(self, args):
        """Initialize TTS service with configuration parameters"""
        load_dotenv()  # This will load the .env file

        self.args = args
        self.tts_auth = riva.client.Auth(
            args.ssl_cert, args.use_ssl, args.tts_server, args.metadata
        )
        self.tts_service = riva.client.SpeechSynthesisService(self.tts_auth)
        self.nchannels = 1
        self.sampwidth = 2

    def synthesize_speech(self, text):
        """Synthesize speech from text input"""

        # client = anthropic.Anthropic()

        # message = client.messages.create(
        #     model="claude-3-5-sonnet-20241022",
        #     max_tokens=1024,
        #     messages=[
        #         {"role": "user", "content": text}
        #     ]
        # )

        # response_anth = message.content[0].text
        logger.info(f" Perceptra: {text}")
        sound_stream = None

        try:
            # Initialize audio output devices if specified
            if self.args.output_device is not None or self.args.play_audio:
                sound_stream = riva.client.audio_io.SoundCallBack(
                    self.args.output_device,
                    nchannels=self.nchannels,
                    sampwidth=self.sampwidth,
                    framerate=self.args.sample_rate_hz,
                )

            start = time.time()

            if self.args.stream:
                self._handle_streaming_synthesis(
                    text, sound_stream, start
                )  # Use Anthropic response
            else:
                self._handle_batch_synthesis(
                    text, sound_stream, start
                )  # Use Anthropic response

        except Exception as e:
            logger.error(f"TTS Error: {e}")
        finally:
            if sound_stream is not None:
                sound_stream.close()

    def _handle_streaming_synthesis(self, text, sound_stream, start):
        """Handle streaming synthesis mode"""
        responses = self.tts_service.synthesize_online(
            text,
            self.args.voice,
            self.args.language_code,
            sample_rate_hz=self.args.sample_rate_hz,
            audio_prompt_file=self.args.audio_prompt_file,
            quality=20 if self.args.quality is None else self.args.quality,
            custom_dictionary={},
        )

        first = True
        for resp in responses:
            stop = time.time()
            if first:
                logger.info(f"Time to first audio: {(stop - start):.3f}s")
                first = False
            if sound_stream is not None:
                sound_stream(resp.audio)

    def _handle_batch_synthesis(self, text, sound_stream, start):
        """Handle batch synthesis mode"""
        resp = self.tts_service.synthesize(
            text,
            self.args.voice,
            self.args.language_code,
            sample_rate_hz=self.args.sample_rate_hz,
            audio_prompt_file=self.args.audio_prompt_file,
            quality=20 if self.args.quality is None else self.args.quality,
        )
        stop = time.time()
        logger.info(f"Time spent: {(stop - start):.3f}s")

        if sound_stream is not None:
            sound_stream(resp.audio)
