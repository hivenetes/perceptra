import time
import riva.client
import riva.client.audio_io
from shared_logging import setup_logger

logger = setup_logger()

class ASRService:
    def __init__(self, args):
        self.args = args
        self.asr_auth = riva.client.Auth(
            args.ssl_cert, args.use_ssl, args.asr_server, args.metadata
        )
        self.asr_service = riva.client.ASRService(self.asr_auth)
        self.configure_asr()

    def configure_asr(self):
        self.asr_config = riva.client.StreamingRecognitionConfig(
            config=riva.client.RecognitionConfig(
                encoding=riva.client.AudioEncoding.LINEAR_PCM,
                language_code=self.args.language_code,
                model=self.args.model_name,
                max_alternatives=1,
                enable_automatic_punctuation=self.args.automatic_punctuation,
                verbatim_transcripts=not self.args.no_verbatim_transcripts,
                sample_rate_hertz=self.args.sample_rate_hz,
                audio_channel_count=1,
            ),
            interim_results=True,
        )
        riva.client.add_word_boosting_to_config(
            self.asr_config, self.args.boosted_lm_words, self.args.boosted_lm_score
        )
        riva.client.add_endpoint_parameters_to_config(
            self.asr_config,
            self.args.start_history,
            self.args.start_threshold,
            self.args.stop_history,
            self.args.stop_history_eou,
            self.args.stop_threshold,
            self.args.stop_threshold_eou,
        )
        riva.client.add_custom_configuration_to_config(
            self.asr_config, self.args.custom_configuration
        )

    def get_transcription(self, audio_chunks) -> str:
        """Process audio chunks and return final transcription"""
        final_transcript = ""

        try:
            responses = self.asr_service.streaming_response_generator(
                audio_chunks=audio_chunks, streaming_config=self.asr_config
            )

            for response in responses:
                if not response.results:  # Skip empty results
                    continue

                for result in response.results:
                    if result.is_final and result.alternatives:
                        final_transcript = result.alternatives[0].transcript
                        return final_transcript

        except Exception as e:
            logger.error(f"Error during transcription: {str(e)}")

        return final_transcript

    def record_and_transcribe(self, duration=5):
        """Record audio for specified duration and return transcription"""
        transcript = ""
        
        try:
            with riva.client.audio_io.MicrophoneStream(
                self.args.sample_rate_hz, 
                self.args.file_streaming_chunk, 
                device=self.args.input_device
            ) as audio_stream:
                responses = self.asr_service.streaming_response_generator(
                    audio_chunks=audio_stream,
                    streaming_config=self.asr_config,
                )

                start_time = time.time()
                remaining_time = duration
                
                for response in responses:
                    current_time = time.time()
                    elapsed_time = current_time - start_time
                    new_remaining_time = duration - int(elapsed_time)
                    
                    if new_remaining_time != remaining_time:
                        remaining_time = new_remaining_time
                        logger.warning(f"Time remaining: {remaining_time}s")
                    
                    if elapsed_time >= duration:
                        break

                    if response.results:
                        for result in response.results:
                            if result.alternatives:
                                transcript = result.alternatives[0].transcript

        except KeyboardInterrupt:
            logger.info("Recording stopped by user")
        except Exception as e:
            logger.error(f"Error during recording: {str(e)}")
        
        return transcript