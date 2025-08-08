from moviepy.editor import VideoFileClip, AudioFileClip

clip = VideoFileClip("/Users/troyehuang/projectaria_client_sdk_samples/test_sync_mp4/b.mp4")

clip = clip.volumex(10.0)

clip.write_videofile("/Users/troyehuang/projectaria_client_sdk_samples/test_sync_mp4/b_increased.mp4", audio_codec="aac")