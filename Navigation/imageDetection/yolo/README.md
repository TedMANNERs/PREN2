# YOLO v3
The following fork of darknet was used:
https://github.com/AlexeyAB/darknet#how-to-train-tiny-yolo-to-detect-your-custom-objects

## How to train a model?
1. Clone the above repository
2. Build it (Use the instructions in the repsitory. This is the most difficult step and has many pitfalls.)
3. Put labeled images (jpg + txt) into the "train/" directory (Create it if it does not exist)
4. Change directory to "train/"
5. Run "prepare_yolo_train_data.py" to split the images into a training and a validation set
6. Download "yolov3-tiny.conv.15" (Check description of darknet repository)
7. Run "darknet.exe detector train *"path to pylon.data"* *"path to yolov3-tiny-pylon.cfg"* *"path to yolov3-tiny.conv.15"*" to start training


## More commands
* Detect objects in image:*darknet.exe detect yolov3-tiny-pylon.cfg backup/yolov3-tiny-pylon_final.weights "pylon (6).jpg"*
* Test: *darknet.exe detector test pylon.data yolov3-tiny-pylon.cfg backup/yolov3-tiny-pylon_final.weights "pylon (6).jpg"*
* Detect objects in video and save it: *darknet.exe detector demo pylon.data yolov3-tiny-pylon.cfg backup/yolov3-tiny-pylon_13000.weights input-video.mp4 -out_filename test_drive.mp4*
