import os
import cv2
import json
import math
import sys
import imutils
from matplotlib import pyplot as plt
from PIL import ImageFont, ImageDraw, Image

INF = 10000

def get_frame(vidname): #모든 프레임을 다 저장. 따라서 경량화 하여 오버헤드 줄일 수 있다.
    pathname = 'examples/media/' + vidname
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

def get_keypoints(filename,size):
    posepoints = []
    for i in range(size): # 0~num i를 1씩 증가시키면서 반복
        num = format(i,"012") #0000000000000 문자열로 저장(12자리 0)
        jFileName = filename +"_"+num +"_keypoints.json"
        with open('output/'+jFileName, 'r') as f:
            json_data = json.load(f)  # json파일 불러오기댐
            # 첫번째 사람만 본다. 2명일때 예외처리 나중에해야
            keypoint = {'x': 0, 'y': 0, 'c': 0}  # 마지막 c는 신뢰도..0.3이하면 신뢰하지 않는다
            posepoint = []

            if not json_data['people']: #openpose의 output은 물체에 사람이 잡히지 않을경우 poeple배열을 비운다. 빈 리스트인지 확인하는 코드
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

def cut_vid(frame,pose_index):
    poseimg = [] #mat타입의 이미지가 저장 될 리스트
    for i in pose_index:
        poseimg.append(frame[i])
    return poseimg

def get_distan(point1,point2): #두 점 사이의 거리를 구하는 함수
    a = point1.get('x') - point2.get('x')
    b = point2.get('y') - point2.get('y')
    return math.sqrt((a*a) + (b*b))

def get_humansize(posepoints): #인체 골격의 크기 구하기
    top=posepoints[0][15]
    bot=posepoints[0][19]
    hight = get_distan(top,bot)
    add = get_distan(posepoints[0][0],posepoints[0][1])
    return hight+add

def cut_img(posepoints,pose_img,pose_index,size):
    centers=[] #프레임별로 몸 중심(8번관절)이 따로 필요하여 리스트로..
    s=int(get_humansize(posepoints))*3
    for i in pose_index: #어드래스가 있는 프레임,테잌어웨이프레임.. 등등 순회
        centers.append((posepoints[i][8].get('x'),posepoints[i][8].get('y')))
    for idx in range(0,7):#0,1,2,3,4,5,6 선형의 시간복잡도
        img=pose_img[idx]
        x, y = centers[idx][0],centers[idx][1]
        num = str(idx)
        #print("결과 이미지 크기는",s*2)
        #여기에--- 모바일 영상 전송시 사이즈 조절 팔요시 size 매개변수로 ! 코드작성
        #roi = img[int(y-s):int(y+s), int(x-s):int(x+s)].copy()
                  #[y시작:y끝             ,x시작:x끝]
        #pose_img[idx] = roi
        img = imutils.resize(img, width=500)
        cv2.imshow("new"+num, img)
        #필요시 image저장코드 :
        #fname = "{}.jpg".format("{0:05d}")
        #cv2.imwrite('result'+num+fname, roi) # save frame as JPEG file
    cv2.waitKey()
    cv2.destroyAllWindows()

def get_center(point1,point2) :
    x1 = point1.get('x')
    y1 = point1.get('y')
    x2 = point2.get('x')
    y2 = point2.get('y')

    center_point = {'x': (x2+x1)/2,'y':  (y2+y1)/2 }
    return center_point

def draw_angle(p1,p2,p3,img):
    red_color = (0, 0, 255)
    px2 = p2.get('x')
    py2 = p2.get('y')
    px2 = int(px2)
    py2 = int(py2)
    px1 = p1.get('x')
    py1 = p1.get('y')
    px3 = p1.get('x')
    py3 = p3.get('y')

    if (px1 == 0 or py1 == 0 or px2 == 0 or py2 == 0 or px3 == 0 or py3 ==0):
        return
    circle_angle = 0
    angle = abs(get_angle(p1,p2,p3))

    start_angle = get_slope(p2, p3)
    end_angle = get_slope(p2, p1)
    if (start_angle-end_angle) > 180 :
        start_angle = get_slope_R1(p2, p3)
        end_angle = get_slope_R1(p2, p1)
        circle_angle = -180

    cv2.ellipse(img, (px2, py2), (18, 18), circle_angle, start_angle, end_angle, red_color, 2)

def draw_line (p1,p2,img,color) :
    sx = int(p1.get('x'))
    sy = int(p1.get('y'))
    fx = int(p2.get('x'))
    fy = int(p2.get('y'))
    if sx == 0 or sy == 0 or  fx ==0 or fy ==0 :
        return

    cv2.line(img, (sx, sy), (fx, fy), color, 2)

def draw_point_line(p1,p2,img) :
    sx = int(p1.get('x'))
    sy = int(p1.get('y'))
    fx = int(p2.get('x'))
    fy = int(p2.get('y'))
    grey_color = (211, 211, 211)

    cv2.line(img, (sx, sy), (fx, fy), grey_color,2,8)

def draw_adress(img, posepoint) : #어드래스 이미지 골격을 그리는 함수
    red_color = (0, 0, 255)
    black_color = (0, 0, 0)
    blue_color = (255, 165, 0)

    lsx = int(posepoint[2].get('x')) #왼어깨x좌표 아래쭉 어
    lsy = int(posepoint[2].get('y'))

    rsx = int(posepoint[5].get('x'))  #오른쪽 어깨
    rsy = int(posepoint[5].get('y') + 50)
    rsy2 = int(posepoint[5].get('y') - 50)
    lsy = int(posepoint[2].get('y') + 50)
    lsy2 = int(posepoint[2].get('y') - 50)




    left_angle = get_angle(posepoint[5],posepoint[2],posepoint[4])
    right_angle = get_angle(posepoint[2],posepoint[5],posepoint[7])

    draw_line(posepoint[2], posepoint[5], img,red_color)
    draw_line(posepoint[5], posepoint[7], img,red_color)
    draw_line(posepoint[2], posepoint[4], img,red_color)
    draw_line(posepoint[22],posepoint[19],img, blue_color)
    draw_angle(posepoint[1], posepoint[2], posepoint[4], img)
    draw_angle(posepoint[2], posepoint[5], posepoint[7], img)
    cv2.line(img, (rsx,rsy), (rsx,rsy2), blue_color, 2) #발 너비와 어깨 너비 비교
    cv2.line(img, (lsx,lsy), (lsx,lsy2), blue_color, 2)
    cv2.putText(img, str(int(left_angle)) + "도", (lsx - 50, lsy), cv2.FONT_HERSHEY_SIMPLEX, 0.5, black_color, 2)


def draw_takeAway(img, posepoint):
    red_color = (0, 0, 255)
    black_color = (0, 0, 0)

    lsx = int(posepoint[2].get('x'))  # 왼어깨x좌표 아래쭉 어
    lsy = int(posepoint[2].get('y'))

    left_angle = get_angle(posepoint[5], posepoint[2], posepoint[4])
    right_angle = get_angle(posepoint[2], posepoint[5], posepoint[7])

    draw_line(posepoint[2], posepoint[5], img,red_color)
    draw_line(posepoint[5], posepoint[7], img,red_color)
    draw_line(posepoint[2], posepoint[4], img,red_color)
    draw_angle(posepoint[1], posepoint[2], posepoint[4], img)
    draw_angle(posepoint[2], posepoint[5], posepoint[7], img)
    cv2.putText(img, str(int(left_angle)) + "도", (lsx - 50, lsy), cv2.FONT_HERSHEY_SIMPLEX, 0.5, black_color, 2)

def draw_top(img, posepoint):
    result = img
    red_color = (0, 0, 255)
    blue_color = (255, 165, 0)

    rhx = int(posepoint[12].get('x')) #오른쪽 골반 x 좌표
    rhy = int(posepoint[12].get('y'))
    rkx = int(posepoint[13].get('x')) #오른쪽 무릎
    rky = int(posepoint[13].get('y'))
    rax = int(posepoint[14].get('x')) #오른쪽 발목
    ray = int(posepoint[14].get('y'))



    right_leg_angle = get_angle(posepoint[12],posepoint[13],posepoint[14])
    start_angle = (math.atan2(rhy-rky, rhx-rkx)) * (180/math.pi)
    end_angle = (math.atan2(ray-rky,rax-rkx) * (180/math.pi))

    draw_line(posepoint[1],posepoint[8], result, blue_color)
    draw_line(posepoint[19],posepoint[22], result, blue_color)
    result = cv2.line(result, (rhx,rhy), (rkx,rky), red_color, 2)
    result = cv2.line(result, (rkx, rky), (rax,ray), red_color,2)
    result = cv2.ellipse(result, (rkx, rky), (18,18), 0 , start_angle, end_angle, red_color, 2)

def draw_down (img, posepoint):
    result = img
    red_color=(0,0,255)
    orange_color = (255, 165, 0)

    rhx = int(posepoint[12].get('x'))  # 오른쪽 골반 x 좌표
    rhy = int(posepoint[12].get('y'))
    rkx = int(posepoint[13].get('x'))  # 오른쪽 무릎
    rky = int(posepoint[13].get('y'))
    rax = int(posepoint[14].get('x'))  # 오른쪽 발목
    ray = int(posepoint[14].get('y'))

    right_leg_angle = get_angle(posepoint[12], posepoint[13], posepoint[14])
    start_angle = (math.atan2(rhy - rky, rhx - rkx)) * (180 / math.pi)
    end_angle = (math.atan2(ray - rky, rax - rkx) * (180 / math.pi))

    # 척추와 골반--
    draw_line(posepoint[1], posepoint[8], img,orange_color)
    draw_line(posepoint[9], posepoint[12], img,orange_color)

    result = cv2.line(result, (rhx, rhy), (rkx, rky), red_color, 2)
    result = cv2.line(result, (rkx, rky), (rax, ray), red_color, 2)
    result = cv2.ellipse(result, (rkx, rky), (18, 18), 0, start_angle, end_angle, red_color, 2)

def draw_impact (img, posepoint):
    result = img
    red_color = (0,0,255)
    orange_color = (255, 165, 0)

    lhx = int(posepoint[9].get('x'))  # 왼쪽 골반 x 좌표
    lhy = int(posepoint[9].get('y'))
    lkx = int(posepoint[10].get('x'))  # 왼쪽 무릎
    lky = int(posepoint[10].get('y'))
    lax = int(posepoint[11].get('x'))  # 왼쪽 발목
    lay = int(posepoint[11].get('y'))

    left_leg_angle = get_angle(posepoint[9], posepoint[10], posepoint[11])
    start_angle = (math.atan2(lay - lky, lax - lkx)) * (180/math.pi)
    end_angle = (math.atan2(lhy - lky, lhx - lkx)) * (180/math.pi)


    result = cv2.line(result, (lhx, lhy), (lkx, lky), red_color, 2)
    result = cv2.line(result, (lkx, lky), (lax, lay), red_color, 2)

    # 척추와 골반--
    draw_line(posepoint[1], posepoint[8], img,orange_color)
    draw_line(posepoint[9], posepoint[12], img,orange_color)
    result = cv2.ellipse(result, (lkx, lky), (18, 18), 0, start_angle, 360 + end_angle, red_color, 2)

def draw_follow_through(img, posepoint):
    result = img
    red_color = (0, 0, 255)
    blue_color = (255, 165, 0)
    orange_color = (0, 165, 255)

    draw_line(posepoint[5],posepoint[6],img,red_color)
    draw_line(posepoint[6],posepoint[7],img,red_color)
    draw_line(posepoint[1],posepoint[5],img,orange_color)
    draw_line(posepoint[2], posepoint[1], img, orange_color)
#척추와 골반--
    draw_line(posepoint[1], posepoint[8], img,blue_color)
    draw_line(posepoint[9], posepoint[12], img,blue_color)

    draw_angle(posepoint[5],posepoint[6],posepoint[7],result)
    draw_angle(posepoint[1], posepoint[5], posepoint[6], result)

def draw_finish(img, posepoint):
    result = img
    red_color = (0, 0, 255)
    orange_color = (255, 165, 0)

    draw_line(posepoint[1],posepoint[8],img,orange_color)
    draw_line(posepoint[9],posepoint[12],img,orange_color)

    draw_line(posepoint[22], posepoint[19], img,red_color) # 지평면
    ground_point= posepoint[8]
    lslope = slope(posepoint[22],posepoint[19])

#    y = slope*(x-ground_point.get('x')) + ground_point('y') #ground포인트를 시작점으로하는 선형 방정식을 정리하면 아래와 같다
    y = posepoint[15].get('y')
    x = lslope*(y - ground_point.get('y')) + ground_point.get('x')
    top_point = {'x' : x, 'y' : y}
    draw_point_line(ground_point, top_point, img)  # 지평면
    #draw_angle(posepoint[1], posepoint[8], top_point, result)

def draw_image(pose_img, pose_idx) :
    adress_idx = pose_idx[0]
    takeAway_idx = pose_idx[1]
    top_idx = pose_idx[2]
    down_idx = pose_idx[3]
    impact_idx = pose_idx[4]
    follow_through = pose_idx [5]
    finish = pose_idx[6]

    draw_adress(pose_img[0], posepoints[adress_idx])
    draw_takeAway(pose_img[1], posepoints[takeAway_idx])
    draw_top(pose_img[2], posepoints[top_idx])
    draw_down(pose_img[3], posepoints[down_idx])
    draw_impact(pose_img[4], posepoints[impact_idx])
    draw_follow_through(pose_img[5],posepoints[follow_through])
    draw_finish(pose_img[6],posepoints[finish])

#-______________________
def slope (p1, p2) :
    if(p1.get('x') == p2.get('x')):
        return 0
    else :
        return (p2.get('y') - p1.get('y'))/(p2.get('x')-p1.get('y'))

def get_slope_R (x1,y1,x2,y2): #두 점의 좌표를 가지고 기울기를 구하는 함수 (이번 코드에는 사용하지 않았음 ㅎㅎ;)
    if x1 != x2 : #분모가 0이되는 상황 방지
        radian = math.atan2((y2-y1),(x2-x1))
        return radian
    else : return 0

def get_slope_R1 (p1,p2) :
    p1x = p1.get('x')
    p1y = p1.get('y')
    p2x = p2.get('x')
    p2y = p2.get('y')
    radian = math.atan((p2y-p1y)/(p2x-p1x))
    andgle = radian * (180 / math.pi)
    return andgle

def get_slope (p1,p2) :
    p1x = p1.get('x')
    p1y = p1.get('y')
    p2x = p2.get('x')
    p2y = p2.get('y')
    radian = get_slope_R(p1x,p1y,p2x,p2y)
    andgle = radian * (180 / math.pi)
    return andgle

def get_distan (point1,point2): #두 점 사이의 거리를 구하는 공식
    a = point1.get('x') - point2.get('x')
    b = point2.get('y') - point2.get('y')
    return math.sqrt((a*a) + (b*b))

def get_angle (joint1,joint2,joint3): #두 몸체의 기울기를 가지고 관절의 각도를구하는 함수      locate ->  j1 ------ j2 ------- j3
    if(joint1.get('x')-joint2.get('x')) == 0:
        return 0
    if(joint3.get('x')-joint2.get('x')) == 0:
        return 0
    radi1 = math.atan((joint1.get('y')-joint2.get('y'))/(joint1.get('x')-joint2.get('x')))
    radi2 = math.atan((joint3.get('y')-joint2.get('y'))/(joint3.get('x')-joint2.get('x')))
    radian = radi1-radi2
    #print(radian)
    angle = radian * (180 / math.pi)
    return angle

def get_y_wrist (posepoints, lr):
    # 손목 위치의 함수를 반환,프레임배열과, 왼오 옵
    y_point_arr = []
    if (lr == "left"):  # 왼
        for i in range(len(posepoints)):
            lwrist = posepoints[i][4].get('y')
            if (lwrist == 0):  # 이상치에서 최소 값을 봐야하므로 inf로 대체
                y_point_arr.append(INF)
            elif (posepoints[i][4].get('c') < 0.2):
                y_point_arr.append(INF)
            else:
                y_point_arr.append(lwrist)

    elif (lr == "right"):  # 오른손
        for i in range(len(posepoints)):
            rwrist = posepoints[i][7].get('y')
            if (rwrist == 0):  # 이상치에서 최소 값을 봐야하므로 inf로 대체
                y_point_arr.append(INF)
            elif (posepoints[i][4].get('c') < 0.2):
                y_point_arr.append(INF)
            else:
                y_point_arr.append(rwrist)
    return y_point_arr

def get_x_wrist (posepoints, lr):
    # 손목 위치의 함수를 반환,프레임배열과, 왼오 옵
    y_point_arr = []
    if (lr == "left"):  # 왼
        for i in range(len(posepoints)):
            lwrist = posepoints[i][4].get('x')
            if (lwrist == 0):  # 이상치에서 최소 값을 봐야하므로 inf로 대체
                y_point_arr.append(INF)
            elif (posepoints[i][4].get('c') < 0.2):
                y_point_arr.append(INF)
            else:
                y_point_arr.append(lwrist)

    elif (lr == "right"):  # 오른손
        for i in range(len(posepoints)):
            rwrist = posepoints[i][7].get('x')
            if (rwrist == 0):  # 이상치에서 최소 값을 봐야하므로 inf로 대체
                y_point_arr.append(INF)
            elif (posepoints[i][4].get('c') < 0.2):
                y_point_arr.append(INF)
            else:
                y_point_arr.append(rwrist)
    return y_point_arr

def get_axis(left_wrist,right_wrist): # 손목의 변화량을 찾기위한 그래프의 축 리스트 리턴
    lx_values, ly_values, rx_values, ry_values = [],[],[],[]
    for i in range(len(left_wrist)):  # left wrist와 right wrist가 같다
        if (left_wrist[i] != INF):  # inf값에는 포즈가 감지되지 않아 0값이 기록되어 있으므로 넘어간다.
            ly_values.append(left_wrist[i])
            lx_values.append(i)

        if (right_wrist[i] != INF):
            ry_values.append(right_wrist[i])
            rx_values.append(i)
    return lx_values, ly_values, rx_values, ry_values
# 순서대로 왼손좌표의 x축(프레임 변화), 왼손좌표의 y축(좌표변화),오른손x,y
def pose_classifier(posepoints,size):
    idx = [0, 0, 0, 0, 0, 0, 0] #어,테이크어웨이,탑,다운,임펙,팔로스루,피니쉬

# -------------- 손목의 x좌표 변화량 감지를 통해 스윙이 시작하는지(어드래스)감지)----
    left_wrist = get_x_wrist(posepoints, 'left')
    right_wrist = get_x_wrist(posepoints, 'right')

    lx_values, ly_values, rx_values, ry_values = get_axis(left_wrist,right_wrist)
    slopes = []
    for i in range(0, len(rx_values)):
        if (len(rx_values) - 1 == i):  # 마지막 점의 경우 변화량을 계산할 필요가 없음
            slopes.append(slope)
            break
        else:
            dx = rx_values[i + 1] - rx_values[i]
            dy = ry_values[i + 1] - ry_values[i]
            slope = dy / dx
            if (slope <= -8 and idx[0] == 0):  # 좌측으로 움직이면 x좌표의 변화량은 감소
                dx_left = lx_values[i + 1] - lx_values[i]
                dy_left = ly_values[i + 1] - ly_values[i]
                slope_left = dy_left / dx_left
                if (slope_left <= -8):
                    idx[0] = rx_values[i-1]
            slopes.append(slope)

# -------------- 손목의 y좌표 변화량 감지를 통해 포즈 분류 ----
    #테이커웨이,스윙 탑,입펙트값을 먼저 구한다.
    left_wrist = get_y_wrist(posepoints, 'left')
    right_wrist = get_y_wrist(posepoints, 'right')

    lx_values, ly_values, rx_values, ry_values = get_axis(left_wrist, right_wrist)

    l_downpoint = left_wrist[idx[0]]
    r_downpoint = right_wrist[idx[0]]
    for i in range(0, len(rx_values)):
        if (len(rx_values) - 1 == i):  # 마지막 점의 경우 변화량을 계산할 필요가 없음
            slopes.append(slope)
            break
        else:
            dx = rx_values[i + 1] - rx_values[i]
            dy = ry_values[i + 1] - ry_values[i] # 손목위치
            slope = dy / dx

            if (slope <= -8 and idx[0] != 0 and idx[1] == 0):  # 테이크어웨이 검사
                dx_left = lx_values[i + 1] - lx_values[i]
                dy_left = ly_values[i + 1] - ly_values[i]
                slope_left = dy_left / dx_left
                # print(slope_left)
                if (slope_left <= -8):
                    idx[1] = rx_values[i - 1]

            if (idx[1] != 0 and idx[2] == 0 and slope > 0):  # 탑 검사
                dx_left = lx_values[i + 1] - lx_values[i]
                dy_left = ly_values[i + 1] - ly_values[i]
                slope_left = dy_left / dx_left
                if (slope_left > 0):
                    idx[2] = rx_values[i - 1]
            if (idx[2] != 0 and idx[4] == 0 and slope < 0 and l_downpoint - 40 < ly_values[i] ):  # 임펙트(idx=4) 검사
                dx_left = lx_values[i + 1] - lx_values[i]
                dy_left = ly_values[i + 1] - ly_values[i]
                slope_left = dy_left / dx_left
                if (slope_left < 0 and r_downpoint - 40 < ry_values[i]):
                    idx[4] = rx_values[i]
            # if(idx[4]!=0 and idx[6]==0 and slope>0) : #피니쉬 검사 : 는 임팩트 이후의 손목 최대값으로 하기로 함..
            #    dx_left = lx_values[i+1] - lx_values[i]
            #    dy_left = ly_values[i+1] - ly_values[i]
            #    slope_left = dy_left/dx_left
            #    print(slope_left)
            #    if(slope_left>0):
            #        idx[6] = rx_values[i-1]
            slopes.append(slope)

    plt.scatter(lx_values, ly_values)
    plt.scatter(rx_values, ry_values)

    plt.legend(['left', 'right'])
   # plt.show()

    # -------------- 이후 피니쉬는 손목의 위치가 가장 높을때 이므로 (임팩트 이후의) 손목 높이의 최대값을 구한다.
    impact = idx[4]
    left_wrist = left_wrist[impact:]
    right_wrist = right_wrist[impact:]
    ltop = left_wrist.index(min(left_wrist))  # 손목의 높이가 최대가 되는 곳(영상의 프레임 인덱스)을 리턴 (y축이 작을 수록 상단에 위치)
    rtop = right_wrist.index(min(right_wrist))  # 손목의 높이가 최대가 되는 곳을 리턴
    ltop = ltop+impact
    rtop = rtop+impact
    if(rtop > idx[4]) : # 피니쉬라고 생각된느프레임이 임팩트 이후인지 확인
        idx[6] = rtop
    elif (ltop > idx[4]) : # 왼쪽손목의 최대높이를 피니쉬로 설정
        idx[6] = ltop
    else:
        idx[6] = -1 # 피니쉬를 찾을 수 없을때 -1 리턴
    # -------------- 이후 사이값으로 다운과 팔로스루 구하기
    idx[3] = int((idx[4] + idx[2]) / 2)
    idx[5] = int((idx[6] + idx[4]) / 2)


    return idx

#-----------
def assess_pose(posepoints,pose_idx):
    hscore = check_headup(posepoints,pose_idx)
    bscore = check_body_sway(posepoints,pose_idx)
    cscore = check_chickin_wing(posepoints,pose_idx)

    score_list = [hscore,bscore,cscore] #가장 심각한 실수가 어떤것지 찾기위해
    worst = score_list.index(min(score_list)) #사용자에게 보여줄 가장 심한 실수의 인덱스를 찾는다.

    if worst == 0 : #head_up이 가장 심각한 실수
        #서버에 문제가 있는 헤드업 사진을 전송하기
        #의견 : 임팩트 이후에 헤드업이 발생한 부분에 그림더 그려줘서 보내는 방식
        a=0
    elif worst == 1 : #바디 스웨이가 가장 심각한 실수
        # 서버에 문제가 있는 헤드업 사진을 전송하기
        # 의견 : 임팩트 이후에 헤드업이 발생한 부분에 그림더 그려줘서 보내는 방식
        a=1
    elif worst == 2 : #치킨윙이 심각한 경우
        # 서버에 문제가 있는 헤드업 사진을 전송하기
        # 의견 : 임팩트 이후에 헤드업이 발생한 부분에 그림더 그려줘서 보내는 방식
        a=2

    total_score = 100
    for i in score_list:
        total_score = total_score+i
        #100점에서 발생한 실수만큼 뺀다
    print(total_score)
    return total_score


def check_headup(posepoints,pose_idx):
    adress_idx = pose_idx[0]
    takeAway_idx = pose_idx[1]
    top_idx = pose_idx[2]
    down_idx = pose_idx[3]
    impact_idx = pose_idx[4]
    follow_through = pose_idx [5]
    finish = pose_idx[6]

    return 0

def check_body_sway (posepoints,pose_idx) :
    dress_idx = pose_idx[0]
    takeAway_idx = pose_idx[1]
    top_idx = pose_idx[2]
    down_idx = pose_idx[3]
    impact_idx = pose_idx[4]
    follow_through_idx = pose_idx[5]
    finish_idx = pose_idx[6]

    score = 0 #100점에서 차감할 점수의 초기값

    top_point = posepoints[top_idx]
    finish_point = posepoints[finish_idx]

    spine_angle_top = get_angle(top_point[1],top_point[8],top_point[12])
    spine_angle_finish = get_angle(finish_point[1], finish_point[8],finish_point[12])
    dif_angle = abs(spine_angle_finish) - abs(spine_angle_top)

    dif_angle = abs(dif_angle) #차이를 절대값으로 점수 계산

    if (dif_angle > 3.5):
        score = dif_angle * 10
    elif (dif_angle <= 3.5):
        score = dif_angle
    elif (dif_angle <= 1.5):
        score = 0
    score = int(score)
    #print(score)


    return -score

def check_chickin_wing(posepoints,pose_idx):
    dress_idx = pose_idx[0]
    takeAway_idx = pose_idx[1]
    top_idx = pose_idx[2]
    down_idx = pose_idx[3]
    impact_idx = pose_idx[4]
    follow_through = pose_idx[5]
    finish = pose_idx[6]

    return -30

filename = 'gpps'
vidname = filename+'.mp4'
pathname='examples/media/'+vidname
#아래 주석풀면 gpu 과부하걸리니 최초 실행시만
#path = os.system('../openpose/build/examples/openpose/openpose.bin --video ' + pathname +  ' --write_json output/ --display 0 --render_pose 0')
size,frame=get_frame(vidname)
posepoints = get_keypoints(filename,size)
pose_idx = pose_classifier(posepoints,size)  #포즈 분류하기

pose_img = cut_vid(frame, pose_idx)  #mat이미지 반환받기
draw_image(pose_img,pose_idx)   #골격 그리기
cut_img(posepoints, pose_img, pose_idx, 0) #서버에 전송할 7가지 이미지 자르기(포즈 자세히 부분에 사용자에게 보여줄거)
assess_pose(posepoints,pose_idx) #포즈 평가하기