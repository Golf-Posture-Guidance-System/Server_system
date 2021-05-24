import math
import cv2
from module.set_data import *
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
        else:
            roi = img[int(y-haf_size):int(y+haf_size), int(x-haf_size):int(x+haf_size)].copy()
            #        [y시작:y끝             ,x시작:x끝]
            img = roi.copy()
            img = imutils.resize(img, width=600)
        #cv2.imshow("new" + num, img)
    cv2.waitKey()
    cv2.destroyAllWindows()


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
    draw_line(posepoint[2],posepoint[1],img,orange_color)
    draw_line(posepoint[5], posepoint[1], img, red_color)
    # 척추와 골반--
    draw_line(posepoint[1], posepoint[8], img, blue_color)
    draw_line(posepoint[9], posepoint[12], img, blue_color)

    draw_angle(posepoint[5], posepoint[6], posepoint[7], img)
    draw_angle(posepoint[1], posepoint[5], posepoint[6], img)


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


def draw_image(posepoints,pose_img, pose_idx):
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