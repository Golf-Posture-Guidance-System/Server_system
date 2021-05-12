#!/usr/bin/env python
# coding: utf-8

# In[1]:


import sys, os
sys.path.append(os.pardir)  # 부모 디렉터리의 파일을 가져올 수 있도록 설정
import json
from module.set_data import *
sys.path.append(os.pardir)  # 부모 디렉터리의 파일을 가져올 수 있도록 설정


# In[3]:


def get_keypoints(vidname,size):
    posepoints = []
    for i in range(size+1): # 0~num i를 1씩 증가시키면서 반복
        num = format(i,"012") # 0000000000000 문자열로 저장(12자리 0)
        jfilename = vidname +"_"+num +"_keypoints.json"
        with open('json/'+jfilename, 'r') as f:
            json_data = json.load(f)  # json파일 불러오기댐
            # 첫번째 사람만 본다. 2명일때 예외처리 나중에해야
            keypoint = {'x': 0, 'y': 0, 'c': 0}  # 마지막 c는 신뢰도..0.3이하면 신뢰하지 않는다
            posepoint = []

            if not json_data['people'] : #openpose의 output은 물체에 사람이 잡히지 않을경우 poeple배열을 비운다. 빈 리스트인지 확인하는 코드
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

def get_slope(x1,y1,x2,y2): #두 점의 좌표를 가지고 기울기를 구하는 함수 (이번 코드에는 사용하지 않았음 ㅎㅎ;)
    if x1 != x2: #분모가 0이되는 상황 방지
        radian = math.arctan((y2-y1)/(x2-x1))
    return radian

def get_distan(point1,point2): #두 점 사이의 거리를 구하는 공식
    a = point1.get('x') - point2.get('x')
    b = point2.get('y') - point2.get('y')
    return math.sqrt((a*a) + (b*b))

def get_angle(joint1,joint2,joint3): #두 몸체의 기울기를 가지고 관절의 각도를구하는 함수      locate ->  j1 ------ j2 ------- j3
    if(joint1.get('x')-joint2.get('x')) == 0:
        return 0
    if(joint3.get('x')-joint2.get('x')) == 0:
        return 0
    radi1 = math.atan2((joint1.get('y')-joint2.get('y')),(joint1.get('x')-joint2.get('x')))
    radi2 = math.atan2((joint3.get('y')-joint2.get('y')),(joint3.get('x')-joint2.get('x')))
    radian = radi1-radi2
    #print(radian)
    andgle = radian * (180 / math.pi)
    return abs(andgle) #각도를절댓값으로 변환 ^^

def cut_frame(posepoints) : #프레임을 어깨 각도를 통해 인식
    size = len(posepoints)
    flag = [0,0,0,  #[0. 어드래스, 1테이크어웨이,2백스윙
            0,0,0]  # 3탑,4 다운스윙,5 임팩트]

    left_wrist = get_y_wrist(posepoints,'left')
    right_wrist = get_y_wrist(posepoints, 'right')
    
    
    where_top = left_wrist.index(min(left_wrist)) #손목의 높이가 최대가 되는 곳을 리턴 (y축이 작을 수록 상단에 위치)
    print(where_top)
    where_top = right_wrist.index(min(right_wrist))  # 손목의 높이가 최대가 되는 곳을 리턴
    print(where_top)

    for i in range(size) :
        posepoint = posepoints[i] #i번째 프레임의 몸체 좌표를 저장
        if (is_adress(posepoint))  and (flag[1] ==0) :
            flag[0] = 1
            #print("어드래스!")
        if (flag[0] == 1) and (is_takeAway(posepoint)) and flag[2] == 0:
            flag[2] = 1
            #print("테이크어웨이")

        #angle_left_houlder = get_angle(posepoints[i][1], posepoints[i][2], posepoints[i][3])
        #angle_right_shoulder = get_angle(posepoints[i][1], posepoints[i][5], posepoints[i][6])
        #if(angle_right_shoulder <= 50) or (angle_left_shoulder <= 50):
         #   print("어드래스 시작")
        #else :
         #   print("?")

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
            
def is_adress(posepoint) : #손과 어깨의 연결이 예각삼각형이여야한다
    left_hand = posepoint[4]
    right_hand = posepoint[7]
    head_size = get_distan(posepoint[17], posepoint[18])
    hand_dis = get_distan(posepoint[4], posepoint[7])
    left_elbow_angel = get_angle(posepoint[2], posepoint[3],posepoint[4])
    right_elbow_angle = get_angle(posepoint[5], posepoint[6],posepoint[7])

    if head_size >= hand_dis : #머리 크기보다 손목사이의 거리가 좁으면 모아져 있다고 판단
        #print("손이 모아져 있습니다.")
        if (left_elbow_angel >= 160) and (right_elbow_angle >= 160):
            #print("팔꿈치가 펴져있습니다.")
            #좌 우 팔꿈치가 어느정도 펴져 있어야 한다.
            return True

def is_takeAway(posepoint) :
    head_size = get_distan(posepoint[17], posepoint[18])
    hand_dis = get_distan(posepoint[4], posepoint[7])

    if  head_size >= hand_dis : #머리 크기보다 손목사이의 거리가 좁으면 모아져 있다고 판단
        if posepoint[7].get('x') > posepoint[8].get('y'):
            #우측 팔목의 x축 배꼽아래보다 좌측에 있다.
            #print("손이 배꼽 아래에 있다.")
            return True

def is_top(l_wrist,r_wrist):
    x_values = []
    y_values = []
    for i in range(0,l_wrist.len):
        x_values.append(l_wrist[i])
        y_values.append(i)
    plt.plot(x_values,y_values)
    plt.show()
    return True

def get_head(posepoints):
    l_ear =posepoints[1][17]
    r_ear =posepoints[1][18]
    
    size = get_distan(l_ear,r_ear)
    print(size)
    return int(size)





# In[ ]:




