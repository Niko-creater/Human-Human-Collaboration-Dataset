from moviepy.editor import VideoFileClip, AudioFileClip

clip = VideoFileClip("/Users/troyehuang/projectaria_client_sdk_samples/alex_alex_session/merge_output.mp4")

clip = clip.volumex(3.0)

clip.write_videofile("/Users/troyehuang/projectaria_client_sdk_samples/alex_alex_session/merge_output_volume_increased.mp4", audio_codec="aac")