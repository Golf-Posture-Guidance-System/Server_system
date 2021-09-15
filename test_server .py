import os
import sys
sys.path.append(os.pardir)  # 부모 디렉터리의 파일을 가져올 수 있도록 설정
from module.classify import *
from module.draw import *
from module.new_assess import *


INF = 10000
error = 0



filename = 'badpose'
vidname = filename + '.mp4'
pathname = 'examples/media/' + vidname
# 아래 주석풀면 gpu 과부하걸리니 최초 실행시만
#path = os.system('../openpose/build/examples/openpose/openpose.bin --video ' + pathname +  ' --write_json output/ --display 0 --render_pose 0 --frame_rotate=270')
size, frame = get_frame(vidname,pathname)
posepoints = get_keypoints(filename, size)
pose_idx = pose_classifier(posepoints)  # 포즈 분류하기
pose_img = cut_vid(frame, pose_idx)  # mat이미지 반환받기
draw_image(posepoints,pose_img, pose_idx)  # 골격 그리기
cut_img(posepoints, pose_img, pose_idx, 0)  # 서버에 전송할 7가지 이미지 자르기(포즈 자세히 부분에 사용자에게 보여줄거)
real_total, convert_score_list, feedback_list = assess_pose(posepoints, pose_idx) #포즈 평가하기
#worst의 경우.  [1 : 치킨윙 발생 , 2:바디스웨이 발생 , 3:탑스윙 구현 x]  # 가장 심각한 실수가 어떤것지 찾기위해