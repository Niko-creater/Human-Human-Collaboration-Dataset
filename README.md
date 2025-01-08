# Human-Human-Collaboration-Dataset

## Supervisors
Alexey Gavryushin, Xi Wang

## Authors
Dingxi Zhang, Jingyuan Li, Peiyu Liu, Zhao Huang

## Description
The idea of the project is to collect an egocentric video dataset that captures real-world, goal-oriented human collaboration, such as cooking or assembling furniture, recorded using Aria glasses. This dataset aims to highlight collaborative nuances, including goal-directed communication, object manipulation, handovers, gestures, and complex interaction dynamics. A key innovation is the multi-perspective recording, enabling analysis of how sensory perceptions and goals are shared and coordinated. By integrating multiple modalities, such as high-quality audio, gaze tracking, and camera poses, the dataset will provide a comprehensive foundation for studying unscripted, everyday collaborative tasks.

Notice that due to time constraints, the dataset recording has not yet entered the formal stage, and all analysis and research are focused on the sample dataset.


## Demo Video
Watch our demo [here](https://drive.google.com/file/d/1IA7z-bVj_ICkt2waLHLmhnHb4-S0ceKt/view?usp=sharing).

## Report

Our project report : [Human-Human-Collaboration-Dataset Report](Report/Human-Collaboration-Dataset.pdf).

## Dataset Sample

The sample dataset could be accessed here.

## Repository Structure

* **Script**
    * **sync_utils**
        * **sync_rerun_play.py**: The python script used to play synchronized VRS files from two perspectives in rerun application.
        * **sync_frames_display.py** The python script used to plot the synchornized frames.
        * **vrs_sync_to_mp4.py** The python script used to combine two-perspective VRS files into a single MP4 file.
        * **vrs_sync_to_mp4_utils.py** The file contain the helper functions that used in *vrs_sync_to_mp4.py*.








