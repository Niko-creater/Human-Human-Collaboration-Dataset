import whisper
import os
import json

input_audio = "data/extracted_audio.wav"
out_dir = "output"
output_file = input_audio.split("/")[-1].replace(".wav", ".json")

model = whisper.load_model("turbo")

# load audio and pad/trim it to fit 30 seconds
audio = whisper.load_audio(input_audio)
audio = whisper.pad_or_trim(audio)

# make log-Mel spectrogram and move to the same device as the model
mel = whisper.log_mel_spectrogram(audio, n_mels=model.dims.n_mels).to(model.device)

# detect the spoken language
_, probs = model.detect_language(mel)
print(f"Detected language: {max(probs, key=probs.get)}")

# # decode the audio
# options = whisper.DecodingOptions()
# result = whisper.decode(model, mel, options)

# # print the recognized text
# print(result.text)

result = model.transcribe(input_audio, language="en", verbose=True)
print(result["text"])

json_path = os.path.join(out_dir, output_file)
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
print(f"Saved full JSON to {json_path}")