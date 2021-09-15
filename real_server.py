import flask
import boto3
import imutils
import time
from flask import Flask, render_template, request, redirect, url_for
from matplotlib import pyplot as plt
import mysql.connector
from PIL import ImageFont, ImageDraw, Image
import os
import cv2
import json
import math
import sys
from module.new_assess import *
from module.classify import *
from module.draw import *
from module.file import *
from module.set_data import *
score = []
total_score = 100
feedback_list = []
error = 1

def main(URL,userid):
    global real_total
    global feedback_list
    global convert_score_list
    global error
    #date = os.system('date')
    time.sleep(2)
    downloadFile(URL)
    filepath = '../openpose/examples/media/'
    filename = 'TestGolf'
    vidname = filepath + filename+'.mp4'
    #아래 주석풀면 gpu 과부하걸리니 최초 실행시만
    path = os.system('../openpose/build/examples/openpose/openpose.bin --video ' '../openpose/examples/media/TestGolf.mp4 --write_json output/ --display 0 --render_pose 0 --frame_rotate=270')
    size,frame=get_frame(vidname)
    posepoints ,error = get_keypoints(filename,size)
    if (error == -1):
        return
    pose_idx ,error= pose_classifier(posepoints)  # 포즈 분류하기
    if (error == -1):
        return
    pose_img = cut_vid(frame, pose_idx)  # pose_img 는 리스트 입니다..
    draw_image(pose_img, pose_idx, posepoints)  # 골격 그리기
    image = cut_img(posepoints, pose_img, pose_idx, 0)  # 서버에 전송할 7가지 이미지 자르기(포즈 자세히 부분에 사용자에게 보여줄거)
    real_total, convert_score_list, feedback_list = assess_pose(posepoints, pose_idx)  # 포즈 평가하기
    makeImageFile(image,URL,userid)
app = Flask(__name__)
@app.route('/db', methods = ['GET', 'POST'])
def chat():
    msg_received = flask.request.get_json()
    msg_subject = msg_received["subject"]

    if msg_subject == "register":
        return register(msg_received)
    elif msg_subject == "login":
        return login(msg_received)
    elif msg_subject == "video":
        return video(msg_received)
    elif msg_subject == "MainMenu":
        return MainMenu(msg_received)
    else:
        return "Invalid request."
def video(msg_received):
    userid = msg_received["userid"]
    videoURL = msg_received["URL"]

    try:
        time.sleep(5)
        downloadFile(videoURL)
        createFolder('./' + userid)
        main(videoURL,userid)
        if(error == -1):
            return {"error" : error}
        elif(error == 1):
            return {"adressscore" : 100 + score[0] , "takebackscore" : 100 + score[1] , "topascore" : 100 + score[2] , "dscore" : 100 + score[3] , "iascore" : 100 + score[4] ,
                    "truascore" : 100 + score[5] , "fscore" : 100 + score[6] ,"chiken_wing" : feedback_list[0], "body_sway" : feedback_list[1], "finish_advice" : feedback_list[2],
                    "add_advice1" : feedback_list[3], "add_advice2" : feedback_list[4], "add_advice3" : feedback_list[5], "taway_advice" : feedback_list[6], "score" : total_score,
                    "top_advice1" : feedback_list[7], "top_advice2" : feedback_list[8], "top_advice3" : feedback_list[9], "down_advice" : feedback_list[10],
                    "imp_advice1" : feedback_list[11], "imp_advice2" : feedback_list[12], "imp_advice3" : feedback_list[13], "slice_advice" : feedback_list[14],
                    "thu_advice1" : feedback_list[15], "thu_advice2" : feedback_list[16], "thu_advice3" : feedback_list[17], "down_advice2" : feedback_list[18],
                    "top_advice4" : feedback_list[19], "worst" : feedback_list[20], "error" : error}

    except Exception as e:
        print("Error while inserting the new record :", repr(e))
        return "failure"
def register(msg_received):
    id = msg_received["userid"]
    password = msg_received["userpwd"]
    username = msg_received["username"]
    email = msg_received["useremail"]

    select_query = "SELECT * FROM users where id = " + "'" + id + "'"
    db_cursor.execute(select_query)
    records = db_cursor.fetchall()
    if len(records) != 0:
        return "Another user used the username. Please chose another username."

    insert_query = "INSERT INTO users (id, psw, name, email) VALUES (%s, MD5(%s), %s, %s)"
    insert_values = (id, password, username, email)
    try:
        db_cursor.execute(insert_query, insert_values)
        chat_db.commit()
        return "success"
    except Exception as e:
        print("Error while inserting the new record :", repr(e))
        return "failure"

def MainMenu(msg_received):
    userid = msg_received["userid"]
    select_query = "SELECT name FROM users where id = " + "'" + userid + "'"
    db_cursor.execute(select_query)
    records = db_cursor.fetchall()
    result = ",".join(records[0])
    username = result + "님"
    if len(records) == 0:
        return username
    else:
        return username

def login(msg_received):
    username = msg_received["userid"]
    password = msg_received["userpwd"]
    select_query = "SELECT name FROM users where id = " + "'" + username + "' and psw = " + "MD5('" + password + "')"
    db_cursor.execute(select_query)
    records = db_cursor.fetchall()

    if len(records) == 0:
        return "failure"
    else:
        return "success"
try:
    chat_db = mysql.connector.connect(host="golfdb.chx469ppubzv.ap-northeast-2.rds.amazonaws.com",
                                      user="jaewon", passwd="jl42474247", database="Golfuser")
except:
    sys.exit("Error connecting to the database. Please check your inputs.")
db_cursor = chat_db.cursor()
#main()
if __name__ == "__main__":
	app.run(host="0.0.0.0", port=5000, debug=True, threaded=True)
