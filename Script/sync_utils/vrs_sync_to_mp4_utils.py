import os
import shutil

import numpy as np
from PIL.Image import Image
from moviepy.audio.AudioClip import AudioClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.VideoClip import VideoClip
from projectaria_tools.core import data_provider
from projectaria_tools.core.sensor_data import TimeDomain, TimeQueryOptions
from projectaria_tools.core.stream_id import StreamId

def split_providers(providers:list[data_provider]) -> tuple[data_provider, data_provider]:
    """A utility function used internally."""
    server_provider = [provider for provider in providers
                       if provider.get_metadata().time_sync_mode.name
                          == 'TicSyncServer'][0]
    client_providers = [provider for provider in providers
                       if provider.get_metadata().time_sync_mode.name
                          == 'TicSyncClient'][0]
    return server_provider, client_providers

def max_signed_value_for_bytes(n):
    return (1 << (8 * n - 1)) - 1

class VrsMp4SyncConverter:
    def __init__(self, vrs_path1: str, vrs_path2: str, down_sampling_factor: int = 1):
        self.down_sampling_factor_ = down_sampling_factor

        server_provider, client_provider = split_providers([data_provider.create_vrs_data_provider(vrs_path1),
                                                            data_provider.create_vrs_data_provider(vrs_path2)])

        self.server_provider_ = server_provider
        self.client_provider_ = client_provider

        if not self.server_provider_ or not self.client_provider_:
            raise ValueError("Either the server or client VRS file could not be read.")

        self.image_streamid_ = StreamId("214-1")
        self.audio_streamid_ = StreamId("231-1")

        if not self.server_provider_.check_stream_is_active(self.image_streamid_):
            raise SystemExit("The server VRS file does not contain RGB frames.")
        if not self.client_provider_.check_stream_is_active(self.image_streamid_):
            raise SystemExit("The client VRS file does not contain RGB frames.")

        # if not self.server_provider_.check_stream_is_active(self.audio_streamid_):
        #     raise SystemExit("The server VRS file does not contain audio.")

        self.contain_audio_ = self.server_provider_.check_stream_is_active(
            self.audio_streamid_
        )

        if self.contain_audio_ is True:
            self.audio_config = self.server_provider_.get_audio_configuration(
                self.audio_streamid_
            )
            self.audio_max_value_ = max_signed_value_for_bytes(4)

            # RECORD_TIME for audio is the START of a Record
            # DEVICE_TIME for audio is the END of a Record
            # start_audio_timestamp use RECORD_TIME while end_audio_timestamp use DEVICE_TIME
            # The time period between both times is the duration of the MP4
            self.start_timestamp_ns_ = self.server_provider_.get_first_time_ns(
                self.audio_streamid_, TimeDomain.RECORD_TIME
            )
            self.end_timestamp_ns_ = self.server_provider_.get_last_time_ns(
                self.audio_streamid_, TimeDomain.DEVICE_TIME
            )


        # Synchronization parameters
        self.start_timestamp_ns_ = self.server_provider_ .get_first_time_ns(
            self.image_streamid_, TimeDomain.DEVICE_TIME
        )
        self.end_timestamp_ns_ = self.server_provider_ .get_last_time_ns(
            self.image_streamid_, TimeDomain.DEVICE_TIME
        )

        if self.contain_audio():
            self.audio_start_timestamp_ns_ = self.server_provider_.get_first_time_ns(
                self.audio_streamid_, TimeDomain.RECORD_TIME
            )
            self.audio_offset_ns_ = self.audio_start_timestamp_ns_ - self.start_timestamp_ns_
    def contain_audio(self) -> bool:
        return self.contain_audio_


    def audio_buffersize(self):
        audio_data = self.server_provider_.get_audio_data_by_index(self.audio_streamid_, 1)
        return len(audio_data[1].capture_timestamps_ns)

    def video_fps(self):
        return self.server_provider_.get_nominal_rate_hz(self.image_streamid_)

    def make_frame(self, t: float) -> np.ndarray:
        # Calculate server and client timestamps in nanoseconds
        video_timestamp_ns = t * 1e9
        server_vrs_timestamp_ns = int(self.start_timestamp_ns_ + video_timestamp_ns)

        server_frame_data = self.server_provider_.get_image_data_by_time_ns(
            self.image_streamid_,
            server_vrs_timestamp_ns,
            TimeDomain.DEVICE_TIME,
            TimeQueryOptions.CLOSEST,
        )
        server_frame = self._convert_image(server_frame_data)

        client_frame_data = self.client_provider_.get_image_data_by_time_ns(
            self.image_streamid_,
            server_vrs_timestamp_ns,
            TimeDomain.TIC_SYNC,
            TimeQueryOptions.CLOSEST,
        )
        client_frame = self._convert_image(client_frame_data)

        # Combine server and client frames horizontally
        combined_frame = np.hstack((server_frame, client_frame))
        return combined_frame

    def _convert_image(self, image_data_and_record):
        img_array = image_data_and_record[0].to_numpy_array().copy()
        if self.down_sampling_factor_ > 1:
            img_array = Image.fromarray(img_array)
            img_array = img_array.resize(
                (
                    int(img_array.width / self.down_sampling_factor_),
                    int(img_array.height / self.down_sampling_factor_),
                )
            )
            img_array = np.array(img_array)
        img_array = np.rot90(img_array, -1)
        return img_array
    def make_audio_data(self, t) -> np.ndarray:
        if self.contain_audio_ is False:
            raise SystemExit(
                "The vrs does not contain audio and cannot be used to extract audio data."
            )

        # length of input variable len(t) == audio_buffersize - 1
        if np.size(t) == 1:
            return 0
        query_timestamp_ns = t * 1e9
        vrs_timestamp_ns = int(self.start_timestamp_ns_ + query_timestamp_ns[0])

        # obtaining the closest audio record to the vrs_timestamp_ns
        audio_data_and_config = self.server_provider_.get_audio_data_by_time_ns(
            self.audio_streamid_,
            vrs_timestamp_ns,
            TimeDomain.RECORD_TIME,
            TimeQueryOptions.CLOSEST,
        )
        audio_data = np.array(audio_data_and_config[0].data)
        audio_data = audio_data.astype(np.float64) / self.audio_max_value_

        # return all channels
        # a subset of channels create crackle sounds
        return audio_data


def convert_sync_vrs_to_mp4(
    vrs_file1: str,
    vrs_file2: str,
    output_video_file: str,
    down_sample_factor: int = 1,
):
    """Convert synchronized VRS files into a single MP4 video."""
    converter = VrsMp4SyncConverter(vrs_file1, vrs_file2, down_sample_factor)

    duration_ns = converter.end_timestamp_ns_ - converter.start_timestamp_ns_
    duration_in_seconds = duration_ns * 1e-9
    
    video_writer_clip = VideoClip(converter.make_frame, duration=duration_in_seconds)

    if os.path.exists("tmp") is False:
        os.mkdir("tmp")
    temp_audio_file = os.path.join("tmp", "audio.mp3")
    # extract audio from vrs file
    if converter.contain_audio():
        audio_writer_clip = AudioClip(
            converter.make_audio_data,
            duration=duration_in_seconds,
            fps=converter.audio_config.sample_rate,
        )
        audio_writer_clip.nchannels = converter.audio_config.num_channels
        audio_writer_clip.write_audiofile(
            temp_audio_file,
            fps=converter.audio_config.sample_rate,
            buffersize=converter.audio_buffersize(),
        )
        audio_clip = AudioFileClip(
            temp_audio_file,
        )
        video_writer_clip = video_writer_clip.with_audio(audio_clip)
        audio_writer_clip.close()

    video_writer_clip.write_videofile(output_video_file, fps=converter.video_fps())
    video_writer_clip.close()

    print(f"Output video saved at: {output_video_file}")
    shutil.rmtree("tmp")
