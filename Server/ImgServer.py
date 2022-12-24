import json

import torch
from flask import Flask
from flask import request

from FacenetModel import Facenet
from SQL.InsertProcessor import insert_processor
from SQL.QueryProcessor import query_processor

facenet = Facenet()
app = Flask(__name__)


@app.route("/", methods=['GET', 'POST'])
def hello():
    return "Hello World!"


@app.route("/recognize", methods=['POST'])
def recognize():
    response = request.json
    rgb_frame = response["rgb_frame"]
    rgb_frame = json.loads(rgb_frame)
    rgb_frame = torch.tensor(rgb_frame).cuda().float()
    boxes, probs = facenet.face_detect(rgb_frame)
    # 人脸概率在0.5以上的保留
    boxes = [box for box, prob in zip(boxes, probs) if prob > 0.5]
    if boxes:  # 检测到人脸
        # 人脸图像
        images = facenet.boxes_to_images(rgb_frame, boxes)
        # 人脸特征
        embeddings_features = facenet.face_recognize(images)
        # 人脸识别
        ids, names = facenet.face_features_compare(embeddings_features)
        if ids:
            for id, name, image in zip(ids, names, images):
                insert_processor.store_face_recognized_record(
                    door_id=response["door_id"], direction=response["direction"],
                    result_id=id, image_data=image.numpy())
        return json.dumps([names, boxes])


@app.route("/register", methods=['POST'])
def register():
    response = request.json
    rgb_frame = response["rgb_frame"]
    rgb_frame = json.loads(rgb_frame)
    rgb_frame = torch.tensor(rgb_frame).cuda().float()
    boxes, probs = facenet.face_detect(rgb_frame)
    # 人脸概率在0.5以上的保留
    boxes = [box for box, prob in zip(boxes, probs) if prob > 0.5]
    boxes.sort()
    images = facenet.boxes_to_images(rgb_frame, boxes[-1:])
    embeddings_features = facenet.face_recognize(images)
    feature = embeddings_features[0]
    facenet.register_new_face(response["id"], response["name"], images[0], feature)
    return "register success"


@app.route("/door_record", methods=['POST'])
def door_record():
    response = request.json
    records = query_processor.query_record(
        response["door_id"], response["direction"], response["start_time"], response["end_time"])
    return json.dumps(records)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5555)