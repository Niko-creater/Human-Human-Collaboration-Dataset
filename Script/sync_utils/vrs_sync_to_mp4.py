from vrs_sync_to_mp4_utils import convert_sync_vrs_to_mp4

folder_name = "/Users/troyehuang/projectaria_client_sdk_samples/alex_alex_session/"
a_vrs = folder_name + "person_a.vrs"
b_vrs = folder_name + "person_b.vrs"
output_mp4 = folder_name +"merge_output.mp4"
down_sample_factor = 1
convert_sync_vrs_to_mp4(a_vrs, b_vrs, output_mp4, down_sample_factor)
