# Human-Human-Collaboration-Dataset

## Supervisors
Alexey Gavryushin, Xi Wang

## Authors
Dingxi Zhang, Jingyuan Li, Peiyu Liu, Zhao Huang

## Description
The idea of the project is to collect an egocentric video dataset that captures real-world, goal-oriented human collaboration, such as cooking or assembling furniture, recorded using Aria glasses. This dataset aims to highlight collaborative nuances, including goal-directed communication, object manipulation, handovers, gestures, and complex interaction dynamics. A key innovation is the multi-perspective recording, enabling analysis of how sensory perceptions and goals are shared and coordinated. By integrating multiple modalities, such as high-quality audio, gaze tracking, and camera poses, the dataset will provide a comprehensive foundation for studying unscripted, everyday collaborative tasks.

Due to time constraints, the dataset recording was limited to sample recordings, and all analysis and research were conducted based on the sample dataset.


## Demo Video
Watch our demo [here](https://drive.google.com/file/d/1IA7z-bVj_ICkt2waLHLmhnHb4-S0ceKt/view?usp=sharing).

## Report
Our project report : [Human-Human-Collaboration-Dataset Report](Report/Human-Collaboration-Dataset.pdf).

## Dataset Sample

The dataset sample could be accessed [here](https://drive.google.com/drive/folders/1bIRUw3rXNFYa44ZWabUg5g3bOMronBiP?usp=sharing). 

## Installation Guide

#### Install the required Python packages for Project Aria Tools
```
python3 -m pip install --upgrade pip

python3 -m pip install projectaria-tools'[all]'
```

#### Install Project Aria Tools for C++ (Ubuntu)
**Step 0: Download codebase**
```
mkdir -p $HOME/Documents/projectaria_sandbox
cd $HOME/Documents/projectaria_sandbox

git clone https://github.com/facebookresearch/projectaria_tools.git -b 1.5.6
```
**Step 1: Install dependencies**
```
# Install build essentials
sudo apt install build-essential git cmake

# Install VRS/Pangolin dependencies
sudo apt install libgtest-dev libgmock-dev libgoogle-glog-dev libfmt-dev \
liblz4-dev libzstd-dev libxxhash-dev libboost-all-dev libpng-dev \
libjpeg-turbo8-dev libturbojpeg0-dev libglew-dev libgl1-mesa-dev libeigen3-dev
```
**Step 2: Compile C++ source code**
```
cd $HOME/Documents/projectaria_sandbox

mkdir -p build && cd build

# compile the C++ API
cmake ../projectaria_tools/

make -j2
```
**Step 3: Compile Pangolin**    
```
# compile & install Pangolin
cd /tmp

git clone --recursive https://github.com/stevenlovegrove/Pangolin.git

mkdir -p Pangolin_Build && cd Pangolin_Build

cmake -DCMAKE_BUILD_TYPE=Release -DBUILD_TOOLS=OFF -DBUILD_PANGOLIN_PYTHON=OFF \
-DBUILD_EXAMPLES=OFF ../Pangolin/

make -j2

sudo make install
```
**Step 4: Build projectaria_tools with visualization**
```
cd $HOME/Documents/projectaria_sandbox

mkdir -p build && cd build

# Build C++ Aria Viewer
cmake ../projectaria_tools -DPROJECTARIA_TOOLS_BUILD_TOOLS=ON

make -j2
```
**Step 5: Verify installation by running the viewer**
```
cd $HOME/Documents/projectaria_sandbox/build

# Running the Aria Viewer with example data
./tools/visualization/aria_viewer \
--vrs $VRS_SAMPLE_PATH/sample.vrs
```

For more details, please check [Project Aria Doc](https://facebookresearch.github.io/projectaria_tools/docs/intro)
## Repository Structure

* **Script**: This folder contains all the code for data processing.
    * **sync_utils**
        * **sync_rerun_play.py**: The python script used to play synchronized VRS files from two perspectives in rerun application.
        * **sync_frames_display.py** The python script used to plot the synchornized frames.
        * **vrs_sync_to_mp4.py** The python script used to combine two-perspective VRS files into a single MP4 file.
        * **vrs_sync_to_mp4_utils.py** The file contains the helper functions that used in *vrs_sync_to_mp4.py*.
        * **projectaria_tools** This folder contains other utility functions provided by project aria.

## Acknowledgement

We would like to express our deepest gratitude to the following individuals and organizations whose support, tools, and guidance made this project possible:

- [Project Aria](https://facebookresearch.github.io/projectaria_tools/) for providing Aria glasses and the accompanying utility functions.
- Our course advisor([MixedRealityETHZ Team](https://github.com/MixedRealityETHZ)), project supervisiors 
- Our teammates and collaborators for their contributions to the design and implementation of the project.
- The research participants who contributed to our dataset collection by engaging in the collaboration tasks.









