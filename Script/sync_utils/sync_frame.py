import os

import matplotlib.pyplot as plt
import numpy as np
from typing import Iterator, Any
import rerun as rr

from projectaria_tools.core import data_provider
from projectaria_tools.core.data_provider import VrsMetadata, MetadataTimeSyncMode
from projectaria_tools.core.sensor_data import (
    SensorData,
    ImageData,
    TimeDomain,
    TimeQueryOptions,
)
from projectaria_tools.core.stream_id import StreamId

ticsync_sample_path = "/home/peiyu/projectaria_client_sdk_samples/ticsync/recording_session_11_06_001"

ticsync_filenames = [
    "person_a.vrs",
    "person_b.vrs",]

ticsync_pathnames = [
    os.path.join(ticsync_sample_path, filename)
    for filename in ticsync_filenames]

data_providers = [data_provider.create_vrs_data_provider(filename)
                  for filename in ticsync_pathnames]

server_metadata: VrsMetadata = data_providers[0].get_metadata()
client_metadata: VrsMetadata = data_providers[1].get_metadata()

def print_session_ids(providers:list[data_provider]) -> None:
    for provider in providers:
        print(f'shared session id = {provider.get_metadata().shared_session_id}')

def check_session_ids(providers:list[data_provider]) -> None:
    session_ids = [provider.get_metadata().shared_session_id
                  for provider in providers]
    assert (sid == session_ids[0] for sid in session_ids)

# print_session_ids(data_providers)
check_session_ids(data_providers)

streams = {
    "camera-slam-left": StreamId("1201-1"),
    "camera-slam-right":StreamId("1201-2"),
    "camera-rgb":StreamId("214-1"),
    "camera-eyetracking":StreamId("211-1"),}

def get_server_provider(providers:list[data_provider]) -> data_provider:
    server_providers = [provider for provider in providers
                       if provider.get_metadata().time_sync_mode.name == 'TicSyncServer']
    return server_providers[0]

server_provider = get_server_provider(data_providers)

all_server_timestamps_ns = server_provider.get_timestamps_ns(
    streams["camera-rgb"], TimeDomain.DEVICE_TIME)
print(len(all_server_timestamps_ns))

MS_PER_NS = 1 / 1_000_000


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


def split_providers(providers: list[data_provider]) -> tuple[data_provider, list[data_provider]]:
    """A utility function used internally."""
    server_provider = [provider for provider in providers
                       if provider.get_metadata().time_sync_mode.name
                       == 'TicSyncServer'][0]
    client_providers = [provider for provider in providers
                        if provider.get_metadata().time_sync_mode.name
                        == 'TicSyncClient']
    return server_provider, client_providers


def print_timestamp_offsets_ms(time_ns: int, providers: list[data_provider]) -> None:
    """We are concerned with the offsets (time differences) between
    client glasses and server glasses. Offsets between clients are
    not informative, as each client settles to an approximation of
    the server's timestamps."""
    server_provider, client_providers = split_providers(providers)
    server_time_ns = get_closest_timestamp_ns(time_ns, server_provider)
    client_times_ns = [get_closest_timestamp_ns(time_ns, client_provider)
                       for client_provider in client_providers]
    for i, client_time_ns in enumerate(client_times_ns):
        offset = (client_time_ns - server_time_ns) * MS_PER_NS
        print(f'client{i + 1} offset (ms) = {offset}')


def get_closest_timestamp_ns(ticsync_time_ns: int, provider: data_provider) -> int:
    """Return the actual timestamp in a VRS file that's closest
    to a given time in nanoseconds."""
    domain = ticsync_time_domain_from_provider(provider)
    return provider.get_sensor_data_by_time_ns(
        stream_id=streams["camera-rgb"],
        time_ns=ticsync_time_ns,
        time_domain=domain,
        time_query_options=TimeQueryOptions.CLOSEST).get_time_ns(domain)


def get_closest_image_by_ticsync_time(ticsync_time_ns: int, provider: data_provider) -> ImageData:
    """Get an image from a VRS file closest in TICSync time to a
    given time in nanoseconds."""
    return provider.get_image_data_by_time_ns(
        stream_id=streams["camera-rgb"],
        time_ns=ticsync_time_ns,
        time_domain=ticsync_time_domain_from_provider(provider),
        time_query_options=TimeQueryOptions.CLOSEST)

def show_frames_by_ticsync_timestamp_ns(ticsync_time_ns:int, providers:list[data_provider]) -> None:
    check_session_ids(providers)
    images = [get_closest_image_by_ticsync_time(ticsync_time_ns, provider)
             for provider in providers]
    print_timestamp_offsets_ms(ticsync_time_ns, providers)
    fig_m, axes_m = plt.subplots(1, len(providers), figsize=(10, 5), dpi=300)
    image_index = 0
    for idx, frame in enumerate(images):
        axes_m[idx].set_title(providers[idx].get_metadata().time_sync_mode.name)
        npa = frame[0].to_numpy_array()
        npar = np.rot90(npa, k=1, axes=(1, 0))
        axes_m[idx].imshow(npar)
    plt.show()

show_frames_by_ticsync_timestamp_ns(all_server_timestamps_ns[len(all_server_timestamps_ns) // 2 + 100], data_providers)