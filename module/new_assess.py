from module.set_data import *
from real_server import *
import math
total = 14.3
px = 0.02645 #1픽셀을 cm
"""총 7개의 기준(어드레스 - 피니쉬)을 각각 12.5 개의 비중으로 나눴으며, 
                                        각 기준마다 일정한 기준치를 두어 자세별 점수 계산"""

def score_convert(standard, user, weight): #가중치를 넣어 환산한 점수
    far_point = abs(standard - user) / standard
    convert_score = (1 - far_point) * weight
    return convert_score



def check_address(poseoints, pose_idx):
    address = pose_idx[0]
    score = 0  # 100점에서 차감할 점수의 초기값(음수로 리턴 될 스코어)
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
    stance = (l_heel.get('x') - r_heel.get('x')) * px
    shoulder_width = l_shoulder.get('x') - r_shoulder.get('x') * px # 스탠스를 위해 비교하는 수치
    if r_shoulder.get('y') > l_shoulder.get('y'):  # 오른쪽 어깨가 왼쪽어깨보다 낮을때 기울기
        if 8 > angle or 20 < angle:  # 14도가 적정 어깨 기울기(오차범위 6)
            ad_score1 = score_convert(14, angle, 0.8)
            score += ad_score1
            add_advice1 = "어드레스 셋 업 자세에서 오른쪽 어깨 기울기를 조절하세요."
            print(add_advice1)
        else:
            score += 0.8
    else :  # 오른쪽 어깨가 왼쪽 어깨보다 높은 경우
        upside = (l_shoulder.get('y') - r_shoulder.get('y')) * px
        ad_score1 = upside * 0.8
        score += ad_score1
        add_advice2 = "오른쪽 어깨가 왼쪽보다 높습니다. 오른쪽 어깨를 낮추세요"
        print(add_advice2)


    if stance < 5 or (stance - shoulder_width) > 5:  # 발 너비 스탠스가 5보다 작은 경우(적정 스탠스 너비 5cm) 혹은 어깨 너비보다 너무 넓은 경우
        ad_score2 = score_convert(5,stance,0.2)
        score += ad_score2
        add_advice3 = "발의 너비를 어깨 너비만큼 조절하세요.(적정 너비 5cm)"
        print(add_advice3)
    else:
        score += 0.2

    ad_score = round(score * total,1)
    convert_score = int(ad_score / total * 100)
    print('address: '+str(ad_score)+','+str(convert_score))
    return ad_score,convert_score, add_advice1, add_advice2, add_advice3



def check_takeaway(posepoints, pose_idx):
    takeaway = pose_idx[1]
    score = 0  # 100점에서 차감할 점수의 초기값(음수로 리턴 될 스코어)
    taway_advice = ""
    takeaway_point = posepoints[takeaway]
    right_arm_angle = abs(get_angle(takeaway_point[2], takeaway_point[3], takeaway_point[4]))
    left_arm_angle = abs(get_angle(takeaway_point[5], takeaway_point[6], takeaway_point[7]))

    if right_arm_angle < 170 or left_arm_angle < 170:  # 팔이 굽어져 있는 경우
        t_score1 = score_convert(170, right_arm_angle,0.5)
        t_score2 = score_convert(170,left_arm_angle,0.5)
        score = t_score1 + t_score2
        taway_advice = "팔이 굽어져있습니다. 팔을 쭉 편 상태를 유지하며 스윙하세요."
        print(taway_advice)
    else:
        score += 1

    t_score = round(score * total,1)
    convert_score = int(t_score / total * 100)

    print("takeaway : " + str(t_score) +","+ str(convert_score))
    return t_score,convert_score, taway_advice



def check_topswing(posepoints, pose_idx):
    top = pose_idx[2]
    address = pose_idx[0]
    score = 0  # 100점에서 차감할 점수의 초기값(음수로 리턴 될 스코어)
    top_advice1 = ""
    top_advice2 = ""
    top_advice3 = ""
    top_advice4 = ""
    top_advice5 = ""
    address_point = posepoints[address]
    top_point = posepoints[top]

    r_shoulder = address_point[2]
    l_shoulder = address_point[5]
    r_arm_angle = abs(get_angle(top_point[2], top_point[3], top_point[4]))
    top_point = posepoints[top]
    r_ear = top_point[0]
    l_wrist = top_point[7]
    neck = top_point[1]
    waist = top_point[8]

    gradient = slope(waist, neck)
    l_arm_angle = abs(get_angle(top_point[5], top_point[6], top_point[7]))
    l_leg_angle = abs(get_angle(top_point[12], top_point[13], top_point[14]))
    pelvis_width = top_point[12].get('x') - top_point[9].get('x') * px
    knee_width = top_point[13].get('x') - top_point[10].get('x') * px

    if l_wrist.get('y') < r_ear.get('y'):  # 왼쪽 손목이 오른쪽 귀 위에 있으면 손목이 머리 부근에 있는 것이라 봄
        if l_arm_angle < 170:  # 팔이 쭉 펴져있지 않은 경우
            top_score1 = score_convert(170, l_arm_angle,0.35)
            score += top_score1
            top_advice1 = "탑스윙 시 왼쪽 팔을 쭉 펴세요."
            print(top_advice1)
        else:
            score += 0.35
    else:  # 손목이 머리 아래에 있을 때
        if l_arm_angle < 170:
            minuspoint = (l_wrist.get('y') - r_ear.get('y')) * px * 0.1
            top_score1 = minuspoint * 0.25
            top_score1_2 = score_convert(170, l_arm_angle, 0.1)
            top_score1 = top_score1 + top_score1_2
            score += top_score1
        else:
            minuspoint = (l_wrist.get('y') - r_ear.get('y')) * px
            top_score1 = minuspoint * 0.35
            score += top_score1
        top_advice2 = "손의 위치가 낮습니다. 탑스윙 시 양 손을 머리 위까지 올리고 팔을 쭉 펴세요."
        print(top_advice2)

    # 다리 각도 체크 : 왼쪽 다리를 굽히지만, 왼쪽 다리가 지나치게 구부려져
    # 오른쪽 무릎과 왼쪽 무릎이 가까이 맞닿은 상태가 되지 않아야 한다.
    if l_leg_angle > 165:
        if knee_width < pelvis_width:
            minuspoint = score_convert(pelvis_width, knee_width, 0.05)
            top_score2 = score_convert(165,l_leg_angle, 0.1)
            top_score2 = top_score2 + minuspoint
            score += top_score2
            #print(top_score2)
        top_score2 = score_convert(165,l_leg_angle,0.15)
        score += top_score2
        #print(top_score2)
        top_advice3 = "무릎 구부림이 올바르지 않습니다. 오른쪽 다리에 체중을 싣고 왼쪽 무릎은 살짝만 구부리세요."
        print(top_advice3)
    else:
        score += 0.15
    # 척추 체크 : 척추 축의 기울임 체크
    if gradient < 0:  # 척추 축 반대로 기울어짐
        gradient = abs(int(gradient))
        top_score3 = gradient / 100 * 0.25
        score += top_score3
        #print(top_score3)
        top_advice4 = "척추의 축이 기울어져 있습니다. 하체 뒤로 더 빼주세요."
    else:
        score += 0.25
    #슬라이스 유발
    if r_shoulder.get('y') < l_shoulder.get('y'):  # 어드레스에서 오른쪽 어깨가 더 높을 때(원점에서 멀어질수록 y값 증가)
        minuspoint = (l_shoulder.get('y') - r_shoulder.get('y')) * px * 0.125
        score += minuspoint
    else:
        score += 0.125
    if 80 < r_arm_angle or 90 > r_arm_angle:  # 탑스윙에서 오른쪽 팔꿈치의 각도는 90도가 적정(아닐시 슬라이스 발생 높다)
        top_score4 = score_convert(90, r_arm_angle, 0.125)
        score += top_score4
        top_advice5 = "탑스윙 시 오른쪽 팔꿈치가 직각을 유지하지 않습니다. 이는 슬라이스를 유발합니다."
        print(top_advice5)
        #print(top_score4)
    else:
        score += 0.125

    top_score = round(score * total,1)
    convert_score = int(top_score / total * 100)
    print("top : " + str(top_score) +',' + str(convert_score))
    return int(top_score),convert_score, top_advice1, top_advice2, top_advice3, top_advice4, top_advice5


def check_downswing(posepoints, pose_idx):
    top = pose_idx[2]
    down = pose_idx[3]
    score = 0  # 100점에서 차감할 점수의 초기값(음수로 리턴 될 스코어)
    down_advice = ""
    down_advice2 = ""
    down_point = posepoints[down]
    top_point = posepoints[top]
    right_arm_angle = abs(get_angle(down_point[2], down_point[3], down_point[4]))
    top_leg_angle = abs(get_angle(top_point[9], top_point[10], top_point[11]))
    down_leg_angle = abs(get_angle(down_point[9], down_point[10], down_point[11]))

    # early release 체크로 다운스윙시 오른팔의 각도가 빨리 풀리면 안된다. 탑스윙에서 오른팔 각도를 최대한 유지해야함
    if right_arm_angle > 105:  # 오른쪽 팔꿈치의 변화량 최대 15도(그 이상일시 early release 발생)
        donw_score1 = score_convert(105, right_arm_angle, 0.6)
        score += donw_score1
        #print(score)
        down_advice = "다운스윙 시 오른쪽 팔이 빨리 풀리는 early release가 발생했습니다."
        print(down_advice)
    else :
        score += 0.6
    if top_leg_angle >= down_leg_angle:  # 체중이 왼쪽으로 쏠리면서 오른쪽 다리는 굽혀져야 함
        down_score2 = score_convert(down_leg_angle,top_leg_angle,0.4)
        score += down_score2
        #print(score)
        down_advice2 = "오다른쪽 다리가 펴져있습니다. 체중을 왼쪽에 싣고 오른쪽 다리는 굽히세요."
    else :
         score += 0.4
    d_score = score * total
    convert_score = int(d_score / total * 100)
    print("down : " + str(d_score) + ',' + str(convert_score))
    return int(d_score), convert_score, down_advice, down_advice2


def check_impact(posepoints, pose_idx):
    impact = pose_idx[4]
    score = 0  # 100점에서 차감할 점수의 초기값(음수로 리턴 될 스코어)
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
            ip_score1 = score_convert(13, angle, 0.65)
            score += ip_score1
            imp_advice1 = "임팩트 시 척추가 지나치게 흔들리고 있습니다. 척추각도를 13도로 유지하세요."
            print(imp_advice1)
        else:
            score += 0.65
    else :  # 무게중심이 오른쪽으로 쏠려 척추가 반대로 휘어질 때
        gradient = abs(int(gradient))
        ip_score1 = gradient / 100 * 0.65
        score += ip_score1
        imp_advice2 = "무게중심이 오른발에 쏠렸습니다. 왼쪽에 무게중심을 두세요."
        print(imp_advice2)

    if right_leg_angle > 170:  # 오른쪽 다리가 펴져있지 않고 구부려져 있어야 함
        ip_score2 = score_convert(170, right_leg_angle, 0.35)
        score += ip_score2
        imp_advice3 = "오른쪽 무릎이 펴져있습니다. 무릎을 굽히고 왼쪽에 무게를 두세요."
    else :
        score += 0.35

    i_score = round(score * total,1)
    convert_score = int(i_score / total * 100)
    print("impact : " + str(i_score)+','+str(convert_score))

    return int(i_score),convert_score, imp_advice1, imp_advice2, imp_advice3


def check_followthru(posepoints, pose_idx):
    top_idx = pose_idx[2]
    followtru = pose_idx[5]
    score = 0  # 100점에서 차감할 점수의 초기값(음수로 리턴 될 스코어)
    thu_advice1 = ""
    thu_advice2 = ""
    thu_advice3 = ""
    thu_advice4 = ""
    thu_advice5 = ""
    top_point = posepoints[top_idx]

    follow_point = posepoints[followtru]
    l_arm_angle = abs(get_angle(follow_point[5], follow_point[6], follow_point[7]))
    r_arm_angle = abs(get_angle(follow_point[2], follow_point[3], follow_point[4]))
    start_angle = get_slope(follow_point[6], follow_point[7])
    end_angle = get_slope(follow_point[6], follow_point[5])
    left_leg_angle = abs(get_angle(follow_point[12], follow_point[13], follow_point[14]))
    right_leg_angle = abs(get_angle(follow_point[9], follow_point[10], follow_point[11]))

    # 탑과 팔로스루 비교 .
    spine_slope_top_swing = get_slope(top_point[8], top_point[1])
    spine_slope_follow_through = get_slope(follow_point[8], follow_point[1])

    dif_angle = abs(spine_slope_top_swing) - abs(spine_slope_follow_through)
    dif_angle = abs(dif_angle)  # 차이를 절대값으로 점수 계산

    if spine_slope_follow_through >= -90:  # 팔로스루시 척추가 오른쪽으로 휘었으면 바디스웨이라고 판단.
        thu_advice1 = "바디 스웨이가 발생했네요 스윙시에 몸이 자꾸 움직이면 정확도를낮춥니다."
        print(thu_advice1)
    else:
        score += 0.4

    if r_arm_angle < 170:  # 오른쪽 팔이 쭉 펴져있지 않다면
        follu_score2 = score_convert(170, r_arm_angle, 0.2)
        score += follu_score2
        thu_advice2 = "오른쪽 팔과 클럽을 직선으로 쭉 뻗어주세요."
        print(thu_advice2)
    else :
        score += 0.2

    if (start_angle - end_angle) >= 170:
        if l_arm_angle > 175:  # 왼팔이 175정도라면 충분히 펴져있다고 판단.
            score += 0.25
    else:
        follu_score3 = score_convert(170, start_angle - end_angle, 0.25)
        score += follu_score3
        thu_advice3 = "치킨윙이 발생했습니다. 왼팔을 충분히 펴주세요."
        print(thu_advice3)

    if left_leg_angle < 170:  # 왼쪽 다리는 쭉 펴져있어야 함
        follu_score4 = score_convert(170, left_leg_angle, 0.075)
        score += follu_score4
        thu_advice4 = "왼쪽 다리가 굽어져 있습니다. 쭉 펴세요."
        print(thu_advice4)
    else :
        score += 0.075

    if right_leg_angle > 170:  # 오른쪽 다리 굽힌 채 유지해야함
        follu_score5 = score_convert(170, right_leg_angle,0.075)
        score += follu_score5
        thu_advice5 = "오른쪽 다리가 왼쪽으로 굽어져있지 않습니다. 손의 방향쪽으로 굽히세요."
        print(thu_advice5)
    else:
        score += 0.075



    f_score = round(score * total,1)
    convert_score = int(f_score / total * 100)

    print("follow : " + str(f_score)+','+str(convert_score))
    return int(f_score),convert_score, thu_advice1, thu_advice2, thu_advice3, thu_advice4, thu_advice5





def check_finish(posepoints, pose_idx):
    finish = pose_idx[6]
    score = 0  # 100점에서 차감할 점수의 초기값(음수로 리턴 될 스코어)
    finish_advice1 = ""
    finish_advice2 =""
    finish_advice3 = ""
    finish_point = posepoints[finish]
    r_sholder = finish_point[2]
    l_sholder = finish_point[5]
    right_leg_angle = abs(get_angle(finish_point[9], finish_point[10], finish_point[11]))
    left_leg_angle = abs(get_angle(finish_point[12], finish_point[13], finish_point[14]))
    if r_sholder.get('x') > l_sholder.get('x'):  # 피니쉬 후 어깨가 완전히 돌아가 있는경우
        slope = get_slope(r_sholder, l_sholder)
        pelvic_length = get_distan(finish_point[9], finish_point[12])  # 골반 길이
        score += 0.35
    else:  # 피니쉬 이후에도 어깨가 돌아가지않음
        slope = abs(get_slope(r_sholder, l_sholder))
        finish_score1 = slope / 100 * 0.35
        score += finish_score1
        finish_advice1 = "피니쉬를 할때 몸을 더 비튼다면 비거리가 증가할거예요."
        print(finish_advice1)
    #오른쪽 다리 굽어짐 체크
    if right_leg_angle > 160 :
        finish_score2 = score_convert(160, right_leg_angle, 0.35)
        score += finish_score2
        finish_advice2 = "몸을 비틀 때, 오른쪽 다리를 굽힌 뒤 발 끝을 올리세요."
        print(finish_advice2)
    else :
        score += 0.35
    #왼쪽 다리 펴짐 체크
    if left_leg_angle < 170 :
        finish_score3 = score_convert(170, left_leg_angle, 0.3)
        score += finish_score3
        finish_advice3 = "왼쪽 다리를 일직선이 될때까지 펴세요."
        print(finish_advice3)
    else :
        score += 0.3

    finish_score = round(score * total,1)
    convert_score = int(finish_score / total * 100)

    print("finish: " + str(finish_score)+','+str(convert_score))
    return finish_score, convert_score, finish_advice1, finish_advice2, finish_advice3




def assess_pose(posepoints, pose_idx):

    ascore, a_convert, add_advice1, add_advice2, add_advice3 = check_address(posepoints, pose_idx)
    tscore, t_convert, taway_advice = check_takeaway(posepoints, pose_idx)
    topscore, top_convert, top_advice1, top_advice2, top_advice3, top_advice4, top_advice5 = check_topswing(posepoints, pose_idx)
    dscore, d_convert, down_advice, down_advice2 = check_downswing(posepoints, pose_idx)
    iscore, i_convert, imp_advice1, imp_advice2, imp_advice3 = check_impact(posepoints, pose_idx)
    truscore, tru_convert,thu_advice1, thu_advice2, thu_advice3, thu_advice4, thu_advice5 = check_followthru(posepoints, pose_idx)
    fscore, finish_convert, finish_advice1, finish_advice2, finish_advice3 = check_finish(posepoints, pose_idx)
    score_list = [ascore, tscore, topscore, dscore,iscore,truscore,fscore]
    worst = score_list[0:7].index(min(score_list))
    convert_score_list = [a_convert, t_convert, top_convert, d_convert, i_convert, tru_convert, finish_convert]
    feedback_list = [add_advice1, add_advice2, add_advice3, taway_advice, top_advice1, top_advice2, top_advice3, top_advice4, top_advice5
                     ,down_advice, down_advice2, imp_advice1, imp_advice2, imp_advice3, thu_advice1, thu_advice2, thu_advice3, thu_advice4, thu_advice5, finish_advice1,
                     finish_advice2, finish_advice3, worst]

    #총점 계산
    real_total = 0
    for i in score_list:
        real_total = real_total + i

    real_total = int(real_total)
    print('총점수 : '+str(real_total))


    return real_total, convert_score_list, feedback_list

