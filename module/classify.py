INF = 10000
import math
from matplotlib import pyplot as plt

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
    return error

def to_wrist_accuracy (posepoints,idx): #손목의 위치가 있는 보이는 곳 까지 프레임을 빼주는 재귀함수
    if posepoints[idx[5]][7].get('c')< 0.3:
        idx[5] -= 1
        to_wrist_accuracy(posepoints,idx)
        return idx
    else :
        return idx



def pose_classifier(posepoints):
    idx = [-1, -1, -1, -1, -1, -1, -1]  # 어,테이크어웨이,탑,다운,임펙,팔로스루,피니쉬

    # -------------- 손목의 x좌표 변화량 감지를 통해 스윙이 시작하는지(어드래스)감지)----
    left_wrist = get_x_wrist(posepoints, 'left')
    right_wrist = get_x_wrist(posepoints, 'right')

    lx_values, ly_values, rx_values, ry_values = get_axis(left_wrist, right_wrist)
    slopes = []
    slope = 0
    size = len(rx_values)
    last_frame = rx_values[size - 1]
    for i in range(0, len(rx_values)): #body25 4번 관절로 판단.
        cur_frmae_idx = rx_values[i]
        next_frame_idx = rx_values[i + 1]

        if (last_frame - 2 == cur_frmae_idx):  # 마지막 점의 경우 변화량을 계산할 필요가 없음
            slopes.append(slope)
            break
        else:
            dx = next_frame_idx - cur_frmae_idx  # 손목위치가 있는 인덱스
            cur_locate = posepoints[cur_frmae_idx][4].get('x')  # 오른 손목의 위치....
            next_locate = posepoints[next_frame_idx][4].get('x')
            dy = next_locate - cur_locate  # 프레임 인덱스
            slope = dy / dx

            cur_frmae_idx = rx_values[i]
            if (slope <= -6 and idx[0] == -1):  # 좌측으로 움직이면 x좌표의 변화량은 감소
                dy_left = ly_values[cur_frmae_idx + 1] - ly_values[cur_frmae_idx]
                slope_left = dy_left / dx
                if (slope_left <= -6):
                    idx[0] = cur_frmae_idx
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

    plt.scatter(lx_values, ly_values)
    plt.scatter(rx_values, ry_values)

    plt.legend(['left', 'right'])
    plt.show()

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
    ltop_idx = left_wrist.index(min(left_wrist))  # 손목의 높이가 최대가 되는 곳(영상의 프레임 인덱스)을 리턴 (y축이 작을 수록 상단에 위치)
    rtop_idx = right_wrist.index(min(right_wrist))  # 손목의 높이가 최대가 되는 곳을 리턴
    ltop_idx = ltop_idx + impact  # 임펙트인덱스만큼 뒤에서 자르고 최대값을 찾았으므로 더해준다
    rtop_idx = rtop_idx + impact

    length = len(posepoints)

    if (rtop_idx > idx[4]):  # 피니쉬라고 생각된느프레임이 임팩트 이후인지 확인
        if(rtop_idx+1 < length):
            idx[6] = rtop_idx
        else:
            idx[6] = rtop_idx
    elif ltop_idx > idx[4]:  # 왼쪽손목의 최대높이를 피니쉬로 설정
        if (ltop_idx + 1 >= length):
            idx[6] = ltop_idx + 1
        else:
            idx[6] = ltop_idx
    else:
        idx[6] = -1  # 피니쉬를 찾을 수 없을때 -1 리턴
    # -------------- 이후 사이값으로 다운과 팔로스루 구하기
    idx[3] = int((idx[4] - idx[2]) * 0.666666) + idx[2]  # 다운 2/3지점으로 설정
    idx[5] = int((idx[6] - idx[4]) * 0.333333) + idx[4]  # 팔로스루
    idx = to_wrist_accuracy(posepoints, idx)
    print(idx)
    return idx
