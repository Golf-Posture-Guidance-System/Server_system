import math
import cv2
#from module.set_data import *
import imutils

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
    hight = top.get('y')-bot.get('y')
    return abs(hight)


def cut_img(posepoints, pose_img, pose_index, dst_size = 300):
    centers = []  # 프레임별로 몸 중심(8번관절)이 따로 필요하여 리스트로..
    h_size = int(get_humansize(posepoints)) #사람 크기
    for i in pose_index:  # 어드래스가 있는 프레임,테잌어웨이프레임.. 등등 순회
        centers.append((posepoints[i][8].get('x'), posepoints[i][8].get('y')))
    for idx in range(0, 7):  # 0,1,2,3,4,5,6 선형의 시간복잡도
        img = pose_img[idx]
        x, y = centers[idx][0], centers[idx][1]
        num = str(idx)
        haf_size = h_size*2/3
        if x < y:
            small_side = x
        else :
            small_side = y

        if haf_size >= small_side:
            haf_size = small_side
            roi = img[int(y - haf_size):int(y + haf_size), int(x - haf_size):int(x + haf_size)].copy()
            img = roi.copy()
            pose_img[idx] = img
        else:
            roi = img[int(y-haf_size):int(y+haf_size), int(x-haf_size):int(x+haf_size)].copy()
            #        [y시작:y끝             ,x시작:x끝]
            img = roi.copy()
            img = imutils.resize(img, width=600)
            pose_img[idx] = img
        #cv2.imshow("new" + num, img)
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

def draw_angle2(p1, p2, p3, img):
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
    angle = 360 - abs(get_angle(p1, p2, p3))

    start_angle = get_slope(p2, p3)
    end_angle = get_slope(p2, p1)
    if (start_angle - end_angle) > 180:
        tmp = start_angle
        start_angle = end_angle
        end_angle = tmp  # swap
        circle_angle = -180

    cv2.putText(img, str(int(angle)), (px2 - 50, py2), cv2.FONT_HERSHEY_SIMPLEX, 0.5, black_color, 2)
    cv2.ellipse(img, (px2, py2), (10, 10), circle_angle-180, start_angle , end_angle, black_color, 2)
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


def draw_address(img, posepoint):  # 어드래스 이미지 골격을 그리는 함수
    red_color = (0, 0, 255)
    black_color = (0, 0, 0)
    blue_color = (255, 165, 0)
    yellow_color = (0, 255, 255)

    lsx = int(posepoint[2].get('x'))  # 왼어깨x좌표 아래쭉 어깨
    rsx = int(posepoint[5].get('x'))  # 오른쪽 어깨
    rsy = int(posepoint[5].get('y') + 50)
    rsy2 = int(posepoint[5].get('y') - 50)
    lsy = int(posepoint[2].get('y') + 50)
    lsy2 = int(posepoint[2].get('y') - 50)
    angle = abs(get_angle(posepoint[2], posepoint[5], posepoint[7]))
    start_angle = get_slope(posepoint[5], posepoint[7])
    end_angle = get_slope(posepoint[5], posepoint[2])

    if (start_angle - end_angle) > 180:
        end_angle = abs(end_angle)
    draw_line(posepoint[2], posepoint[5], img, yellow_color)
    draw_line(posepoint[5], posepoint[7], img, red_color)
    draw_line(posepoint[2], posepoint[4], img, red_color)
    draw_line(posepoint[22], posepoint[19], img, blue_color)
    draw_angle(posepoint[1], posepoint[2], posepoint[4], img)

    cv2.putText(img, str(int(angle)), (rsx + 30, rsy - 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, black_color, 2)
    cv2.ellipse(img, (rsx, rsy - 50), (10, 10), 0, start_angle, end_angle, black_color, 2)

    cv2.line(img, (rsx, rsy), (rsx, rsy2), blue_color, 2)  # 발 너비와 어깨 너비 비교
    cv2.line(img, (lsx, lsy), (lsx, lsy2), blue_color, 2)


def draw_takeAway(img, posepoint):
    red_color = (0, 0, 255)
    black_color = (0, 0, 0)
    orange_color = (0, 165, 255)
    yellow_color = (0, 255, 255)
    rsx = int(posepoint[5].get('x'))
    rsy = int(posepoint[5].get('y'))

    angle = abs(get_angle(posepoint[2], posepoint[5], posepoint[7]))
    start_angle = get_slope(posepoint[5], posepoint[7])
    end_angle = get_slope(posepoint[5], posepoint[2])

    if end_angle < 0:
        end_angle = abs(end_angle)
    draw_line(posepoint[2], posepoint[5], img, red_color)
    draw_line(posepoint[5], posepoint[7], img, red_color)
    draw_line(posepoint[2], posepoint[4], img, red_color)
    draw_angle(posepoint[1], posepoint[2], posepoint[4],img)
    cv2.putText(img, str(int(angle)), (rsx + 30, rsy), cv2.FONT_HERSHEY_SIMPLEX, 0.5, black_color, 2)
    cv2.ellipse(img, (rsx, rsy ), (10, 10), 0, start_angle , 360 - end_angle,  black_color, 2)

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
    orange_color = (0, 165, 255)
    yellow_color = (0, 255, 255)


    #척추와 골반
    draw_line(posepoint[1], posepoint[8], img, blue_color)
    draw_line(posepoint[9], posepoint[12], img, blue_color)

    #어깨
    draw_line(posepoint[2], posepoint[5], img, red_color)
    draw_line(posepoint[5], posepoint[6], img, orange_color)
    draw_line(posepoint[6], posepoint[7], img, orange_color)
    draw_line(posepoint[2], posepoint[3], img, yellow_color)
    draw_line(posepoint[3], posepoint[4],img, yellow_color)
    draw_angle(posepoint[5], posepoint[6], posepoint[7], img)
    draw_angle(posepoint[2], posepoint[3], posepoint[4], img)

    #왼쪽 다리 굽혀짐 표시
    draw_line(posepoint[12], posepoint[13], img, red_color)
    draw_line(posepoint[13], posepoint[14], img, red_color)
    draw_angle(posepoint[12], posepoint[13], posepoint[14],img)





def draw_down(img, posepoint):
    blue_color = (255, 165, 0)
    red_color = (0, 0, 255)
    orange_color = (0, 165, 255)




    # 척추와 골반--
    draw_line(posepoint[1], posepoint[8], img, blue_color)
    draw_line(posepoint[9], posepoint[12], img, blue_color)

    # 오른쪽 팔
    draw_line(posepoint[2], posepoint[3], img, orange_color)
    draw_line(posepoint[3], posepoint[4], img, orange_color)
    draw_angle(posepoint[2], posepoint[3], posepoint[4], img)

    #오른 다리 굽혀짐 표시
    draw_line(posepoint[9], posepoint[10], img, red_color)
    draw_line(posepoint[10], posepoint[11], img, red_color)
    draw_angle(posepoint[9], posepoint[10], posepoint[11], img)


def draw_impact(img, posepoint):
    red_color = (0, 0, 255)
    blue_color = (255, 165, 0)
    orange_color = (0, 165, 255)
    black_color = (0, 0, 0)

    neck = posepoint[1]
    waist = posepoint[8]
    px = int(waist.get('x'))
    py = int(waist.get('y'))

    x = neck.get('x') - waist.get('x')
    y = neck.get('y') - waist.get('y')

    point = {'x': waist.get('x'), 'y': neck.get('y')}
    angle = abs(math.atan2(y, x) * 180 / math.pi)
    angle = abs(90-angle)


    draw_line(posepoint[12], posepoint[13], img, red_color)
    draw_line(posepoint[13], posepoint[14], img, red_color)

    # 척추와 골반--
    draw_line(point, posepoint[8], img, orange_color)
    if neck.get('x') < waist.get('x'):
        start_angle = angle
        end_angle = get_slope(point, waist)
    else:
        start_angle = 2 *angle
        end_angle = angle - get_slope(point,waist)
    cv2.putText(img, str(int(angle)), (px+20,py-90), cv2.FONT_HERSHEY_SIMPLEX, 0.5, black_color, 2)
    cv2.ellipse(img, (px, py), (80, 80), 270-angle , start_angle , end_angle, red_color, 2)
    draw_line(posepoint[1], posepoint[8], img, blue_color)
    draw_line(posepoint[9], posepoint[12],img, blue_color)
    draw_angle(posepoint[9], posepoint[10], posepoint[11], img)

    #오른쪽 다리
    draw_line(posepoint[9], posepoint[10], img, red_color)
    draw_line(posepoint[10],posepoint[11], img, red_color)



def draw_follow_through(img, posepoint):
    red_color = (0, 0, 255)
    blue_color = (255, 165, 0)
    orange_color = (0, 165, 255)

    draw_line(posepoint[5], posepoint[6], img, red_color)
    draw_line(posepoint[6], posepoint[7], img, red_color)
    draw_line(posepoint[1], posepoint[5], img, orange_color)
    draw_line(posepoint[2],posepoint[1],img,orange_color)
    draw_line(posepoint[5], posepoint[1], img, red_color)
    # 척추와 골반--
    draw_line(posepoint[1], posepoint[8], img, blue_color)
    draw_line(posepoint[9], posepoint[12], img, blue_color)

    draw_angle(posepoint[5], posepoint[6], posepoint[7], img)
    draw_angle(posepoint[1], posepoint[5], posepoint[6], img)

    #다리 --
    draw_line(posepoint[9],posepoint[11], img, orange_color)
    draw_angle(posepoint[9], posepoint[10], posepoint[11], img)
    draw_line(posepoint[12], posepoint[14], img, orange_color)
    draw_angle(posepoint[12], posepoint[13], posepoint[14], img)


def draw_finish(img, posepoint):
    red_color = (0, 0, 255)
    blue_color = (255, 165, 0)
    orange_color = (0, 165, 255)

    draw_line(posepoint[1], posepoint[8], img, blue_color)
    draw_line(posepoint[9], posepoint[12], img, blue_color)
    #어깨
    draw_line(posepoint[2],posepoint[1],img,orange_color)
    draw_line(posepoint[5], posepoint[1], img, red_color)

    draw_line(posepoint[22], posepoint[19], img, red_color)  # 지평면
    ground_point = posepoint[8]
    lslope = slope(posepoint[22], posepoint[19])

    #    y = slope*(x-ground_point.get('x')) + ground_point('y') #ground포인트를 시작점으로하는 선형 방정식을 정리하면 아래와 같다
    y = posepoint[15].get('y')
    x = lslope * (y - ground_point.get('y')) + ground_point.get('x')
    top_point = {'x': x, 'y': y}
    # draw_angle(posepoint[1], posepoint[8], top_point, result)

    draw_line(posepoint[12], posepoint[13], img, red_color)
    draw_line(posepoint[13], posepoint[14], img, red_color)

    # 척추와 골반--
    draw_line(posepoint[1], posepoint[8], img, blue_color)
    draw_line(posepoint[9], posepoint[12], img, blue_color)
    draw_angle(posepoint[12], posepoint[13], posepoint[14], img)  # 좌측(그림에서 우측)무릎의 굽혀짐


def draw_image(pose_img, pose_idx,posepoints):
    adress_idx = pose_idx[0]
    takeAway_idx = pose_idx[1]
    top_idx = pose_idx[2]
    down_idx = pose_idx[3]
    impact_idx = pose_idx[4]
    follow_through = pose_idx[5]
    finish = pose_idx[6]
    draw_address(pose_img[0], posepoints[adress_idx])
    draw_takeAway(pose_img[1], posepoints[takeAway_idx])
    draw_top(pose_img[2], posepoints[top_idx])
    draw_down(pose_img[3], posepoints[down_idx])
    draw_impact(pose_img[4], posepoints[impact_idx])
    draw_follow_through(pose_img[5], posepoints[follow_through])
    draw_finish(pose_img[6], posepoints[finish])


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

def get_slope(p1, p2):
    p1x = p1.get('x')
    p1y = p1.get('y')
    p2x = p2.get('x')
    p2y = p2.get('y')
    radian = get_slope_R(p1x, p1y, p2x, p2y)
    andgle = radian * (180 / math.pi)
    return andgle

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

def slope(p1, p2):
    if (p1.get('x') == p2.get('x')):
        return 0
    else:
        return (p2.get('y') - p1.get('y')) / (p2.get('x') - p1.get('x'))