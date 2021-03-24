#!/usr/bin/env python
# coding: utf-8

# In[3]:


import cv2
import json
import math

INF = 9999

pose_idx = [20,37,53,68,69,75,90] #어,테,탑,다운,임펙,팔스,피니쉬 가 저장된 걸 반환받았다
############################3
vidcap = cv2.VideoCapture("golf.mp4")
frame=[]
while True:
    success,image = vidcap.read()
    if not success:
          break
    frame.append(image.copy())
size = len(frame)
###########################
def get_keypoints(vidname):
    posepoints = []
    for i in range(size): # 0~num i를 1씩 증가시키면서 반복
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


# In[4]:


def cut_vid(frame,pose_index):
    poseimg = [] #mat타입의 이미지가 저장 될 리스트
    for i in pose_index:
        poseimg.append(frame[i])
    return poseimg


# In[6]:


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


# In[7]:


def cut_img(posepoints,pose_img,pose_index,size):
    centers=[] #프레임별로 몸 중심(8번관절)이 따로 필요하여 리스트로..
    s=int(get_humansize(posepoints))*3
    for i in pose_index: #어드래스가 있는 프레임,테잌어웨이프레임.. 등등 순회
        centers.append((posepoints[i][8].get('x'),posepoints[i][8].get('y')))
    for idx in range(0,6):#0,1,2,3,4,5,6 선형의 시간복잡도
        img=pose_img[idx]
        x, y = centers[idx][0],centers[idx][1]
        num = str(idx)
        print("결과 이미지 크기는",s*2)
        #여기에--- 모바일 영상 전송시 사이즈 조절 팔요시 size 매개변수로 ! 코드작성
        roi = img[int(y-s):int(y+s), int(x-s):int(x+s)].copy()
                  #[y시작:y끝             ,x시작:x끝]
        cv2.imshow("new"+num, roi)
        #필요시 image저장코드 :
        #fname = "{}.jpg".format("{0:05d}")
        #cv2.imwrite('result'+num+fname, image) # save frame as JPEG file
    cv2.waitKey()
    cv2.destroyAllWindows()


# In[10]:


posepoints = get_keypoints("front_wo")
pose_img = cut_vid(frame,pose_idx)
cut_img(posepoints,pose_img,pose_idx,0)


# In[ ]:




