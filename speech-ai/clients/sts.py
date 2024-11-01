import argparse
import wave
import riva.client
from riva.client.argparse_utils import add_connection_argparse_parameters, add_asr_config_argparse_parameters
import riva.client.audio_io
import time
from pathlib import Path


def parse_args() -> argparse.Namespace:
    default_device_info = riva.client.audio_io.get_default_input_device_info()
    default_device_index = None if default_device_info is None else default_device_info['index']
    
    parser = argparse.ArgumentParser(
        description="End-to-end speech agent with ASR and TTS",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    
    # ASR parameters
    parser.add_argument("--asr-server", default="localhost:50051", help="ASR server endpoint")
    parser.add_argument("--tts-server", default="localhost:50052", help="TTS server endpoint")
    parser.add_argument("--input-device", type=int, default=default_device_index, help="Input audio device to use")
    parser.add_argument("--sample-rate-hz", type=int, default=16000, help="Sample rate for audio recording")
    parser.add_argument("--file-streaming-chunk", type=int, default=1600, help="Maximum frames per audio chunk")
    parser = add_asr_config_argparse_parameters(parser)
    
    # TTS parameters
    parser.add_argument("--voice", help="Voice name for TTS")
    parser.add_argument("--output-device", type=int, help="Output device to use.")
    parser.add_argument("-o", "--output", type=Path, default="output.wav", help="Output file .wav file to write synthesized audio.")
    parser.add_argument(
        "--stream",
        action="store_true",
        help="If this option is set, then streaming synthesis is applied. Streaming means that audio is yielded "
        "as it gets ready. If `--stream` is not set, then a synthesized audio is returned in 1 response only when "
        "all text is processed.",
    )
    parser.add_argument(
        "--audio_prompt_file",
        type=Path,
        help="An input audio prompt (.wav) file for zero shot model. This is required to do zero shot inferencing.")    
    parser.add_argument("--quality", type=int, help="Number of times decoder should be run on the output audio. A higher number improves quality of the produced output but introduces latencies.")
    
    
    
    # Common parameters
    parser = add_connection_argparse_parameters(parser)
    
    args = parser.parse_args()
    return args

def get_transcription(asr_service, audio_chunks, config) -> str:
    """Process audio chunks and return final transcription"""
    final_transcript = ""
    
    try:
        responses = asr_service.streaming_response_generator(
            audio_chunks=audio_chunks,
            streaming_config=config
        )
        
        for response in responses:
            if not response.results:  # Skip empty results
                continue
                
            for result in response.results:
                if result.is_final and result.alternatives:  # Check if alternatives exist
                    final_transcript = result.alternatives[0].transcript
                    return final_transcript
                    
    except Exception as e:
        print(f"Error during transcription: {str(e)}")
        
    return final_transcript

def main() -> None:
    args = parse_args()
    if args.output is not None:
        args.output = args.output.expanduser()
    
    # Initialize ASR service
    asr_auth = riva.client.Auth(
        args.ssl_cert,
        args.use_ssl,
        args.asr_server,
        args.metadata
    )
    asr_service = riva.client.ASRService(asr_auth)
    
    # Initialize TTS service with different server
    tts_auth = riva.client.Auth(
        args.ssl_cert,
        args.use_ssl,
        args.tts_server,
        args.metadata
    )
    tts_service = riva.client.SpeechSynthesisService(tts_auth)
    nchannels = 1
    sampwidth = 2
    sound_stream, out_f = None, None
    
    # Configure ASR
    asr_config = riva.client.StreamingRecognitionConfig(
        config=riva.client.RecognitionConfig(
            encoding=riva.client.AudioEncoding.LINEAR_PCM,
            language_code=args.language_code,
            model=args.model_name,
            max_alternatives=1,
            enable_automatic_punctuation=args.automatic_punctuation,
            verbatim_transcripts=not args.no_verbatim_transcripts,
            sample_rate_hertz=args.sample_rate_hz,
            audio_channel_count=1,
        ),
        interim_results=True,
    )
    riva.client.add_word_boosting_to_config(asr_config, args.boosted_lm_words, args.boosted_lm_score)
    riva.client.add_endpoint_parameters_to_config(
        asr_config,
        args.start_history,
        args.start_threshold,
        args.stop_history,
        args.stop_history_eou,
        args.stop_threshold,
        args.stop_threshold_eou
    )
    riva.client.add_custom_configuration_to_config(
        asr_config,
        args.custom_configuration
    )    
    
    print("Recording... (Press Ctrl+C to stop)")
    
    try:
        with riva.client.audio_io.MicrophoneStream(
            args.sample_rate_hz,
            args.file_streaming_chunk,
            device=args.input_device
        ) as audio_stream, open('asr-output.txt', 'w') as output_file:
            responses = asr_service.streaming_response_generator(
                audio_chunks=audio_stream,
                streaming_config=asr_config,
            )
            for response in responses:
                if response.results:
                    for result in response.results:
                        transcript = result.alternatives[0].transcript
                        output_file.write(f"{transcript}\n")
                        output_file.flush()  # Ensure immediate writing
                        print(transcript)  # Still show in console
                        
                        

                        if transcript:
                            print("\nGenerating speech from transcription...")
                        try:
                                if args.output_device is not None or args.play_audio:
                                    sound_stream = riva.client.audio_io.SoundCallBack(
                                        args.output_device, nchannels=nchannels, sampwidth=sampwidth, framerate=args.sample_rate_hz
                                    )
                                if args.output is not None:
                                    out_f = wave.open(str(args.output), 'wb')
                                    out_f.setnchannels(nchannels)
                                    out_f.setsampwidth(sampwidth)
                                    out_f.setframerate(args.sample_rate_hz)

                                print("Generating audio for request...")
                                start = time.time()
                                if args.stream:
                                    print("args.stream", transcript)
                                    responses = tts_service.synthesize_online(
                                        transcript, args.voice, args.language_code, sample_rate_hz=args.sample_rate_hz,
                                        audio_prompt_file=args.audio_prompt_file, quality=20 if args.quality is None else args.quality,
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
                                else:
                                    print("NOT args.stream", transcript)

                                    resp = tts_service.synthesize(
                                        transcript, args.voice, args.language_code, sample_rate_hz=args.sample_rate_hz,
                                        audio_prompt_file=args.audio_prompt_file, quality=20 if args.quality is None else args.quality,
                                    )
                                    stop = time.time()
                                    print(f"Time spent: {(stop - start):.3f}s")
                                    if sound_stream is not None:
                                        sound_stream(resp.audio)
                                    if out_f is not None:
                                        out_f.writeframesraw(resp.audio)
                        except Exception as e:
                                print(e)
                        finally:
                                if out_f is not None:
                                    out_f.close()
                                if sound_stream is not None:
                                    sound_stream.close()                            
    except KeyboardInterrupt:
        print("\nRecording stopped by user")
        return

if __name__ == "__main__":
    main()