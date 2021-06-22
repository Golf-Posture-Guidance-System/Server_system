from module.set_data import *
from real_server import *
import math

def check_chiken_wing(posepoints, pose_idx):
    follow_through_idx = pose_idx[5]
    follow_through = posepoints[follow_through_idx]
    deduction = 0  # 100점에서 차감할 점수의 초기값(음수로 리턴 될 스코어)
    chiken_wing = ""
    angle = abs(get_angle(follow_through[5], follow_through[6], follow_through[7]))

    start_angle = get_slope(follow_through[6], follow_through[7])
    end_angle = get_slope(follow_through[6], follow_through[5])
    if (start_angle - end_angle) > 180:
        if angle > 175: #왼팔이 175정도라면 충분히 펴져있다고 판단.
            return 0, chiken_wing
        deduction += 10
        bent = 180-angle #팔이 굽혀진 정도
        deduction += int(bent / 180 * 15)
        chiken_wing = "치킨윙이 발생했습니다. 왼팔을 충분히 펴주세요."
    return -deduction, chiken_wing


def check_body_sway(posepoints, pose_idx):
    dress_idx = pose_idx[0]
    take_away_idx = pose_idx[1]
    top_idx = pose_idx[2]
    down_idx = pose_idx[3]
    impact_idx = pose_idx[4]
    follow_through_idx = pose_idx[5]
    finish_idx = pose_idx[6]
    body_sway = ""
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
        body_sway = "바디 스웨이가 발생했네요 스윙시에 몸이 자꾸 움직이면 정확도를낮춥니다."
    #print(dif_angle)
    deduction = int(deduction)
    return -deduction, body_sway

def check_slice(posepoints, pose_idx):
    address = pose_idx[0]
    top = pose_idx[2]
    deduction = 0  # 100점에서 차감할 점수의 초기값(음수로 리턴 될 스코어)
    slice_advice = ""
    address_point = posepoints[address]
    top_point = posepoints[top]
    r_shoulder = address_point[2]
    l_shoulder = address_point[5]
    r_arm_angle = abs(get_angle(top_point[2],top_point[3],top_point[4]))
    if r_shoulder.get('y') < l_shoulder.get('y'): #오른쪽 어깨가 더 높을 때(원점에서 멀어질수록 y값 증가)
        distance = r_shoulder.get('y') - l_shoulder.get('y')
        deduction += int(distance * 0.5)
    if 80 < r_arm_angle or 90 > r_arm_angle: #탑스윙에서 오른쪽 팔꿈치의 각도는 90도가 적정(아닐시 슬라이스 발생 높다)
        dp = (90 - r_arm_angle) / 90 * 10
        deduction += int(dp)
        slice_advice = "탑스윙 시 오른쪽 팔꿈치가 직각을 유지하지 않습니다. 이는 슬라이스를 유발합니다."
        print(slice_advice)

    return -deduction, slice_advice

def check_address(poseoints, pose_idx):
    address = pose_idx[0]
    deduction = 0 # 100점에서 차감할 점수의 초기값(음수로 리턴 될 스코어)
    add_advice1 = ""
    add_advice2 = ""
    add_advice3 = ""
    address_point = poseoints[address]
    r_shoulder = address_point[2]
    l_shoulder = address_point[5]
    r_heel = address_point[24]
    l_heel = address_point[21]

    x = l_shoulder.get('x') - r_shoulder.get('x')
    y = l_shoulder.get('y') - r_shoulder.get('y')
    angle = abs(math.atan2(y, x) * 180 / math.pi)
    stance = l_heel.get('x') - r_heel.get('x')
    shoulder_width = l_shoulder.get('x') - r_shoulder.get('x') #스탠스를 위해 비교하는 수치
    if r_shoulder.get('y') > l_shoulder.get('y'): #오른쪽 어깨가 왼쪽어깨보다 낮을때 기울기
        if 8 > angle or 20 < angle : #14도가 적정 어깨 기울기(오차범위 6)
            lean = 14 - angle
            deduction += int(lean / 14 * 5)
            add_advice1 = "어드레스 셋 업 자세에서 오른쪽 어깨 기울기를 조절하세요."
            print(add_advice1)
    else : #오른쪽 어깨가 왼쪽 어깨보다 높은 경우
        deduction_point1 = (r_shoulder.get('y') - l_shoulder.get('y')) * 0.5 #차감포인트 1 : 오른쪽 어깨가 올라간 만큼 차감
        deduction_point2 = abs((angle)) * 0.5 #차감포인트 2 : 반대로 올라간 각도만큼 차감, 맘 약하니깐 반으로 줄여줌..
        deduction = int(deduction_point1 + deduction_point2)
        add_advice2 = "오른쪽 어깨가 왼쪽보다 높습니다. 오른쪽 어깨를 낮추세요"
        print(add_advice2)
    if stance < 5 or (stance - shoulder_width) > 5 : #발 너비 스탠스가 5보다 작은 경우(적정 스탠스 너비 5cm) 혹은 어깨 너비보다 너무 넓은 경우
        deduction += 5
        add_advice3 = "발의 너비를 어깨 너비만큼 조절하세요.(적정 너비 5cm)"
        print(add_advice3)

    return -deduction,add_advice1,add_advice2,add_advice3


def check_takeaway(posepoints, pose_idx):
    takeaway = pose_idx[1]
    deduction = 0  # 100점에서 차감할 점수의 초기값(음수로 리턴 될 스코어)
    taway_advice = ""
    takeaway_point = posepoints[takeaway]
    right_arm_angle = abs(get_angle(takeaway_point[2],takeaway_point[3],takeaway_point[4]))
    left_arm_angle = abs(get_angle(takeaway_point[5],takeaway_point[6],takeaway_point[7]))

    if right_arm_angle < 170 or left_arm_angle < 170 : #팔이 굽어져 있는 경우
        bent1 = 180 - right_arm_angle
        bent2 = 180 - left_arm_angle
        dp1 = int(bent1 / 180 * 5)
        dp2 = int(bent2 / 180 * 5)
        deduction += int(dp1 + dp2)
        taway_advice = "팔이 굽어져있습니다. 팔을 쭉 편 상태를 유지하며 스윙하세요."
        print(taway_advice)
    return -deduction, taway_advice

def check_topswing(posepoints, pose_idx):
    top = pose_idx[2]
    deduction = 0  # 100점에서 차감할 점수의 초기값(음수로 리턴 될 스코어)
    top_advice1 = ""
    top_advice2 = ""
    top_advice3 = ""
    top_advice4 = ""
    top_point = posepoints[top]
    
    r_ear = top_point[0]
    l_wrist = top_point[7]
    neck = top_point[1]
    waist = top_point[8]
    
    gradient = slope(waist, neck)
    l_arm_angle = abs(get_angle(top_point[5], top_point[6], top_point[7]))
    l_leg_angle = abs(get_angle(top_point[12], top_point[13], top_point[14]))
    pelvis_width = top_point[12].get('x') - top_point[9].get('x')
    knee_width = top_point[13].get('x') - top_point[10].get('x')

    if l_wrist.get('y') < r_ear.get('y'): #왼쪽 손목이 오른쪽 귀 위에 있으면 손목이 머리 부근에 있는 것이라 봄
        if l_arm_angle < 170 : #팔이 쭉 펴져있지 않은 경우
            bent = 170 - l_arm_angle
            deduction += int(bent / 170 * 5)
            top_advice1 = "탑스윙 시 왼쪽 팔을 쭉 펴세요."
            print(top_advice1)
    else : #손목이 머리 아래에 있을 때
        deduction += 10
        dp1 = (r_ear.get('y') - l_wrist.get('y')) * 0.5 #떨어진 위치만큼 차감
        if l_arm_angle < 170 :
            bent = 170 - l_arm_angle
            dp2 = int(bent / 170 * 5)
        deduction = int(dp1 + dp2)
        top_advice2 = "탑스윙 시 양 손을 머리 위로 올리고 팔을 쭉 편 상태로 스윙하세요."
        print(top_advice2)
    # 다리 각도 체크 : 왼쪽 다리를 굽히지만, 왼쪽 다리가 지나치게 구부려져
                # 오른쪽 무릎과 왼쪽 무릎이 가까이 맞닿은 상태가 되지 않아야 한다.
    if l_leg_angle > 170:
        bent = 170 - l_arm_angle
        dp1 = int(bent / 170 * 5)
        if knee_width < pelvis_width:
            dp1 += int(knee_width * 0.5)
        deduction += dp1
        top_advice3 = "무릎 구부림이 올바르지 않습니다. 오른쪽 다리에 체중을 싣고 왼쪽 무릎은 살짝만 구부리세요."
        print(top_advice3)
    
    # 척추 체크 : 척추 축의 기울임 체크
    if gradient < 0 : #척추 축 반대로 기울어짐
        deduction += 10
        deduction += int(gradient*0.5)
        top_advice4 = "척추의 축이 기울어져 있습니다. 하체 뒤로 더 빼주세요."
    
    return -deduction, top_advice1, top_advice2, top_advice3, top_advice4

def check_downswing(posepoints, pose_idx):
    
    top = pose_idx[2]
    down = pose_idx[3]
    
    deduction = 0  # 100점에서 차감할 점수의 초기값(음수로 리턴 될 스코어)
    
    down_advice = ""
    down_advice2 = ""
    down_point = posepoints[down]
    top_point = posepoints[top]
    right_arm_angle = abs(get_angle(down_point[2], down_point[3], down_point[4]))
    top_leg_angle = abs(get_angle(top_point[9], top_point[10], top_point[11]))
    down_leg_angle = abs(get_angle(down_point[9], down_point[10], down_point[11]))
    
    # early release 체크로 다운스윙시 오른팔의 각도가 빨리 풀리면 안된다. 탑스윙에서 오른팔 각도를 최대한 유지해야함
    if right_arm_angle > 105 : #오른쪽 팔꿈치의 변화량 최대 15도(그 이상일시 early release 발생)
        bent = down_leg_angle - 105
        dp = int(bent / 105 * 15)
        deduction += dp
        down_advice = "다운스윙 시 오른쪽 팔이 빨리 풀리는 early release가 발생했습니다."
        print(down_advice)

    if top_leg_angle >= down_leg_angle : #체중이 왼쪽으로 쏠리면서 오른쪽 다리는 굽혀져야 함
        deduction += 5
        bent = top_leg_angle - down_leg_angle
        dp = int(bent / top_leg_angle * 20)
        deduction += dp
        down_advice2 = "오다른쪽 다리가 펴져있습니다. 체중을 왼쪽에 싣고 오른쪽 다리는 굽히세요."
        
    return -deduction, down_advice, down_advice2

def check_impact(posepoints, pose_idx):
    impact = pose_idx[4]
    deduction = 0 #100점에서 차감할 점수의 초기값(음수로 리턴 될 스코어)
    imp_advice1 = ""
    imp_advice2 = ""
    imp_advice3 = ""
    impact_point = posepoints[impact]
    neck = impact_point[1]
    waist = impact_point[8]

    x = neck.get('x') - waist.get('x')
    y = neck.get('y') - waist.get('y')
    gradient = slope(waist, neck)

    right_leg_angle = abs(get_angle(impact_point[9], impact_point[10], impact_point[11]))
    angle = abs(math.atan2(y, x) * 180 / math.pi)
    angle = abs(90 - angle)

    if gradient > 0:  # 척추의 휘어짐이 올바르면 척추 각도를 본다
        if angle < 11 or angle > 15:  # 임팩트 시 척추의 각도는 13도가 적정(오차범위 2)
            bent = 13 - angle
            dp = int(bent / 13 * 10)
            deduction += dp
            imp_advice1 = "임팩트 시 척추가 지나치게 흔들리고 있습니다. 척추각도를 13도로 유지하세요."
            print(imp_advice1)
    
    else : #무게중심이 오른쪽으로 쏠려 척추가 반대로 휘어질 때
        deduction += 15
        imp_advice2 = "무게중심이 오른발에 쏠렸습니다. 왼쪽에 무게중심을 두세요."
        print(imp_advice2)

    if right_leg_angle > 170:  # 오른쪽 다리가 펴져있지 않고 구부려져 있어야 함
        deduction += 5
        bent = 170 - right_leg_angle
        dp = int(bent / 170 * 10)
        deduction += dp
        imp_advice3 = "오른쪽 무릎이 펴져있습니다. 무릎을 굽히고 왼쪽에 무게를 두세요."
        
    return -deduction, imp_advice1, imp_advice2, imp_advice3

def check_followthru(posepoints, pose_idx):
    followtru = pose_idx[5]
    deduction = 0  # 100점에서 차감할 점수의 초기값(음수로 리턴 될 스코어)
    thu_advice1 = ""
    thu_advice2 = ""
    thu_advice3 = ""
    follow_point = posepoints[followtru]
    r_shoulder = follow_point[2]
    r_arm_angle = abs(get_angle(follow_point[2], follow_point[3], follow_point[4]))
    left_leg_angle = abs(get_angle(follow_point[12], follow_point[13], follow_point[14]))
    right_leg_angle = abs(get_angle(follow_point[9], follow_point[10], follow_point[11]))
    
    if r_arm_angle < 170: #오른쪽 팔이 쭉 펴져있지 않다면
        bent = 180 - r_arm_angle
        dp = int(bent / 180 * 10)
        deduction += dp
        thu_advice1 = "오른쪽 팔과 클럽을 직선으로 쭉 뻗어주세요."
        print(thu_advice1)
    
    if left_leg_angle < 170 : #왼쪽 다리는 쭉 펴져있어야 함
        bent = 180 - left_leg_angle
        dp = int(bent / 180 * 7)
        deduction += dp
        thu_advice2 = "왼쪽 다리가 굽어져 있습니다. 쭉 펴세요."
        print(thu_advice2)
    
    if right_leg_angle > 170: #오른쪽 다리 굽힌 채 유지해야함
        bent = 180 - right_leg_angle
        dp = int(bent / 180 * 10)
        deduction += dp
        thu_advice3 = "오른쪽 다리가 왼쪽으로 굽어져있지 않습니다. 손의 방향쪽으로 굽히세요."
        print(thu_advice3)
    
    return -deduction, thu_advice1, thu_advice2, thu_advice3

def check_finish(posepoints, pose_idx):
    finish = pose_idx[6]
    deduction = 0  # 100점에서 차감할 점수의 초기값(음수로 리턴 될 스코어)
    finish_advice = ""
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
        finish_advice = "피니쉬를 할때 몸을 더 비튼다면 비거리가 증가할거예요."
        print(finish_advice)
    return -deduction, finish_advice



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
    cscore,chiken_wing = check_chiken_wing(posepoints, pose_idx)
    bscore, body_sway = check_body_sway(posepoints, pose_idx)
    fscore, finish_advice = check_finish(posepoints, pose_idx)
    ascore,add_advice1,add_advice2,add_advice3 = check_address(posepoints, pose_idx)
    tscore , taway_advice= check_takeaway(posepoints, pose_idx)
    topscore ,top_advice1, top_advice2, top_advice3, top_advice4 = check_topswing(posepoints, pose_idx)
    dscore, down_advice, down_advice2 = check_downswing(posepoints, pose_idx)
    iscore, imp_advice1, imp_advice2, imp_advice3 = check_impact(posepoints, pose_idx)
    slicescore ,slice_advice= check_slice(posepoints, pose_idx)
    truscore ,thu_advice1, thu_advice2, thu_advice3 = check_followthru(posepoints, pose_idx)
    additional = additional_point(posepoints, pose_idx)
    score_list = [ascore, tscore, topscore + slicescore, dscore, iscore, truscore + cscore + bscore, fscore, additional]  # 가장 심각한 실수가 어떤것지 찾기위해
    feedback_list = [chiken_wing ,body_sway, finish_advice, add_advice1, add_advice2, add_advice3, taway_advice,
                     top_advice1, top_advice2, top_advice3, down_advice, imp_advice1, imp_advice2, imp_advice3,
                     slice_advice, thu_advice1, thu_advice2, thu_advice3, down_advice2, top_advice4]
    worst = score_list.index(min(score_list))  # 사용자에게 보여줄 가장 심한 실수의 인덱스를 찾는다.
    score = sum(score_list[0:3])
    if score >= 0:
        print("완벽한 스윙이네요!")
    elif worst == 0:  # check_chiken_wing 이 가장 심각한 실수
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
    return total_score, feedback_list
