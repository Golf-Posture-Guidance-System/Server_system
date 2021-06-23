import os
import sys
sys.path.append(os.pardir)  # 부모 디렉터리의 파일을 가져올 수 있도록 설정
from module.classify import *
from module.draw import *
from module.assess import *

global score
global feedback_list
global error
# date = os.system('date')
filepath = '../openpose/examples/media/'
filename = 'TestGolf'
vidname = filepath + filename + '.mp4'
# 아래 주석풀면 gpu 과부하걸리니 최초 실행시만
path = os.system(
    '../openpose/build/examples/openpose/openpose.bin --video ' '../openpose/examples/media/TestGolf.mp4 --write_json output/ --display 0 --render_pose 0')
size, frame = get_frame(vidname)
posepoints, error = get_keypoints(filename, size)
pose_idx, error = pose_classifier(posepoints)  # 포즈 분류하기
pose_img = cut_vid(frame, pose_idx)  # pose_img 는 리스트 입니다..
draw_image(pose_img, pose_idx, posepoints)  # 골격 그리기
image = cut_img(posepoints, pose_img, pose_idx, 0)  # 서버에 전송할 7가지 이미지 자르기(포즈 자세히 부분에 사용자에게 보여줄거)
score, feedback_list = assess_pose(posepoints, pose_idx)  # 포즈 평가하기