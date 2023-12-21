# Up Scaling Video
## Phase 1: Dataset Creation
- Downloading videos from YouTube in 1080p and 480p
- Splitting videos in frame with ffmpeg, one frame per second
- Copy frames in a good format for training

## Phase 2: Model Training (v2)
- Buffer images with the Tensorflow model
- Create a model which fit in AWS instances
- Train the model
- Test the model
  - Split a full video in frame
  - Predict the high resolution of all images
  - Merge predicted images
