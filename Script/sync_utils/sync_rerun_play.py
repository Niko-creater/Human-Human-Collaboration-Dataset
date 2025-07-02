import os
from tqdm import tqdm
import numpy as np
from typing import Iterator, Any
import rerun as rr

from projectaria_tools.core import data_provider
from projectaria_tools.core.sensor_data import (
    SensorData,
    ImageData,
    TimeDomain,
    TimeQueryOptions,
)
from projectaria_tools.core.stream_id import StreamId

ticsync_filenames = [
    "person_a.vrs",
    "person_b.vrs",]

streams = {
    "camera-slam-left": StreamId("1201-1"),
    "camera-slam-right":StreamId("1201-2"),
    "camera-rgb":StreamId("214-1"),
    "camera-audio":StreamId("231-1"),
    "camera-eyetracking":StreamId("211-1"),}

ticsync_sample_path = "/Users/troyehuang/projectaria_client_sdk_samples/test_recording/"

ticsync_pathnames = [
    os.path.join(ticsync_sample_path, filename)
    for filename in ticsync_filenames]

data_providers = [data_provider.create_vrs_data_provider(filename)
                  for filename in ticsync_pathnames]


def get_server_provider(providers:list[data_provider]) -> data_provider:
    server_providers = [provider for provider in providers
                       if provider.get_metadata().time_sync_mode.name == 'TicSyncServer']
    return server_providers[0]

server_provider = get_server_provider(data_providers)

def split_providers(providers:list[data_provider]) -> tuple[data_provider, list[data_provider]]:
    """A utility function used internally."""
    server_provider = [provider for provider in providers
                       if provider.get_metadata().time_sync_mode.name
                          == 'TicSyncServer'][0]
    client_providers = [provider for provider in providers
                       if provider.get_metadata().time_sync_mode.name
                          == 'TicSyncClient']
    return server_provider, client_providers

all_server_timestamps_ns = server_provider.get_timestamps_ns(
    streams["camera-rgb"], TimeDomain.DEVICE_TIME)

def check_session_ids(providers:list[data_provider]) -> None:
    session_ids = [provider.get_metadata().shared_session_id
                  for provider in providers]
    assert (sid == session_ids[0] for sid in session_ids)

def create_reference_iterator(server_provider:data_provider) -> Iterator[SensorData]:
    # Set up deliver options for the server VRS data provider.
    deliver_option = server_provider.get_default_deliver_queued_options()
    # Deactivate all server streams, for a fresh start.
    deliver_option.deactivate_stream_all()
    # Activate the one camera-rgb stream we care about.
    deliver_option.activate_stream(streams["camera-rgb"])
    # deliver_option.activate_stream(streams["camera-slam-left"])
    # deliver_option.activate_stream(streams["camera-eyetracking"])
    # deliver_option.activate_stream(streams["camera-audio"])
    # Create a timestamp-ordered, sensor-data iterator from the server.
    # This will work for large streams like the ~4GB VRS files for the
    # three-minute videos.
    result: Iterator = server_provider.deliver_queued_sensor_data(deliver_option)
    return result

SEC_PER_NS = 1 / 1e9

def diff_timestamps_ns_s(t1_ns:int, t2_ns:int) -> int:
    return (t1_ns - t2_ns) * SEC_PER_NS

def timestamp_ns_after_delay_s(timestamps_ns:list[int], delay_s:int) -> int:
    first_timestamp_ns = timestamps_ns[0]
    ts_ns = 0
    for i, ts_ns in enumerate(timestamps_ns):
        if diff_timestamps_ns_s(ts_ns, first_timestamp_ns) >= delay_s:
            break
    return ts_ns

def ticsync_time_domain_from_provider(provider: data_provider) -> TimeDomain:
    """Return a VRS file's local approximation of the conceptual
    TICSync time."""
    mode = provider.get_metadata().time_sync_mode.name
    if mode == 'TicSyncServer':
        domain = TimeDomain.DEVICE_TIME
    elif mode == 'TicSyncClient':
        domain = TimeDomain.TIC_SYNC
    else:
        raise NotImplementedError(f'Unsupported time-sync mode {mode}')
    return domain

ticsync_time_ns_after_settlement = max([timestamp_ns_after_delay_s(
    provider.get_timestamps_ns(
        streams["camera-rgb"],
        ticsync_time_domain_from_provider(provider)), 45)
    for provider in data_providers])

def log_datum(
    is_server: bool,
    device_nickname: str,  # to ID a device Rerun's display
    sensor_name: str,  # e.g., 214-1 for RGB camera
    label: str,  # e.g., camera-rgb; for double-checking
    datum: SensorData,
    timestamp_ns: int,
) -> None:
    """Called by show_rerun."""
    # Set device_entity for labeling displays in Rerun.
    rr.set_time_nanos("device_time", timestamp_ns)
    if is_server:
        device_entity = "/server/" + device_nickname + "/"
    else:
        device_entity = "/client/" + device_nickname + "/"

    rr_stream_name = device_entity + sensor_name
    # assert "camera" in label
    # The datum has its image data in slot 0.
    image_index = 0
    img = datum.image_data_and_record()[image_index].to_numpy_array()
    # Rotate the image for readability of the clock.
    rotated_img = np.rot90(img, k=1, axes=(1, 0))
    rr.log(
        rr_stream_name + "/image",
        rr.Image(rotated_img).compress(jpeg_quality=75),)

def show_rerun(providers: list[data_provider], start_ticsync_timestamp_ns:int, nframes:int = 300):
    check_session_ids(providers)
    assert nframes > 0
    server_provider, client_providers = split_providers(providers)
    server_data_stream = create_reference_iterator(server_provider)
    server_nick = server_provider.get_metadata().device_serial[-6:]
    client_nicks = [client_provider.get_metadata().device_serial[-6:]
                   for client_provider in client_providers]
    print(f'{server_nick = }')
    print(f'{client_nicks = }')
    startframe = 0
    for i, server_datum in tqdm(enumerate(server_data_stream)):
        # The server datum contains the server image. Get its timestamp,
        # in the reference TimeDomain DEVICE_TIME.
        server_timestamp_ns = server_datum.get_time_ns(TimeDomain.DEVICE_TIME)
        if server_timestamp_ns < start_ticsync_timestamp_ns:
            continue
        elif startframe == 0:
            startframe = i
        if (i - startframe) >= nframes:
            break
        # The rest of these attributes help with labeling the Rerun displays.
        stream_id = server_datum.stream_id()  # e.g. 214-1 for the RGB camera.
        stream_id_str = str(stream_id)  # as a string
        # The following will say "camera-rgb", for labeling the Rerun displays.
        stream_label = server_provider.get_label_from_stream_id(server_datum.stream_id())
        log_datum(
            is_server=True,
            device_nickname=server_nick,
            sensor_name=stream_id_str,
            label=stream_label,
            datum=server_datum,
            timestamp_ns=server_timestamp_ns,)
        for i, (nickname, provider) in enumerate(zip(client_nicks, client_providers)):
            # Get the closest client sensor datum, in its TIC_SYNC TimeDomain,
            # to the server's reference time in its DEVICE_TIME TimeDomain.
            client_datum = provider.get_sensor_data_by_time_ns(
                stream_id=stream_id,
                time_ns=server_timestamp_ns,
                time_domain=TimeDomain.TIC_SYNC,
                time_query_options=TimeQueryOptions.CLOSEST,
            )
            # Key the Rerun display of the client image to the client's TIC_SYNC time.
            client_timestamp_ns = client_datum.get_time_ns(TimeDomain.TIC_SYNC)
            # Log the client image.
            log_datum(
                is_server=False,
                device_nickname=nickname,
                sensor_name=stream_id_str,
                label=stream_label,
                datum=client_datum,
                timestamp_ns=client_timestamp_ns,)

rr.init("Aria TICSync Visualizer", spawn=True)
# rr.connect()
start_time_ns = ticsync_time_ns_after_settlement
# print(start_time_ns, len(all_server_timestamps_ns))
# print(data_providers)
show_rerun(data_providers, start_time_ns, nframes=10000)
