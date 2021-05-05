import os
import flask
import boto3
import cv2
import json
import math
import sys
import imutils
import time
from flask import Flask, render_template, request, redirect, url_for
from matplotlib import pyplot as plt
import mysql.connector
from PIL import ImageFont, ImageDraw, Image

import os
import cv2
import json
import math
import sys
import imutils
from matplotlib import pyplot as plt
from PIL import ImageFont, ImageDraw, Image

INF = 10000

error = 0


def get_frame(vidname):  # 모든 프레임을 다 저장. 따라서 경량화 하여 오버헤드 줄일 수 있다.
    pathname = vidname
    vidcap = cv2.VideoCapture(pathname)
    frame = []

    while True:
        success, image = vidcap.read()
        if not success:
            break
        frame.append(image.copy())
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    size = len(frame)
    return size, frame


def get_keypoints(filename, size):
    posepoints = []
    for i in range(size):  # 0~num i를 1씩 증가시키면서 반복
        num = format(i, "012")  # 0000000000000 문자열로 저장(12자리 0)
        jFileName = filename + "_" + num + "_keypoints.json"
        with open('output/' + jFileName, 'r') as f:
            json_data = json.load(f)  # json파일 불러오기댐
            # 첫번째 사람만 본다. 2명일때 예외처리 나중에해야
            keypoint = {'x': 0, 'y': 0, 'c': 0}  # 마지막 c는 신뢰도..0.3이하면 신뢰하지 않는다
            posepoint = []

            if not json_data['people']:  # openpose의 output은 물체에 사람이 잡히지 않을경우 poeple배열을 비운다. 빈 리스트인지 확인하는 코드
                return posepoints

            for j in range(75):  # 관절개수가 25개(0~24)
                if j % 3 == 0:  # 0번째 자리
                    keypoint['x'] = json_data['people'][0]['pose_keypoints_2d'][j]
                elif j % 3 == 1:
                    keypoint['y'] = json_data['people'][0]['pose_keypoints_2d'][j]
                elif j % 3 == 2:
                    keypoint['c'] = json_data['people'][0]['pose_keypoints_2d'][j]
                    posepoint.append(keypoint.copy())  # 리스트는 깊은복사라서.. copy로
                    # print(keypoint)
        posepoints.append(posepoint.copy())
    return posepoints


def cut_vid(frame, pose_index):
    poseimg = []  # mat타입의 이미지가 저장 될 리스트
    for i in pose_index:
        poseimg.append(frame[i])
    return poseimg


def get_distan(point1, point2):  # 두 점 사이의 거리를 구하는 함수
    a = point1.get('x') - point2.get('x')
    b = point2.get('y') - point2.get('y')
    return math.sqrt((a * a) + (b * b))


def get_humansize(posepoints):  # 인체 골격의 크기 구하기
    top = posepoints[0][15]
    bot = posepoints[0][19]
    hight = get_distan(top, bot)
    add = get_distan(posepoints[0][0], posepoints[0][1])
    return hight + add


def cut_img(posepoints, pose_img, pose_index, size):
    centers = []  # 프레임별로 몸 중심(8번관절)이 따로 필요하여 리스트로..
    img = []
    s = int(get_humansize(posepoints)) * 3
    for i in pose_index:  # 어드래스가 있는 프레임,테잌어웨이프레임.. 등등 순회
        centers.append((posepoints[i][8].get('x'), posepoints[i][8].get('y')))
    for idx in range(0, 7):  # 0,1,2,3,4,5,6 선형의 시간복잡도
        img = pose_img[idx]
        x, y = centers[idx][0], centers[idx][1]
        num = str(idx)
        # print("결과 이미지 크기는",s*2)
        # 여기에--- 모바일 영상 전송시 사이즈 조절 팔요시 size 매개변수로 ! 코드작성
        # roi = img[int(y-s):int(y+s), int(x-s):int(x+s)].copy()
        # [y시작:y끝             ,x시작:x끝]
        # pose_img[idx] = roi
        img = imutils.resize(img, width=500)
        pose_img[idx] = img
        # cv2.imshow("new" + num, img)
        # 필요시 image저장코드 :
        # fname = "{}.jpg".format("{0:05d}")
        # cv2.imwrite('result'+num+fname, img) # save frame as JPEG file
    cv2.waitKey()
    cv2.destroyAllWindows()
    return pose_img

def get_center(point1, point2):
    x1 = point1.get('x')
    y1 = point1.get('y')
    x2 = point2.get('x')
    y2 = point2.get('y')

    center_point = {'x': (x2 + x1) / 2, 'y': (y2 + y1) / 2}
    return center_point


def draw_angle(p1, p2, p3, img):
    red_color = (0, 0, 255)
    black_color = (0, 0, 0)
    px2 = p2.get('x')
    py2 = p2.get('y')
    px2 = int(px2)
    py2 = int(py2)
    px1 = p1.get('x')
    py1 = p1.get('y')
    px3 = p1.get('x')
    py3 = p3.get('y')

    if (px1 == 0 or py1 == 0 or px2 == 0 or py2 == 0 or px3 == 0 or py3 == 0):
        # 0일경우는 골격이 가려지거나 프레임이 좋지않아 인식되지않은 경우 이므로  그리지 않는다.
        return 0  # 그리기 실패

    circle_angle = 0
    angle = abs(get_angle(p1, p2, p3))

    start_angle = get_slope(p2, p3)
    end_angle = get_slope(p2, p1)
    if (start_angle - end_angle) > 180:
        tmp = start_angle
        start_angle = end_angle
        end_angle = tmp  # swap
        circle_angle = -180

    cv2.putText(img, str(int(angle)), (px2 - 50, py2), cv2.FONT_HERSHEY_SIMPLEX, 0.5, black_color, 2)
    cv2.ellipse(img, (px2, py2), (10, 10), circle_angle, start_angle, end_angle, black_color, 2)
    return 1  # 그리기 성공


def draw_line(p1, p2, img, color):
    sx = int(p1.get('x'))
    sy = int(p1.get('y'))
    fx = int(p2.get('x'))
    fy = int(p2.get('y'))
    if sx == 0 or sy == 0 or fx == 0 or fy == 0:
        return 0  # 그리기 실패

    cv2.line(img, (sx, sy), (fx, fy), color, 2)
    return 1  # 그리기 성공


def draw_point_line(p1, p2, img):  # 점선 그리기 하려고햇으나 ..
    sx = int(p1.get('x'))
    sy = int(p1.get('y'))
    fx = int(p2.get('x'))
    fy = int(p2.get('y'))
    grey_color = (211, 211, 211)

    cv2.line(img, (sx, sy), (fx, fy), grey_color, 2, 8)


def draw_adress(img, posepoint):  # 어드래스 이미지 골격을 그리는 함수
    red_color = (0, 0, 255)
    black_color = (0, 0, 0)
    blue_color = (255, 165, 0)

    lsx = int(posepoint[2].get('x'))  # 왼어깨x좌표 아래쭉 어깨

    rsx = int(posepoint[5].get('x'))  # 오른쪽 어깨
    rsy = int(posepoint[5].get('y') + 50)
    rsy2 = int(posepoint[5].get('y') - 50)
    lsy = int(posepoint[2].get('y') + 50)
    lsy2 = int(posepoint[2].get('y') - 50)

    left_angle = get_angle(posepoint[5], posepoint[2], posepoint[4])
    right_angle = get_angle(posepoint[2], posepoint[5], posepoint[7])

    draw_line(posepoint[2], posepoint[5], img, red_color)
    draw_line(posepoint[5], posepoint[7], img, red_color)
    draw_line(posepoint[2], posepoint[4], img, red_color)
    draw_line(posepoint[22], posepoint[19], img, blue_color)
    draw_angle(posepoint[1], posepoint[2], posepoint[4], img)
    draw_angle(posepoint[2], posepoint[5], posepoint[7], img)
    cv2.line(img, (rsx, rsy), (rsx, rsy2), blue_color, 2)  # 발 너비와 어깨 너비 비교
    cv2.line(img, (lsx, lsy), (lsx, lsy2), blue_color, 2)


def draw_takeAway(img, posepoint):
    red_color = (0, 0, 255)
    orange_color = (0, 165, 255)
    yellow_color = (0, 255, 255)

    draw_line(posepoint[2], posepoint[5], img, red_color)
    draw_line(posepoint[5], posepoint[7], img, red_color)
    draw_line(posepoint[2], posepoint[4], img, red_color)
    # 팔 삼각형

    # 실제 팔의 라인
    draw_line(posepoint[2], posepoint[3], img, orange_color)
    draw_line(posepoint[3], posepoint[4], img, yellow_color)
    draw_line(posepoint[5], posepoint[6], img, yellow_color)
    draw_line(posepoint[6], posepoint[7], img, orange_color)

    draw_angle(posepoint[2], posepoint[3], posepoint[4], img)
    draw_angle(posepoint[5], posepoint[6], posepoint[7], img)


def draw_top(img, posepoint):
    red_color = (0, 0, 255)
    blue_color = (255, 165, 0)

    draw_line(posepoint[1], posepoint[8], img, blue_color)
    draw_line(posepoint[19], posepoint[22], img, blue_color)
    #척추와 골반


    #오른 다리 굽혀짐 표시
    draw_line(posepoint[9], posepoint[10], img, red_color)
    draw_line(posepoint[10], posepoint[11], img, red_color)
    draw_angle(posepoint[9], posepoint[10], posepoint[11], img)


def draw_down(img, posepoint):
    result = img
    red_color = (0, 0, 255)
    orange_color = (255, 165, 0)

    rhx = int(posepoint[12].get('x'))  # 오른쪽 골반 x 좌표
    rhy = int(posepoint[12].get('y'))
    rkx = int(posepoint[13].get('x'))  # 오른쪽 무릎
    rky = int(posepoint[13].get('y'))
    rax = int(posepoint[14].get('x'))  # 오른쪽 발목
    ray = int(posepoint[14].get('y'))

    # 척추와 골반--
    draw_line(posepoint[1], posepoint[8], img, orange_color)
    draw_line(posepoint[9], posepoint[12], img, orange_color)

    #오른 다리 굽혀짐 표시
    draw_line(posepoint[9], posepoint[10], img, red_color)
    draw_line(posepoint[10], posepoint[11], img, red_color)
    draw_angle(posepoint[9], posepoint[10], posepoint[11], img)


def draw_impact(img, posepoint):
    result = img
    red_color = (0, 0, 255)
    orange_color = (255, 165, 0)

    lhx = int(posepoint[9].get('x'))  # 왼쪽 골반 x 좌표
    lhy = int(posepoint[9].get('y'))
    lkx = int(posepoint[10].get('x'))  # 왼쪽 무릎
    lky = int(posepoint[10].get('y'))
    lax = int(posepoint[11].get('x'))  # 왼쪽 발목
    lay = int(posepoint[11].get('y'))

    left_leg_angle = get_angle(posepoint[9], posepoint[10], posepoint[11])
    start_angle = (math.atan2(lay - lky, lax - lkx)) * (180 / math.pi)
    end_angle = (math.atan2(lhy - lky, lhx - lkx)) * (180 / math.pi)

    draw_line(posepoint[12], posepoint[13], img, red_color)
    draw_line(posepoint[13], posepoint[14], img, red_color)

    # 척추와 골반--
    draw_line(posepoint[1], posepoint[8], img, orange_color)
    draw_line(posepoint[9], posepoint[12], img, orange_color)
    draw_angle(posepoint[12], posepoint[13], posepoint[14], img)  # 좌측(그림에서 우측)무릎의 굽혀짐


def draw_follow_through(img, posepoint):
    red_color = (0, 0, 255)
    blue_color = (255, 165, 0)
    orange_color = (0, 165, 255)

    draw_line(posepoint[5], posepoint[6], img, red_color)
    draw_line(posepoint[6], posepoint[7], img, red_color)
    draw_line(posepoint[1], posepoint[5], img, orange_color)
    draw_line(posepoint[2], posepoint[1], img, orange_color)
    # 척추와 골반--
    draw_line(posepoint[1], posepoint[8], img, blue_color)
    draw_line(posepoint[9], posepoint[12], img, blue_color)

    draw_angle(posepoint[5], posepoint[6], posepoint[7], img)
    draw_angle(posepoint[1], posepoint[5], posepoint[6], img)


def draw_finish(img, posepoint):
    red_color = (0, 0, 255)
    orange_color = (255, 165, 0)

    draw_line(posepoint[1], posepoint[8], img, orange_color)
    draw_line(posepoint[9], posepoint[12], img, orange_color)

    draw_line(posepoint[22], posepoint[19], img, red_color)  # 지평면
    ground_point = posepoint[8]
    lslope = slope(posepoint[22], posepoint[19])

    #    y = slope*(x-ground_point.get('x')) + ground_point('y') #ground포인트를 시작점으로하는 선형 방정식을 정리하면 아래와 같다
    y = posepoint[15].get('y')
    x = lslope * (y - ground_point.get('y')) + ground_point.get('x')
    top_point = {'x': x, 'y': y}
    #draw_point_line(ground_point, top_point, img)  # 지평면
    # draw_angle(posepoint[1], posepoint[8], top_point, result)

    draw_line(posepoint[12], posepoint[13], img, red_color)
    draw_line(posepoint[13], posepoint[14], img, red_color)

    # 척추와 골반--
    draw_line(posepoint[1], posepoint[8], img, orange_color)
    draw_line(posepoint[9], posepoint[12], img, orange_color)
    draw_angle(posepoint[12], posepoint[13], posepoint[14], img)  # 좌측(그림에서 우측)무릎의 굽혀짐


def draw_image(pose_img, pose_idx,posepoints):
    adress_idx = pose_idx[0]
    takeAway_idx = pose_idx[1]
    top_idx = pose_idx[2]
    down_idx = pose_idx[3]
    impact_idx = pose_idx[4]
    follow_through = pose_idx[5]
    finish = pose_idx[6]

    draw_adress(pose_img[0], posepoints[adress_idx])
    draw_takeAway(pose_img[1], posepoints[takeAway_idx])
    draw_top(pose_img[2], posepoints[top_idx])
    draw_down(pose_img[3], posepoints[down_idx])
    draw_impact(pose_img[4], posepoints[impact_idx])
    draw_follow_through(pose_img[5], posepoints[follow_through])
    draw_finish(pose_img[6], posepoints[finish])


# -______________________
def slope(p1, p2):
    if (p1.get('x') == p2.get('x')):
        return 0
    else:
        return (p2.get('y') - p1.get('y')) / (p2.get('x') - p1.get('y'))


def get_slope_R(x1, y1, x2, y2):  # 두 점의 좌표를 가지고 수직선과의 각도를 구하는 함수
    if x1 != x2:  # 분모가 0이되는 상황 방지
        radian = math.atan2((y2 - y1), (x2 - x1))
        return radian
    else:
        return 0


def get_slope_R1(p1, p2):
    p1x = p1.get('x')
    p1y = p1.get('y')
    p2x = p2.get('x')
    p2y = p2.get('y')
    radian = math.atan((p2y - p1y) / (p2x - p1x))
    andgle = radian * (180 / math.pi)
    return andgle


def get_slope(p1, p2):
    p1x = p1.get('x')
    p1y = p1.get('y')
    p2x = p2.get('x')
    p2y = p2.get('y')
    radian = get_slope_R(p1x, p1y, p2x, p2y)
    andgle = radian * (180 / math.pi)
    return andgle


def get_distan(point1, point2):  # 두 점 사이의 거리를 구하는 공식
    a = point1.get('x') - point2.get('x')
    b = point2.get('y') - point2.get('y')
    return math.sqrt((a * a) + (b * b))


def get_angle(joint1, joint2, joint3):  # 두 몸체의 기울기를 가지고 관절의 각도를구하는 함수      locate ->  j1 ------ j2 ------- j3
    if (joint1.get('x') - joint2.get('x')) == 0:
        return 0
    if (joint3.get('x') - joint2.get('x')) == 0:
        return 0
    radi1 = math.atan2((joint1.get('y') - joint2.get('y')), (joint1.get('x') - joint2.get('x')))
    radi2 = math.atan2((joint3.get('y') - joint2.get('y')), (joint3.get('x') - joint2.get('x')))
    radian = radi1 - radi2
    # print(radian)
    angle = radian * (180 / math.pi)
    if (abs(angle) > 180):
        angle = 360 - abs(angle)
    return angle


def get_y_wrist(posepoints, lr):
    # 손목 위치의 함수를 반환,프레임배열과, 왼오 옵
    y_point_arr = []
    if (lr == "left"):  # 왼
        for i in range(len(posepoints)):
            lwrist = posepoints[i][7].get('y')
            if (lwrist == 0):  # 이상치에서 최소 값을 봐야하므로 inf로 대체
                y_point_arr.append(INF)
            elif (posepoints[i][7].get('c') < 0.2):
                y_point_arr.append(INF)
            else:
                y_point_arr.append(lwrist)

    elif (lr == "right"):  # 오른손
        for i in range(len(posepoints)):
            rwrist = posepoints[i][4].get('y')
            if (rwrist == 0):  # 이상치에서 최소 값을 봐야하므로 inf로 대체
                y_point_arr.append(INF)
            elif (posepoints[i][4].get('c') < 0.2):
                y_point_arr.append(INF)
            else:
                y_point_arr.append(rwrist)
    return y_point_arr


def get_x_wrist(posepoints, lr):
    # 손목 위치의 함수를 반환,프레임배열과, 왼오 옵
    y_point_arr = []
    if (lr == "left"):  # 왼
        for i in range(len(posepoints)):
            lwrist = posepoints[i][7].get('x')
            if (lwrist == 0):  # 이상치에서 최소 값을 봐야하므로 inf로 대체
                y_point_arr.append(INF)
            elif (posepoints[i][7].get('c') < 0.2):
                y_point_arr.append(INF)
            else:
                y_point_arr.append(lwrist)

    elif (lr == "right"):  # 오른손
        for i in range(len(posepoints)):
            rwrist = posepoints[i][4].get('x')
            if (rwrist == 0):  # 이상치에서 최소 값을 봐야하므로 inf로 대체
                y_point_arr.append(INF)
            elif (posepoints[i][4].get('c') < 0.2):
                y_point_arr.append(INF)
            else:
                y_point_arr.append(rwrist)
    return y_point_arr


def get_axis(left_wrist, right_wrist):  # 손목의 변화량을 찾기위한 그래프의 축 리스트 리턴
    lx_values, ly_values, rx_values, ry_values = [], [], [], []
    for i in range(len(left_wrist)):  # left wrist와 right wrist가 같다
        if (left_wrist[i] != INF):  # inf값에는 포즈가 감지되지 않아 0값이 기록되어 있으므로 넘어간다.
            ly_values.append(left_wrist[i])
            lx_values.append(i)

        if (right_wrist[i] != INF):
            ry_values.append(right_wrist[i])
            rx_values.append(i)
    return lx_values, ly_values, rx_values, ry_values


# 순서대로 왼손좌표의 x축(프레임 변화), 왼손좌표의 y축(좌표변화),오른손x,y

def get_error(arr):  # 손목 위치의 허용 오차 구하기
    mini = min(arr)
    maxi = max(arr)
    dif = maxi - mini
    error = (dif / 5)
    print(error)
    return error


def pose_classifier(posepoints):
    idx = [-1, -1, -1, -1, -1, -1, -1]  # 어,테이크어웨이,탑,다운,임펙,팔로스루,피니쉬

    # -------------- 손목의 x좌표 변화량 감지를 통해 스윙이 시작하는지(어드래스)감지)----
    left_wrist = get_x_wrist(posepoints, 'left')
    right_wrist = get_x_wrist(posepoints, 'right')

    lx_values, ly_values, rx_values, ry_values = get_axis(left_wrist, right_wrist)
    slopes = []
    for i in range(0, len(rx_values)):
        if (len(rx_values) - 1 == i):  # 마지막 점의 경우 변화량을 계산할 필요가 없음
            slopes.append(slope)
            break
        else:
            dx = rx_values[i + 1] - rx_values[i]
            dy = ry_values[i + 1] - ry_values[i]
            slope = dy / dx

            cur_frmae_idx = rx_values[i]
            if (slope <= -8 and idx[0] == -1):  # 좌측으로 움직이면 x좌표의 변화량은 감소
                dy_left = ly_values[cur_frmae_idx + 1] - ly_values[cur_frmae_idx]
                slope_left = dy_left / dx
                if (slope_left <= -8):
                    idx[0] = rx_values[i - 1]
                    break
            slopes.append(slope)

    # -------------- 손목의 y좌표 변화량 감지를 통해 포즈 분류 ----
    # 테이커웨이,스윙 탑,입펙트값을 먼저 구한다.

    left_wrist = get_y_wrist(posepoints, 'left')
    right_wrist = get_y_wrist(posepoints, 'right')

    lx_values, ly_values, rx_values, ry_values = get_axis(left_wrist, right_wrist)
    # 왼손의 인덱스,왼손의 x좌표값,오른손 인덱스,오른손 x좌표깂

    l_downpoint = left_wrist[idx[0]]  # 손목의 가장 낮은 높이 이것과 비슷해야 임팩트(공을칠떄 손목이 맨아래에위치)
    r_downpoint = right_wrist[idx[0]]  # 손목의 가장 낮은 높이 이것과 비슷해야 임팩트(공을칠떄 손목이 맨아래에위치)

    r_error = get_error(ry_values)
    size = len(rx_values)
    last_frame = rx_values[size - 1]
    for i in range(0, size):
        cur_frmae_idx = rx_values[i]
        next_frame_idx = rx_values[i + 1]

        if (last_frame - 2 == cur_frmae_idx):  # 마지막 점의 경우 변화량을 계산할 필요가 없음
            slopes.append(slope)
            break
        else:
            dx = next_frame_idx - cur_frmae_idx  # 손목위치가 있는 인덱스
            cur_locate = posepoints[cur_frmae_idx][4].get('y')  # 오른 손목의 위치....
            next_locate = posepoints[next_frame_idx][4].get('y')
            dy = next_locate - cur_locate  # 프레임 인덱스
            slope = dy / dx

            if (idx[0] != -1 and slope <= -8 and idx[0] < cur_frmae_idx and idx[1] == -1):  # 테이크어웨이 검사
                dy_left = ly_values[cur_frmae_idx + 1] - ly_values[cur_frmae_idx]
                slope_left = dy_left / dx
                if (slope_left <= -8):
                    idx[1] = cur_frmae_idx + 2
                    continue

            if (idx[1] != -1) and idx[1] < cur_frmae_idx and idx[2] == -1 and slope >= 20:  # 탑 검사
                dy_left = posepoints[next_frame_idx][7].get('y') - posepoints[cur_frmae_idx][7].get('y')
                slope_left = dy_left / dx
                if slope_left > 0:
                    idx[2] = cur_frmae_idx -2
                    continue
            if (idx[2] != -1 and idx[2] < cur_frmae_idx and idx[4] == -1 and slope < -2 and r_downpoint - r_error < cur_locate):
                idx[4] = cur_frmae_idx
                break

            slopes.append(slope)

    #plt.scatter(lx_values, ly_values)
    #plt.scatter(rx_values, ry_values)

    #plt.legend(['left', 'right'])
    #plt.show()

    # ----------2번 탑스윙 재 계산 ------------
    impact = idx[4]
    right_wrist1 = right_wrist[0:impact]
    # 손목의 높이가 최대가 되는 곳(영상의 프레임 인덱스)을 리턴 (y축이 작을 수록 상단에 위치)
    rtop_idx = right_wrist.index(min(right_wrist1))  # 손목의 높이가 최대가 되는 곳을 리턴
    rtop = min(right_wrist1)
    if (posepoints[idx[2]][4].get('y')>rtop+r_error ):
        idx[2] = rtop_idx

    # -------------- 이후 피니쉬는 손목의 위치가 가장 높을때 이므로 (임팩트 이후의) 손목 높이의 최대값을 구한다.

    left_wrist = left_wrist[impact:]
    right_wrist = right_wrist[impact:]
    ltop = left_wrist.index(min(left_wrist))  # 손목의 높이가 최대가 되는 곳(영상의 프레임 인덱스)을 리턴 (y축이 작을 수록 상단에 위치)
    rtop_idx = right_wrist.index(min(right_wrist))  # 손목의 높이가 최대가 되는 곳을 리턴
    ltop = ltop + impact  # 임펙트인덱스만큼 뒤에서 자르고 최대값을 찾았으므로 더해준다
    rtop_idx = rtop_idx + impact
    if (rtop_idx > idx[4]):  # 피니쉬라고 생각된느프레임이 임팩트 이후인지 확인
        idx[6] = rtop_idx
    elif (ltop > idx[4]):  # 왼쪽손목의 최대높이를 피니쉬로 설정
        idx[6] = ltop
    else:
        idx[6] = -1  # 피니쉬를 찾을 수 없을때 -1 리턴
    # -------------- 이후 사이값으로 다운과 팔로스루 구하기
    idx[3] = int((idx[4] - idx[2]) * 0.666666) + idx[2]  # 다운 2/3지점으로 설정
    idx[5] = int((idx[6] + idx[4]) / 2)  # 팔로스루
    print(idx)
    return idx





# -----------
def assess_pose(posepoints, pose_idx):
    hscore = check_headup(posepoints, pose_idx)
    bscore = check_body_sway(posepoints, pose_idx)
    cscore = check_chickin_wing(posepoints, pose_idx)

    score_list = [hscore, bscore, cscore]  # 가장 심각한 실수가 어떤것지 찾기위해
    worst = score_list.index(min(score_list))  # 사용자에게 보여줄 가장 심한 실수의 인덱스를 찾는다.

    if worst == 0:  # head_up이 가장 심각한 실수
        # 서버에 문제가 있는 헤드업 사진을 전송하기
        # 의견 : 임팩트 이후에 헤드업이 발생한 부분에 그림더 그려줘서 보내는 방식
        a = 0
    elif worst == 1:  # 바디 스웨이가 가장 심각한 실수
        # 서버에 문제가 있는 헤드업 사진을 전송하기
        # 의견 : 임팩트 이후에 헤드업이 발생한 부분에 그림더 그려줘서 보내는 방식
        a = 1
    elif worst == 2:  # 치킨윙이 심각한 경우
        # 서버에 문제가 있는 헤드업 사진을 전송하기
        # 의견 : 임팩트 이후에 헤드업이 발생한 부분에 그림더 그려줘서 보내는 방식
        a = 2

    total_score = 100
    for i in score_list:
        total_score = total_score + i
        # 100점에서 발생한 실수만큼 뺀다
    print("당신의 포즈 점수는")
    print(total_score)
    return total_score


def check_headup(posepoints, pose_idx):
    adress_idx = pose_idx[0]
    takeAway_idx = pose_idx[1]
    top_idx = pose_idx[2]
    down_idx = pose_idx[3]
    impact_idx = pose_idx[4]
    follow_through = pose_idx[5]
    finish = pose_idx[6]

    return 0


def check_body_sway(posepoints, pose_idx):
    dress_idx = pose_idx[0]
    take_away_idx = pose_idx[1]
    top_idx = pose_idx[2]
    down_idx = pose_idx[3]
    impact_idx = pose_idx[4]
    follow_through_idx = pose_idx[5]
    finish_idx = pose_idx[6]

    score = 0  # 100점에서 차감할 점수의 초기값

    top_point = posepoints[top_idx]
    finish_point = posepoints[finish_idx]

    spine_angle_top_swing = get_angle(top_point[1], top_point[8], top_point[12])
    spine_angle_finish = get_angle(finish_point[1], finish_point[8], finish_point[12])
    dif_angle = abs(spine_angle_finish) - abs(spine_angle_top_swing)

    dif_angle = abs(dif_angle)  # 차이를 절대값으로 점수 계산

    if dif_angle > 3.5:
        score = dif_angle * 10
    elif (dif_angle <= 3.5):
        score = dif_angle
    elif (dif_angle <= 1.5):
        score = 0
    score = int(score)
    # print(score)

    return -score


def check_chickin_wing(posepoints, pose_idx):
    dress_idx = pose_idx[0]
    take_away_idx = pose_idx[1]
    top_idx = pose_idx[2]
    down_idx = pose_idx[3]
    impact_idx = pose_idx[4]
    follow_through = pose_idx[5]
    finish = pose_idx[6]

    return -30

def main(URL,userid):
    #date = os.system('date')
    time.sleep(2)
    downloadFile(URL)
    filepath = '../openpose/examples/media/'
    filename = 'TestGolf'
    vidname = filepath + filename+'.mp4'
    #아래 주석풀면 gpu 과부하걸리니 최초 실행시만
    path = os.system('../openpose/build/examples/openpose/openpose.bin --video ' '../openpose/examples/media/TestGolf.mp4 --write_json output/ --display 0 --render_pose 0')
    size,frame=get_frame(vidname)
    posepoints = get_keypoints(filename,size)
    pose_idx = pose_classifier(posepoints)  # 포즈 분류하기
    pose_img = cut_vid(frame, pose_idx)  # pose_img 는 리스트 입니다..
    draw_image(pose_img, pose_idx, posepoints)  # 골격 그리기
    image = cut_img(posepoints, pose_img, pose_idx, 0)  # 서버에 전송할 7가지 이미지 자르기(포즈 자세히 부분에 사용자에게 보여줄거)
    assess_pose(posepoints, pose_idx)  # 포즈 평가하기
    makeImageFile(image,URL,userid)
def uploadFile(filename, files,userid):
    s3 = boto3.client(
        's3',  # 사용할 서비스 이름, ec2이면 'ec2', s3이면 's3', dynamodb이면 'dynamodb'
        aws_access_key_id="AKIAV7WUXMYC2J5GO6ND",  # 액세스 ID
        aws_secret_access_key="oGPrWSHFA2s9q0/Ow3kPs2vi5vOW3lEBj0Qb6YJj")  # 비밀 엑세스 키
    s3.upload_file(files, 'golfapplication', userid + '/image/' +filename)
def downloadFile(URL):
    filename = '../openpose/examples/media/TestGolf.mp4'
    bucket = 'golfapplication'
    key = URL[56:]
    s3 = boto3.client(
        's3',  # 사용할 서비스 이름, ec2이면 'ec2', s3이면 's3', dynamodb이면 'dynamodb'
        aws_access_key_id="AKIAV7WUXMYC2J5GO6ND",  # 액세스 ID
        aws_secret_access_key="oGPrWSHFA2s9q0/Ow3kPs2vi5vOW3lEBj0Qb6YJj")  # 비밀 엑세스 키
    s3.download_file(bucket, key, filename)
def createFolder(directory):
    try:
        if not os.path.exists(directory):
                os.makedirs(directory)
    except OSError:
         print('Error: Creating directory. ' + directory)
def makeImageFile(image,URL,userid):
    for idx in range(0, 7):
        num = str(idx)
        Fname =  URL[61 :]
        cv2.imwrite(userid + '/' + Fname + '-' + num + '.jpg', image[idx])  # save frame as JPEG file
        uploadFile(Fname + '-' + num + '.jpg',userid + '/' + Fname + '-' + num + '.jpg',userid)
app = Flask(__name__)
@app.route('/db', methods = ['GET', 'POST'])
def chat():
    msg_received = flask.request.get_json()
    msg_subject = msg_received["subject"]

    if msg_subject == "register":
        return register(msg_received)
    elif msg_subject == "login":
        return login(msg_received)
    elif msg_subject == "video":
        return video(msg_received)
    else:
        return "Invalid request."
def video(msg_received):
    userid = msg_received["userid"]
    videoURL = msg_received["URL"]

    select_query = "SELECT * FROM video where URL = " + "'" + videoURL + "'"
    db_cursor.execute(select_query)
    records = db_cursor.fetchall()
    if len(records) != 0:
        return "Another user used the username. Please chose another username."

    insert_query = "INSERT INTO video (id, URL) VALUES (%s,%s)"
    insert_values = (userid, videoURL)
    try:
        db_cursor.execute(insert_query, insert_values)
        chat_db.commit()
        time.sleep(2)
        downloadFile(videoURL)
        createFolder('./' + userid)
        main(videoURL,userid)
        return "success"
    except Exception as e:
        print("Error while inserting the new record :", repr(e))
        return "failure"
def register(msg_received):
    id = msg_received["userid"]
    password = msg_received["userpwd"]
    username = msg_received["username"]
    email = msg_received["useremail"]

    select_query = "SELECT * FROM users where id = " + "'" + id + "'"
    db_cursor.execute(select_query)
    records = db_cursor.fetchall()
    if len(records) != 0:
        return "Another user used the username. Please chose another username."

    insert_query = "INSERT INTO users (id, psw, name, email) VALUES (%s, MD5(%s), %s, %s)"
    insert_values = (id, password, username, email)
    try:
        db_cursor.execute(insert_query, insert_values)
        chat_db.commit()
        return "success"
    except Exception as e:
        print("Error while inserting the new record :", repr(e))
        return "failure"

def login(msg_received):
    username = msg_received["userid"]
    password = msg_received["userpwd"]
    select_query = "SELECT name FROM users where id = " + "'" + username + "' and psw = " + "MD5('" + password + "')"
    db_cursor.execute(select_query)
    records = db_cursor.fetchall()

    if len(records) == 0:
        return "failure"
    else:
        return "success"
try:
    chat_db = mysql.connector.connect(host="golfdb.chx469ppubzv.ap-northeast-2.rds.amazonaws.com",
                                      user="jaewon", passwd="jl42474247", database="Golfuser")
except:
    sys.exit("Error connecting to the database. Please check your inputs.")
db_cursor = chat_db.cursor()
#main()
if __name__ == "__main__":
	app.run(host="0.0.0.0", port=5000, debug=True, threaded=True)