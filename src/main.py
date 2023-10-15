import os
import sys
import webbrowser
import requests
import concurrent.futures
import cv2
import numpy as np

from PyQt5 import QtCore, QtGui, uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox, QDialog
from PyQt5.QtCore import Qt, QThread, pyqtSignal, PYQT_VERSION_STR
from PyQt5.QtGui import QIcon

import torch
import torchvision


file_path = os.path.dirname(os.path.abspath(__file__))

form_class = uic.loadUiType(file_path + "\\main_ui.ui")[0]
running_a = False
running_b = False
running_c = False
running_d = False

length = {2: [], 7: [], 8: [], 9: []}


"""
falko에 관한 정보 제공
"""
class FalkoInfoWindow(QDialog):
    def __init__(self, parent):
        super(FalkoInfoWindow, self).__init__(parent)
        uic.loadUi(file_path+"\\falko_info.ui", self)
        self.show()
        self.setWindowIcon(QIcon('falko.jpg'))
        self.setWindowTitle("falko Information")
        pixmap = QtGui.QPixmap("falko.jpg")
        scaled_pixmap = pixmap.scaled(1.3 * pixmap.width(), 1.3 * pixmap.height())
        self.label.setPixmap(scaled_pixmap)
        self.label.setGeometry(30, 35, 1.3 * pixmap.width(), 1.3 * pixmap.height())
        self.stop.clicked.connect(self.close)


"""
좌석 위치 정보 불러오기
"""
class SeatSettingsWindow(QDialog):
    def __init__(self, parent):
        super(SeatSettingsWindow, self).__init__(parent)
        uic.loadUi(file_path+"\\seat_settings.ui", self)
        self.show()
        self.setWindowIcon(QIcon('falko.jpg'))
        self.setWindowTitle("Seat Setting")
        self.load_settings()

        self.a_seat_info = parent.a_seat_info
        self.b_seat_info = parent.b_seat_info
        self.c_seat_info = parent.c_seat_info
        self.d_seat_info = parent.d_seat_info

        self.Load_A.clicked.connect(self.file_load)
        self.Load_B.clicked.connect(self.file_load)
        self.Load_C.clicked.connect(self.file_load)
        self.Load_D.clicked.connect(self.file_load)
        self.finish.clicked.connect(self.dialog_close)

    #사용자가 설정한 좌석 정보 저장
    def save_settings(self):
        settings = QtCore.QSettings("MyApp", "SeatSettingsWindow")
        settings.setValue("A_file_text", self.A_file.toPlainText())
        settings.setValue("B_file_text", self.B_file.toPlainText())
        settings.setValue("C_file_text", self.C_file.toPlainText())
        settings.setValue("D_file_text", self.D_file.toPlainText())

    #창이 켜지면 사용자가 이전에 선택한 좌석 정보를 자동으로 세팅
    def load_settings(self):
        settings = QtCore.QSettings("MyApp", "SeatSettingsWindow")
        self.A_file.setText(settings.value("A_file_text", ""))
        self.B_file.setText(settings.value("B_file_text", ""))
        self.C_file.setText(settings.value("C_file_text", ""))
        self.D_file.setText(settings.value("D_file_text", ""))

    #'파일 열기'를 통해 사용자가 지정한 좌석 정보 파일을 세팅
    def file_load(self):
        sender_button = self.sender() 

        fname = QFileDialog.getOpenFileName(self)
        if sender_button == self.Load_A:
            self.A_file.setText(fname[0])
        elif sender_button == self.Load_B:
            self.B_file.setText(fname[0])
        elif sender_button == self.Load_C:
            self.C_file.setText(fname[0])
        elif sender_button == self.Load_D:
            self.D_file.setText(fname[0])
        self.save_settings()

    #창이 꺼지면 사용자가 지정한 좌석 정보를 리스트에 복사
    def dialog_close(self):
        seat_info = {
            self.A_file.toPlainText(): self.a_seat_info,
            self.B_file.toPlainText(): self.b_seat_info,
            self.C_file.toPlainText(): self.c_seat_info,
            self.D_file.toPlainText(): self.d_seat_info
        }
        for file_name, seat_dict in seat_info.items():
            seat_dict.clear()
            file_name = os.path.basename(file_name)
            with open(file_name, 'r') as file:
                for line in file:
                    line = line.strip()
                    if line:
                        key, value = line.split(':')
                        if 'a' in file_name[0]:
                            self.a_seat_info[key.strip()] = eval(value.strip())
                        elif 'b' in file_name[0]:
                            self.b_seat_info[key.strip()] = eval(value.strip())
                        elif 'c' in file_name[0]:
                            self.c_seat_info[key.strip()] = eval(value.strip())
                        elif 'd' in file_name[0]:
                            self.d_seat_info[key.strip()] = eval(value.strip())
        self.accept()

"""
YOLO를 통해 좌석을 인식하여 좌석 위치 정보를 텍스트 파일로 저장
"""
class SeatCaptureWindow(QDialog):
    def __init__(self, parent):
        super(SeatCaptureWindow, self).__init__(parent)
        uic.loadUi(file_path+"\\seat_capture.ui", self)
        self.show()
        self.setWindowIcon(QIcon('falko.jpg'))
        self.setWindowTitle("Seat Capture")

        self.search_file.clicked.connect(self.file_load)
        self.a_button.clicked.connect(self.process_video)
        self.b_button.clicked.connect(self.show_seat)
        self.c_button.clicked.connect(self.show_seat)
        self.d_button.clicked.connect(self.show_seat)
        self.finish.clicked.connect(self.close)

    """
    1. 좌석을 인식한 후 A1부터 열대로 좌석 번호를 라벨링
    2. 이후 인식한 좌석 정보를 텍스트 파일로 저장
    """
    def process_video(self):
        #YOLO 모델 불러오기
        model = torch.hub.load('ultralytics/yolov5', 'yolov5s')  #  P6 model
        # results = model(imgs, size=1280)  # inference at 1280

        self.a_seat_info = {}
        cam = cv2.VideoCapture(0)
        ret, frame = cam.read()

        cv2.imwrite(file_path+'\\seat.jpg', frame, params=[cv2.IMWRITE_PNG_COMPRESSION, 0])
        cam.release()
        # img = cv2.imread(file_path+"\\seat.jpg")
        # height, width, channels = img.shape

        boxes = []

        results = model(frame)

        # 좌석 클래스에 해당하는 객체 추출
        pred = results.pred[0]
        seat_results = pred[pred[:, 5] == 56]
        seat_boxes = seat_results[:, :4]
        seat_scores = seat_results[:, 4]
        
        # 중복 박스 제거 (NMS 적용)
        keep = torchvision.ops.nms(seat_boxes, seat_scores, iou_threshold=0.5)
        seat_boxes = seat_boxes[keep]
        seat_scores = seat_scores[keep]

        for i, box in enumerate(seat_boxes):
            x1, y1, x2, y2 = box.int()
            w = x2 - x1
            h = y2 - y1
            boxes.append([x1, y1, w, h])

        centers = [(i, int(box[0] + box[2]/2), int(box[1] + box[3]/2)) for i, box in enumerate(boxes)]

        """
        인식한 좌석 라벨링
        """
        num_cols = 0
        sorted_centers = []
        cnt = 1

        for i, center in enumerate(sorted(centers, key=lambda x: (-x[2], x[1]))):
            if i == 0 or center[2] < sorted_centers[i-1][2] - 100:
                num_cols += 1
            sorted_centers.append([center[0], center[1], center[2], num_cols])

        row_sorted = sorted(sorted_centers, key=lambda x: (x[3], x[1]))

        for i, center in enumerate(row_sorted):
            if i == 0 or (center[2] < row_sorted[i-1][2] - 100 and center[3] != row_sorted[i-1][3]):
                cnt = 1
            row_sorted[i].append(cnt)
            cnt += 1

        i = 0
        for center in row_sorted:
            seat_num = chr(64 + center[3])+str(center[4])
            boxes[center[0]].append(seat_num)

        for i in range(len(boxes)):
            x, y, w, h, s_num = boxes[i]
            (startX, startY) = x, y
            self.a_seat_info[s_num] = [startX, startY, w, h]

        a_sorted_seats = sorted(self.a_seat_info.keys(), key=lambda x: (x[0], int(x[1:])))
        self.seat_info.setText(" ".join(a_sorted_seats))

        fname = self.file_name.toPlainText()
        a_file_path = os.path.join(fname, "a_seat_information.txt")

        with open(a_file_path, 'w') as file:
            for key, value in self.a_seat_info.items():
                file.write(f'{key}: {value}\n')

    #미리 설정된 B, C, D 카메라 공간 내 좌석 정보를 띄움.
    def show_seat(self):
        sender_button = self.sender()
        b_seat_numbers = []
        c_seat_numbers = []
        d_seat_numbers = []

        if sender_button == self.b_button:
            self.file_name_text = self.file_name.toPlainText()
            b_file_path = os.path.join(self.file_name_text, "b_seat_information.txt")
            with open(b_file_path, 'r') as file:
                for line in file:
                    line = line.strip()
                    if line:
                        seat_number, _ = line.split(':')
                        b_seat_numbers.append(seat_number.strip())
            b_sorted_seats = sorted(b_seat_numbers, key=lambda x: (x[0], int(x[1:])))
            self.seat_info.setText(" ".join(b_sorted_seats))
        elif sender_button == self.c_button:
            self.file_name_text = self.file_name.toPlainText()
            c_file_path = os.path.join(self.file_name_text, "c_seat_information.txt")
            with open(c_file_path, 'r') as file:
                for line in file:
                    line = line.strip()
                    if line:
                        seat_number, _ = line.split(':')
                        c_seat_numbers.append(seat_number.strip())
            c_sorted_seats = sorted(c_seat_numbers, key=lambda x: (x[0], int(x[1:])))
            self.seat_info.setText(" ".join(c_sorted_seats))
        elif sender_button == self.d_button:
            self.file_name_text = self.file_name.toPlainText()
            d_file_path = os.path.join(self.file_name_text, "d_seat_information.txt")
            with open(d_file_path, 'r') as file:
                for line in file:
                    line = line.strip()
                    if line:
                        seat_number, _ = line.split(':')
                        d_seat_numbers.append(seat_number.strip())
            d_sorted_seats = sorted(d_seat_numbers, key=lambda x: (x[0], int(x[1:])))
            self.seat_info.setText(" ".join(d_sorted_seats))

    #좌석 정보 파일을 저장할 경로 선택
    def file_load(self):
        fname = QFileDialog.getExistingDirectory(self, "폴더 선택", "", QFileDialog.ShowDirsOnly)
        self.file_name.setText(fname)

"""
영상처리 스레드
"""
class Worker(QThread):
    finished = pyqtSignal()

    def __init__(self, seat_info, camera_number, camera_label, seat_num_label, display_num, res_cnt, p_cnt):
        super().__init__()
        self.seat_info = seat_info
        self.camera_number = camera_number
        self.camera_label = camera_label
        self.seat_num_label = seat_num_label
        self.display_num = display_num
        self.res_cnt = res_cnt
        self.p_cnt = p_cnt
        self.running = False
        self.cap = None

        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=3)
        self.net = torch.hub.load('ultralytics/yolov5', 'yolov5s')
        # self.net = cv2.dnn.readNet("yolov3.weights", "yolov3.cfg")
        # self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
        # self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)
        # self.layer_names = self.net.getLayerNames()
        # self.output_layers = [self.layer_names[i - 1] for i in self.net.getUnconnectedOutLayers()]

        self.reserved_seat = ['A1', 'B2']  #임시
    
    #스레드 시작
    def start(self):
        self.running = True
        self.run()

    #스레드 시작
    def stop(self):
        self.running = False

    #스레드 실행
    def run(self):

        self.running = True
        self.cap = cv2.VideoCapture(self.camera_number)
        frame_num = {seat_num: 0 for seat_num in self.seat_info}
        frame_interval = 3

        while self.running:
            # self.reserved_seat = self.call_api(self.display_num)
            self.res_cnt.setText(str(len(self.reserved_seat)) + "    ")
            ret, frame = self.cap.read()

            if not ret:
                break
            if self.camera_number != 1:
                if self.cap.get(cv2.CAP_PROP_POS_FRAMES) % frame_interval != 0:
                    continue
            people_future = self.executor.submit(self.detect_people, frame, self.p_cnt)
            seats_future = self.executor.submit(self.detect_seats, frame, people_future.result(), frame_num, self.seat_info, self.reserved_seat)
            people_result = people_future.result()
            seat_people_real = seats_future.result()

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, c = frame.shape
            qImg = QtGui.QImage(frame.data, w, h, w * c, QtGui.QImage.Format_RGB888)
            pixmap = QtGui.QPixmap.fromImage(qImg)
            p = pixmap.scaled(self.camera_label.size(), aspectRatioMode=Qt.KeepAspectRatio, transformMode=Qt.SmoothTransformation)
            self.camera_label.setPixmap(p)
            self.camera_label.setScaledContents(True)

        self.cap.release()
        self.camera_label.setPixmap(QtGui.QPixmap())
        self.seat_num_label.setText(" ")
        self.finished.emit()

    #이미지 라벨 크기 이벤트 발생 감지
    def resizeEvent(self, event):
        self.update_label_size()
        super().resizeEvent(event)

    #변화한 이미지 라벨 크기에 맞춰 영상 크기 조정
    def update_label_size(self):
        pixmap = self.camera_label.pixmap()
        if pixmap:
            scaled_pixmap = pixmap.scaled(self.camera_label.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.SmoothTransformation)
            if scaled_pixmap.size().width() > pixmap_size.width() or scaled_pixmap.size().height() > pixmap_size.height():
                scaled_pixmap = pixmap.scaled(pixmap_size, Qt.AspectRatioMode.KeepAspectRatio, Qt.SmoothTransformation)
            self.camera_label.setPixmap(scaled_pixmap)

    #YOLO를 이용하여 frame 내 사람 객채들을 인식한 후, 사람 객체 좌표 반환
    def detect_people(self, frame, p_cnt):

        height, width = frame.shape[:2]

        class_ids = []
        confidences = []
        boxes = []

        results = self.net(frame)
        # 좌석 클래스에 해당하는 객체 추출
        pred = results.pred[0]
        seat_results = pred[pred[:, 5] == 56]
        seat_boxes = seat_results[:, :4]
        seat_scores = seat_results[:, 4]
        
        # 중복 박스 제거 (NMS 적용)
        keep = torchvision.ops.nms(seat_boxes, seat_scores, iou_threshold=0.5)
        seat_boxes = seat_boxes[keep]
        seat_scores = seat_scores[keep]

        for i, box in enumerate(seat_boxes):
            x1, y1, x2, y2 = box.int()
            w = x2 - x1
            h = y2 - y1
            boxes.append([x1, y1, w, h])

        people_coordinate = []
        for i in range(len(boxes)):
            if i in indexes:
                x, y, w, h = boxes[i]
                people_coordinate.append([x, y, w, h])

        p_cnt.setText(str(len(people_coordinate)) + "    ")
        return people_coordinate
    
    """
    1. 사람 객체와 좌석 객체의 영역이 겹치는 지 확인
    2. 사람이 앉은 좌석 중 예약되지 않은 좌석을 빨간 박스로 표시 및 좌석 번호 띄움.
    """
    def detect_seats(self, frame, people_result, frame_num, seat_info, reserved_seat):
        seat_people_real = []
        p_true = {seat_num: {} for seat_num in seat_info}

        for p_coord in people_result:
            for seat_num, s_coord in self.seat_info.items():  
                x1 = max(s_coord[0], p_coord[0])
                y1 = max(s_coord[1], p_coord[1])
                x2 = min(s_coord[0] + s_coord[2], p_coord[0] + p_coord[2])
                y2 = min(s_coord[1] + s_coord[3], p_coord[1] + p_coord[3])

                w = x2 - x1
                h = y2 - y1

                area = w * h
                if area >= 0.7 * s_coord[2] * s_coord[3]:
                    frame_num[seat_num] += 1
                    p_true[seat_num] = p_coord
                    continue

        for seat_num in seat_info.keys():
            if (p_true[seat_num] == {} and frame_num[seat_num] > 10):
                frame_num[seat_num] = 0
                continue

        for s_num, f_num in frame_num.items():
            if f_num > 10:
                if s_num in seat_people_real:
                    continue
                else:
                    seat_people_real.append(s_num)

        self.seat_num_label.setText(" ")
        for i in range(len(seat_people_real)):
            if seat_people_real[i] not in reserved_seat:
                cv2.rectangle(frame, (seat_info[seat_people_real[i]][0], seat_info[seat_people_real[i]][1]),
                                    (seat_info[seat_people_real[i]][0] + seat_info[seat_people_real[i]][2],
                                        seat_info[seat_people_real[i]][1] + seat_info[seat_people_real[i]][3]), (0, 0, 255), 2)
                self.seat_num_label.setText(seat_people_real[i] + "  ")

    #데이터베이스에서 예매 좌석 번호불러오기
    def call_api(self, num):
        url = "http://eanemovie.shop/api/seats"
        response = requests.get(url)

        tmp = {2: [], 7: [], 8: [], 9: []}

        global length
        if response.status_code == 200:
            seats = response.json()
            for i, seat in enumerate(seats):
                schedule = seat['scheduleId']

                if schedule == 2 and num == 2:
                    tmp[2].append(seat["number"])
                elif schedule == 7 and num == 7:
                    tmp[7].append(seat["number"])
                elif schedule == 8 and num == 8:
                    tmp[8].append(seat["number"])
                elif schedule == 9 and num == 9:
                    tmp[9].append(seat["number"])

            if (length[num] != len(tmp[num])):
                length[num] = len(tmp[num])

            return tmp[num]

        else:
            print("API 호출에 실패하였습니다.")

"""
메인 화면 / 4개의 카메라 공간에서 무단 착석 감지가 이루어짐.
"""
class MainWindow(QMainWindow, form_class):

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("falko")

        self.mainLayout_AB.setSpacing(0)
        self.mainLayout_CD.setSpacing(0)

        self.mainLayout_AB.addWidget(self.A_widget)
        self.mainLayout_AB.addWidget(self.B_widget)
        self.mainLayout_CD.addWidget(self.C_widget)
        self.mainLayout_CD.addWidget(self.D_widget)
        self.setWindowIcon(QIcon('falko.jpg'))

        self.a_seat_info = {}
        self.b_seat_info = {}
        self.c_seat_info = {}
        self.d_seat_info = {}

        self.worker_a = None
        self.worker_b = None
        self.worker_c = None
        self.worker_d = None
        self.thread_a = None
        self.thread_b = None
        self.thread_c = None
        self.thread_d = None

        self.reserved_seat = []

        self.actionSeat_Setting.triggered.connect(self.seat_set)
        self.actionSeat_capture.triggered.connect(self.seat_capture)

        self.A_on.clicked.connect(self.a_video_start)
        self.A_off.clicked.connect(self.a_video_stop)

        self.B_on.clicked.connect(self.b_video_start)
        self.B_off.clicked.connect(self.b_video_stop)

        self.C_on.clicked.connect(self.c_video_start)
        self.C_off.clicked.connect(self.c_video_stop)

        self.D_on.clicked.connect(self.d_video_start)
        self.D_off.clicked.connect(self.d_video_stop)

        self.actionQuit.triggered.connect(self.close)
        self.actionSave.triggered.connect(self.save)
        self.actionJoin_Us_on_Git.triggered.connect(self.go_git)
        self.actionfalko_Information.triggered.connect(self.falko_info)

    #A 카메라 켜기
    def a_video_start(self, timer):
        if self.a_seat_info:
            self.A_on.setEnabled(False)
            self.A_on.setStyleSheet("color: white;" "background-color:#646464")
            self.A_off.setStyleSheet("color: white;" "background-color: #B60000")
            self.worker_a = Worker(self.a_seat_info, 1, self.a_camera_label, self.a_seat_num, 2, self.A_res_cnt, self.A_peo_cnt)
            self.thread_a = QThread()
            self.worker_a.moveToThread(self.thread_a)

            self.worker_a.finished.connect(self.worker_a.deleteLater)
            self.worker_a.finished.connect(self.thread_a.quit)
            self.thread_a.started.connect(self.worker_a.run)

            self.thread_a.start()
        else:
            QMessageBox.information(self, 'No Seat Informaion', 'Please Setting your A seat information.')

    #A 카메라 끄기
    def a_video_stop(self):
        if self.worker_a:
            self.A_on.setEnabled(True)
            self.A_off.setStyleSheet("color: white;" "background-color:#646464")
            self.A_on.setStyleSheet("color: white;" "background-color: #005F00")
            self.worker_a.stop()
            self.thread_a.quit()
            self.thread_a.wait()
            self.worker_a = None
            self.thread_a = None

            self.A_res_cnt.setText("0    ")
            self.A_peo_cnt.setText("0    ")

    #B 영상 켜기
    def b_video_start(self):
        if self.b_seat_info:
            self.B_on.setEnabled(False)
            self.B_on.setStyleSheet("color: white;" "background-color:#646464")
            self.B_off.setStyleSheet("color: white;" "background-color: #B60000")
            self.worker_b = Worker(self.b_seat_info, 'B.mp4', self.b_camera_label, self.b_seat_num, 7, self.B_res_cnt, self.B_peo_cnt)
            self.thread_b = QThread()
            self.worker_b.moveToThread(self.thread_b)

            self.worker_b.finished.connect(self.worker_b.deleteLater)
            self.worker_b.finished.connect(self.thread_b.quit)
            self.thread_b.started.connect(self.worker_b.run)

            self.thread_b.start()
        else:
            QMessageBox.information(self, 'No Seat Informaion', 'Please Setting your B seat information.')

    #B 영상 끄기
    def b_video_stop(self):
        if self.thread_b:
            self.B_on.setEnabled(True)
            self.B_off.setStyleSheet("color: white;" "background-color:#646464")
            self.B_on.setStyleSheet("color: white;" "background-color: #005F00")
            self.worker_b.stop()
            self.thread_b.quit()
            self.thread_b.wait()
            self.worker_b = None
            self.thread_b = None

            self.B_res_cnt.setText("0    ")
            self.B_peo_cnt.setText("0    ")
    
    #C 영상 켜기
    def c_video_start(self):
        if self.c_seat_info:
            self.C_on.setEnabled(False)
            self.C_on.setStyleSheet("color: white;" "background-color:#646464")
            self.C_off.setStyleSheet("color: white;" "background-color: #B60000")
            self.worker_c = Worker(self.c_seat_info, 'C.mp4', self.c_camera_label, self.c_seat_num, 8, self.C_res_cnt, self.C_peo_cnt)
            self.thread_c = QThread()
            self.worker_c.moveToThread(self.thread_c)

            self.worker_c.finished.connect(self.worker_c.deleteLater)
            self.worker_c.finished.connect(self.thread_c.quit)
            self.thread_c.started.connect(self.worker_c.run)

            self.thread_c.start()

        else:
            QMessageBox.information(self, 'No Seat Informaion', 'Please Setting your C seat information.')

    #C 영상 끄기
    def c_video_stop(self):
        if self.thread_c:
            self.C_on.setEnabled(True)
            self.C_off.setStyleSheet("color: white;" "background-color:#646464")
            self.C_on.setStyleSheet("color: white;" "background-color: #005F00")
            self.worker_c.stop()
            self.thread_c.quit()
            self.thread_c.wait()
            self.worker_c = None
            self.thread_c = None

            self.C_res_cnt.setText("0    ")
            self.C_peo_cnt.setText("0    ")

    #D 영상 켜기
    def d_video_start(self):
        if self.d_seat_info:
            self.D_on.setEnabled(False)
            self.D_on.setStyleSheet("color: white;" "background-color:#646464")
            self.D_off.setStyleSheet("color: white;" "background-color: #B60000")
            self.worker_d = Worker(self.d_seat_info, 'http://***.**.**.**/?action=stream', self.d_camera_label, self.d_seat_num, 9, self.D_res_cnt, self.D_peo_cnt)
            self.thread_d = QThread()
            self.worker_d.moveToThread(self.thread_d)

            self.worker_d.finished.connect(self.worker_d.deleteLater)
            self.worker_d.finished.connect(self.thread_d.quit)
            self.thread_d.started.connect(self.worker_d.run)

            self.thread_d.start()

        else:
            QMessageBox.information(self, 'No Seat Informaion', 'Please Setting your D seat information.')

    #D 영상 끄기
    def d_video_stop(self):
        if self.thread_d:
            self.D_on.setEnabled(True)
            self.D_off.setStyleSheet("color: white;" "background-color:#646464")
            self.D_on.setStyleSheet("color: white;" "background-color: #005F00")
            self.worker_d.stop()
            self.thread_d.quit()
            self.thread_d.wait()
            self.worker_d = None
            self.thread_d = None

            self.D_res_cnt.setText("0    ")
            self.D_peo_cnt.setText("0    ")

    # 무단 착석한 좌석 번호를 텍스트 파일로 저장
    def save(self):
        filters = "Text files (*.txt);;All Files (*)"
        fname, _ = QFileDialog.getSaveFileName(self, filter=filters)
        if fname:
            if not fname.endswith('.txt'):
                fname += '.txt'
            with open(fname, 'w') as file:
                file.write(f'<A Camera> Unreserved Seat : {self.a_seat_num.text()}\n')
                file.write(f'<B Camera> Unreserved Seat : {self.b_seat_num.text()}\n')
                file.write(f'<C Camera> Unreserved Seat : {self.c_seat_num.text()}\n')
                file.write(f'<D Camera> Unreserved Seat : {self.d_seat_num.text()}')

    # falko 사용법이 적힌 git 링크로 이동
    def go_git(self):
        url = "https://github.com/eane13/falko"
        webbrowser.open(url)

    # falko Informaion 창 띄움. 
    def falko_info(self):
        FalkoInfoWindow(self)

    # 좌석 정보 설정 창 띄움.
    def seat_set(self):
        SeatSettingsWindow(self)

    # 좌석 인식 창 띄움.
    def seat_capture(self):
        SeatCaptureWindow(self)


app = QApplication(sys.argv)
myWindow = MainWindow()
myWindow.resize(996, 932)
myWindow.show()
app.exec_()
