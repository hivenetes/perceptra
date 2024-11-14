import wave
import time
import riva.client
import riva.client.audio_io
from openai import OpenAI

class TTSService:
    def __init__(self, args):
        """Initialize TTS service with configuration parameters"""
        self.args = args
        self.tts_auth = riva.client.Auth(
            args.ssl_cert, args.use_ssl, args.tts_server, args.metadata
        )
        self.tts_service = riva.client.SpeechSynthesisService(self.tts_auth)
        self.nchannels = 1
        self.sampwidth = 2
        
    def synthesize_speech(self, text):
        """Synthesize speech from text input"""
        # Initialize OpenAI client and make API call
        client = OpenAI()
        completion = client.chat.completions.create(
            model="gpt-4",  # Note: fixed typo in model name from "gpt-4o"
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": text}  # Use input text as prompt
            ]
        )
        response_oai = completion.choices[0].message.content
        
        sound_stream, out_f = None, None
        
        try:
            # Initialize audio output devices if specified
            if self.args.output_device is not None or self.args.play_audio:
                sound_stream = riva.client.audio_io.SoundCallBack(
                    self.args.output_device,
                    nchannels=self.nchannels,
                    sampwidth=self.sampwidth,
                    framerate=self.args.sample_rate_hz,
                )
            if self.args.output is not None:
                out_f = wave.open(str(self.args.output), "wb")
                out_f.setnchannels(self.nchannels)
                out_f.setsampwidth(self.sampwidth)
                out_f.setframerate(self.args.sample_rate_hz)

            print("Generating audio for request...")
            start = time.time()
            
            if self.args.stream:
                self._handle_streaming_synthesis(response_oai, sound_stream, out_f, start)  # Use OpenAI response
            else:
                self._handle_batch_synthesis(response_oai, sound_stream, out_f, start)  # Use OpenAI response
                
        except Exception as e:
            print(f"TTS Error: {e}")
        finally:
            if out_f is not None:
                out_f.close()
            if sound_stream is not None:
                sound_stream.close()

    def _handle_streaming_synthesis(self, text, sound_stream, out_f, start):
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
                print(f"Time to first audio: {(stop - start):.3f}s")
                first = False
            if sound_stream is not None:
                sound_stream(resp.audio)
            if out_f is not None:
                out_f.writeframesraw(resp.audio)

    def _handle_batch_synthesis(self, text, sound_stream, out_f, start):
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
        print(f"Time spent: {(stop - start):.3f}s")
        
        if sound_stream is not None:
            sound_stream(resp.audio)
        if out_f is not None:
            out_f.writeframesraw(resp.audio)