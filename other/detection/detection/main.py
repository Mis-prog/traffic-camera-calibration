from datetime import datetime

import numpy as np
import os
import cv2
import math
import m3u8
import urllib.request
import matplotlib.path as mplPath
import imutils

import requests
from ultralytics import YOLO




CURR_DIR = os.path.dirname(os.path.realpath(__file__))

online = True
model_path = os.path.join(CURR_DIR, r"best_8n_car_truck_van.onnx")
video_path = os.path.join(CURR_DIR, r"../data/move.mp4")

if online:
    html = requests.get('http://maps.ufanet.ru/ufa').text
    index_for_token = html.find("перекрёсток Карла Маркса - Свердлова")
    ttemp = html[index_for_token:index_for_token + 400]
    index_for_token = ttemp.find("marker.token = ")
    ttemp = ttemp[index_for_token:index_for_token + len("marker.token = 8314d794f6cc4620ae02fb62ef4163b2") + 1].split(
        "marker.token = ")[1][1:]
    playlist = "http://136.169.226.59/1-4/mono.m3u8?token=" + ttemp
    videoLink = os.path.dirname(playlist) + '/'

model = YOLO(model_path)

model.conf = 0.45
model.iou = 0.5


color_dict = {0: (0, 255, 0),
              1: (255, 175, 80),
              2: (0, 100, 255),
              3: (255, 215, 0),
              4: (255, 119, 182)
              }

colors_traffic = [
    (10, 10, 242),
    (10, 211, 242),
    (0, 247, 87),
    (243, 247, 0),
    (247, 103, 0),
    (247, 0, 169),
    (255, 255, 255)
]



def download_files(local_files):



    global playlist
    try:

        m3u8_obj = m3u8.load(playlist)

    except:
        html = requests.get('http://maps.ufanet.ru/ufa').text
        index_for_token = html.find("перекрёсток Карла Маркса - Свердлова")
        ttemp = html[index_for_token:index_for_token + 400]
        index_for_token = ttemp.find("marker.token = ")
        ttemp = \
            ttemp[index_for_token:index_for_token + len("marker.token = 8314d794f6cc4620ae02fb62ef4163b2") + 1].split(
                "marker.token = ")[1]
        playlist = "http://136.169.226.59/1-4/mono.m3u8?token=" + ttemp
        download_files(local_files)
        return

    ts_segments_str = str(m3u8_obj.segments)

    for line in ts_segments_str.splitlines():
        if ".ts" in line:
            server_file_path = os.path.join(videoLink, line)
            file_name = line[line.rfind('/') + 1:line.find('?')]
            local_file_path = os.path.join(CURR_DIR, "video_files", file_name)
            if not local_file_path in local_files:
                local_files.append(local_file_path)
                urllib.request.urlretrieve(server_file_path, local_file_path)

    return local_files


def onMouse(event, x, y, flags, param):
    # EVENT
    if event == cv2.EVENT_LBUTTONDOWN:
        print('x = %d, y = %d' % (x, y))


x_res, y_res = (1920, 1080)  # RESOLUTION
x_resized, y_resized = (1280, 720)  # NEW RESIZED RESOLUTION


pol5 = (785 , 586 )
pol1 = (10 , 684 )
pol2 = (10 , 1028 )
pol3 = (1124 , 1022 )
pol4 = (1359 , 929 )


polygon = np.array([pol5,pol4,pol3,pol2,pol1 ], dtype=int)  # points for polygone
poly_path = mplPath.Path(polygon)

traffic_lanes = np.array([[(10, 684), (10,857), (940, 713), (785, 586),(785, 586)],#так как в массиве np все строки  должны иметь
                          # одинаковую размерность,но одна из полос имеет 5 ключевых точек,то в ту,в которой только 4,
                          # продублировал последнюю
                          [(10, 857), (10,1028), (1124, 1022), (1359,929),(940,713)]], dtype=int)

traffic_lanes_path = [mplPath.Path(lane) for lane in traffic_lanes]

ids = [i for i in range(100, 0, -1)]

default_distance = 50  # euclid metric


def main():

    count = 0
    tracking_objects = {}

    if online:
        local_files = download_files([])
        del_file = None


    while True:
        if online:
            if len(local_files) == 0:
                local_files = download_files([])
            local_file = local_files[0]

            cap = cv2.VideoCapture(local_file)

            if del_file:
                os.remove(del_file)

        else:
            cap = cv2.VideoCapture(video_path)

        lane_count = {i: [0]*3 for i in range(len(traffic_lanes_path))}#пока здесь 3,так как классов 3,0-машина,1-грузовик,и 2 фургон(van),и у каждого свое порядковое место


        file_frames = 0
        while cap.isOpened():

            ret, frame = cap.read()

            if type(frame) == type(None):
                break

            frame = imutils.resize(frame, width=1920, height=1080)
            file_frames += 1
            if file_frames == 1: continue

            if ret == True:



                count += 1

                results = model(frame)




                image = frame.copy()
                boxes=results[0].boxes
                boxes=[box for box in boxes]
                for box in boxes:

                    cx = int(box.xywh[0][0])
                    cy =int(box.xywh[0][1])



                    if int(box.cls)-1 != 2 and poly_path.contains_point((cx, cy)):

                        image = cv2.rectangle(frame, (int(box.xyxy[0][0]),int(box.xyxy[0][1])),(int(box.xyxy[0][2]),int(box.xyxy[0][3])), color_dict[int(box.cls)-1],
                                              2)  # object rectangle





                image = cv2.polylines(image, [polygon.reshape((-1, 1, 2))], True, (255, 4, 0), 2)

                for k, lane in enumerate(traffic_lanes):
                    image = cv2.polylines(image, [lane.reshape((-1, 1, 2))], True, colors_traffic[k], 2)



                if True:

                    tracking_objects_copy=tracking_objects.copy()# так как итерация по оригиналу словаря может быть затруднена так как из него удаляют динамически элементы
                    for object_id, (pt2, cls2, vector_speed, useless) in tracking_objects_copy.items():
                        if useless > 3:
                            for k, traffic_lane in enumerate(traffic_lanes_path): #добавить объект в список уже проехавших только когда он перестанет определяться.
                                # тогда же необходимо просмотреть,с какой полосы он ушел и увеличить датчик проехавших по ней на 1
                                if traffic_lane.contains_point((pt2[0], pt2[1])):

                                    lane_count[k][cls2] += 1
                                    break
                            tracking_objects.pop(object_id)
                            ids.append(object_id)
                            continue
                        object_exists = False
                        for box in boxes:

                            distance = math.hypot(pt2[0] + vector_speed[0] * (useless + 1) - box.xywh[0][0],
                                                  pt2[1] + vector_speed[1] * (useless + 1) - box.xywh[0][1])

                            # Update IDs positions
                            if distance < default_distance:

                                tracking_objects[object_id] = (box.xywh[0][0],box.xywh[0][1]),int(box.cls)-1, [box.xywh[0][0] - pt2[0],
                                                                                         box.xywh[0][1] - pt2[1]], 0

                                object_exists = True

                                boxes.remove(box)
                                break
                        if not object_exists:
                            tracking_objects[object_id] = pt2,cls2, vector_speed, useless + 1

                    # Add new IDs found
                    for box in boxes:
                        tracking_objects[ids[-1]] = (box.xywh[0][0],box.xywh[0][1]), int(box.cls)-1, [0, 0], 0
                        ids.pop()






                for i in range(len(traffic_lanes_path)):
                    image = cv2.putText(image, f"lane {i} count cars: {lane_count[i][0]} trucks: {lane_count[i][1]}" , (20, 100 + i * 50),
                                        cv2.FONT_HERSHEY_SIMPLEX, 1.5, colors_traffic[i], 2)

                image = cv2.resize(image, (x_resized, y_resized), interpolation=cv2.INTER_AREA)



                cv2.imshow('frame', image)
                cv2.namedWindow('frame')
                cv2.setMouseCallback('frame', onMouse)

                if cv2.waitKey(1) == ord('q'):

                    cap.release()
                    cv2.destroyAllWindows()
                        #в файле день сохранения
                    my_file = open("count_on_lines_"+datetime.now().__str__().split(" ")[0]+".txt", "w+")
                    for i in range(len(traffic_lanes_path)):
                        my_file.write(f"lane {i} count cars: {lane_count[i][0]} trucks: {lane_count[i][1]} \n")
                    my_file.close()
                    return

            else:
                break
        # if not online:
        #     # my_file = open("count_on_lines" + datetime.now().__str__() + ".txt", "w+")
        #     # for i in range(len(traffic_lanes_path)):
        #     #     my_file.write(f"lane {i} count cars: {lane_count[i][0]} trucks: {lane_count[i][1]} \n")
        #     # my_file.close()
        #     # break

        # if online:
        #     del_file = local_file
        #     local_files.pop(0)
        #     local_files = download_files(local_files)



main()

