from module.set_data import *

def check_chiken_wing(posepoints, pose_idx):
    follow_through_idx = pose_idx[5]
    follow_through = posepoints[follow_through_idx]
    deduction = 0  # 100점에서 차감할 점수의 초기값(음수로 리턴 될 스코어)

    angle = abs(get_angle(follow_through[5], follow_through[6], follow_through[7]))

    start_angle = get_slope(follow_through[6], follow_through[7])
    end_angle = get_slope(follow_through[6], follow_through[5])
    if (start_angle - end_angle) > 180:
        if angle > 175: #왼팔이 175정도라면 충분히 펴져있다고 판단.
            return 0
        deduction += 10
        bent = 180-angle #팔이 굽혀진 정도
        deduction += int(bent / 180 * 20)

    return -deduction


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
    follow_through = posepoints[follow_through_idx]

#탑과 피니쉬 비교 .
    spine_slope_top_swing = get_slope(top_point[8], top_point[1])
    spine_slope_follow_through = get_slope(follow_through[8], follow_through[1])

    dif_angle = abs(spine_slope_top_swing) - abs(spine_slope_follow_through)
    dif_angle = abs(dif_angle)  # 차이를 절대값으로 점수 계산

    if spine_slope_follow_through >= -90: # 팔로스루시 척추가 오른쪽으로 휘었으면 바디스웨이라고 판단.
        deduction += 15
        deduction += int(dif_angle)

    #print(dif_angle)
    deduction = int(deduction)
    return -deduction


def check_finish(posepoints, pose_idx):
    finish = pose_idx[6]
    deduction = 0  # 100점에서 차감할 점수의 초기값(음수로 리턴 될 스코어)

    finish_point = posepoints[finish]
    r_sholder = finish_point[2]
    l_sholder = finish_point[5]
    if r_sholder.get('x') > l_sholder.get('x'):  #피니쉬 후 어깨가 완전히 돌아가 있는경우
        slope = get_slope(r_sholder,l_sholder)
        pelvic_length = get_distan(finish_point[9],finish_point[12])  #골반 길이
    else:  #피니쉬 이후에도 어깨가 돌아가지않음
        deduction += 20
        slope = get_slope(r_sholder, l_sholder)
        distortion = abs(90 + slope)  #어깨 뒤틀림 정도
        deduction += int(distortion/90 * 20)

    return -deduction



def additional_point(posepoints, pose_idx):
    #가산점 부여 : 1. 스윙의 시퀀스 속도가 매우 빠른 경우 (프로인 경우)
    point = 0
    sequence = pose_idx[5] - pose_idx[1]
    if sequence <= 20 :
        point += 10
    elif sequence <= 30 :
        point += 5
    return point


def assess_pose(posepoints, pose_idx):
    cscore = check_chiken_wing(posepoints, pose_idx)
    bscore = check_body_sway(posepoints, pose_idx)
    fscore = check_finish(posepoints, pose_idx)
    additional = additional_point(posepoints, pose_idx)
    score_list = [cscore, bscore, fscore,additional]  # 가장 심각한 실수가 어떤것지 찾기위해
    worst = score_list.index(min(score_list))  # 사용자에게 보여줄 가장 심한 실수의 인덱스를 찾는다.

    if worst == 0:  # check_chiken_wing 이 가장 심각한 실수
        # 서버에 문제가 있는 헤드업 사진을 전송하기
        # 의견 : 임팩트 이후에 헤드업이 발생한 부분에 그림더 그려줘서 보내는 방식
        print("치킨윙이 발생했네요 팔로스루시 팔을 폅시다.")
        a = 0
    elif worst == 1:  # 바디 스웨이가 가장 심각한 실수
        # 서버에 문제가 있는 헤드업 사진을 전송하기
        # 의견 : 임팩트 이후에 헤드업이 발생한 부분에 그림더 그려줘서 보내는 방식
        print("바디 스웨이가 발생했네요 스윙시에 몸이 자꾸 움직이면 정확도를낮춥니다.")
    elif worst == 2:  # 아쉬운 피니쉬동작이 심각한 경우
        # 서버에 문제가 있는 헤드업 사진을 전송하기
        # 의견 : 임팩트 이후에 헤드업이 발생한 부분에 그림더 그려줘서 보내는 방식
        print("피니쉬를 할때 몸을 더 비튼다면 비거리가 증가할거예요 .")

#----------- 점수 계산 --------------
    total_score = 100
    for i in score_list:
        total_score = total_score + i
        # 100점에서 발생한 실수만큼 뺀다

    print("당신의 포즈 점수는")
    print(total_score)
    return score_list