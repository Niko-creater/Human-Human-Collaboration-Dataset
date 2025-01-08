from projectaria_tools.utils.vrs_to_mp4_utils import convert_vrs_to_mp4

from vrs_sync_to_mp4_utils import convert_sync_vrs_to_mp4

# input_vrs = "./video_vrs/recording_session_11_06_004/person_b.vrs"
# output_mp4 = "./video_mp4/recording_session_11_06_004/person_b.mp4"
# log_folder = "./logs/"
# down_sample_factor = 1
# convert_vrs_to_mp4(input_vrs, output_mp4, log_folder, down_sample_factor)

folder_name = "recording_session_12_09_001"
a_vrs = "./video_vrs/" + folder_name + "/person_a.vrs"
b_vrs = "./video_vrs/" + folder_name + "/person_b.vrs"
output_mp4 = "./video_mp4/" + folder_name +"/merge_output.mp4"
down_sample_factor = 1
convert_sync_vrs_to_mp4(a_vrs, b_vrs, output_mp4, down_sample_factor)
