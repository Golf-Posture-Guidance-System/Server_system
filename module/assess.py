from module.set_data import *

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

    deduction = 0  # 100점에서 차감할 점수의 초기값(음수로 리턴 될 스코어)

    top_point = posepoints[top_idx]
    finish_point = posepoints[finish_idx]

#탑과 피니쉬 비교 .
    spine_angle_top_swing = get_angle(top_point[1], top_point[8], top_point[12])
    spine_angle_finish = get_angle(finish_point[1], finish_point[8], finish_point[12])
    dif_angle = abs(spine_angle_finish) - abs(spine_angle_top_swing)

    spine_slope_top_swing = get_slope(top_point[1],top_point[8])
    spine_slope_finish = get_slope(finish_point[1],finish_point[8])
    dif_angle = abs(spine_slope_top_swing) - abs(spine_slope_finish)
    #print(spine_slope_top_swing)
    #print(spine_slope_finish)

    dif_angle = abs(dif_angle)  # 차이를 절대값으로 점수 계산

    print(dif_angle)
    if dif_angle > 15:
        deduction = 50 # 차 > 15
    elif dif_angle <= 15:
        if dif_angle < 13 :
            if dif_angle < 10 :
                deduction = 0 # 차 < 10
            else :
                deduction = 10 # 10 <= 차 < 13
        else :
            deduction = 30 # 13 <= 차 <= 15

    deduction = int(deduction)
    return -deduction


def check_chickin_wing(posepoints, pose_idx):
    dress_idx = pose_idx[0]
    take_away_idx = pose_idx[1]
    top_idx = pose_idx[2]
    down_idx = pose_idx[3]
    impact_idx = pose_idx[4]
    follow_through = pose_idx[5]
    finish = pose_idx[6]



    return 0

def additional_point(posepoints, pose_idx,soroe):
    #가산점 부여 : 1. 스윙의 시퀀스 속도가 매우 빠른 경우 (프로인 경우)
    point = 0
    sequence = pose_idx[5] - pose_idx[1]
    if sequence <= 44 :
        point += 10
    elif sequence <= 30 :
        print += 5
    return point




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

#----------- 점수 계산 --------------
    total_score = 100
    for i in score_list:
        total_score = total_score + i
        # 100점에서 발생한 실수만큼 뺀다
    #부가적인 가산점을 더해준다.
    print("가산점 부여 전")
    print(total_score)
    total_score += additional_point(posepoints, pose_idx,total_score)

    print("당신의 포즈 점수는")
    print(total_score)
    return total_score