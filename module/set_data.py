import sys, os
import cv2
import json
import math

sys.path.append(os.pardir)  # 부모 디렉터리의 파일을 가져올 수 있도록 설정


INF = 10000

error = 0


def get_frame(pathname):  # 모든 프레임을 다 저장. 따라서 경량화 하여 오버헤드 줄일 수 있다.
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
                return posepoints, -1
            for j in range(75):  # 관절개수가 25개(0~24)
                if j % 3 == 0:  # 0번째 자리
                    keypoint['x'] = json_data['people'][0]['pose_keypoints_2d'][j]
                    if(keypoint['x'] > 800) :
                        return posepoints, -1
                elif j % 3 == 1:
                    keypoint['y'] = json_data['people'][0]['pose_keypoints_2d'][j]
                elif j % 3 == 2:
                    keypoint['c'] = json_data['people'][0]['pose_keypoints_2d'][j]
                    posepoint.append(keypoint.copy())  # 리스트는 깊은복사라서.. copy로
                    # print(keypoint)
        posepoints.append(posepoint.copy())
    return posepoints, 1


def slope(p1, p2):
    if (p1.get('x') == p2.get('x')):
        return 0
    else:
        return (p2.get('y') - p1.get('y')) / (p2.get('x') - p1.get('x'))


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


def get_distan(point1,point2): #두 점 사이의 거리를 구하는 공식
    a = point1.get('x') - point2.get('x')
    b = point2.get('y') - point2.get('y')
    return math.sqrt((a*a) + (b*b))


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


def get_y_wrist(posepoints,lr) : 
    #손목 위치의 함수를 반환,프레임배열과, 왼오 옵
    y_point_arr = []
    if (lr == "left"): #왼
        for i in range(len(posepoints)):
            lwrist = posepoints[i][4].get('y')
            if(lwrist == 0): #이상치에서 최소 값을 봐야하므로 inf로 대체
                y_point_arr.append(INF)
            elif (posepoints[i][4].get('c') < 0.2):
                y_point_arr.append(INF)
            else:y_point_arr.append(lwrist)
            
    elif (lr == "right"): #오른손
        for i in range(len(posepoints)):
            rwrist = posepoints[i][7].get('y')
            if(rwrist == 0): #이상치에서 최소 값을 봐야하므로 inf로 대체
                y_point_arr.append(INF)
            elif (posepoints[i][4].get('c') < 0.2):
                y_point_arr.append(INF)
            else:y_point_arr.append(rwrist)            
    return y_point_arr      


def get_x_wrist(posepoints,lr) : 
    #손목 위치의 함수를 반환,프레임배열과, 왼오 옵
    y_point_arr = []
    if (lr == "left"): #왼
        for i in range(len(posepoints)):
            lwrist = posepoints[i][4].get('x')
            if(lwrist == 0): #이상치에서 최소 값을 봐야하므로 inf로 대체
                y_point_arr.append(INF)
            elif (posepoints[i][4].get('c') < 0.2):
                y_point_arr.append(INF)
            else:y_point_arr.append(lwrist)
            
    elif (lr == "right"): #오른손
        for i in range(len(posepoints)):
            rwrist = posepoints[i][7].get('x')
            if(rwrist == 0): #이상치에서 최소 값을 봐야하므로 inf로 대체
                y_point_arr.append(INF)
            elif (posepoints[i][4].get('c') < 0.2):
                y_point_arr.append(INF)
            else:y_point_arr.append(rwrist)            
    return y_point_arr


def get_head(posepoints):
    l_ear = posepoints[1][17]
    r_ear = posepoints[1][18]
    
    size = get_distan(l_ear,r_ear)
    return int(size)

