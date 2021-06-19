import boto3
import os
import cv2
def uploadFile(filename, files,userid):
    s3 = boto3.client(
        's3',  # 사용할 서비스 이름, ec2이면 'ec2', s3이면 's3', dynamodb이면 'dynamodb'
        aws_access_key_id="AKIAV7WUXMYC2J5GO6ND",  # 액세스 ID
        aws_secret_access_key="oGPrWSHFA2s9q0/Ow3kPs2vi5vOW3lEBj0Qb6YJj")  # 비밀 엑세스 키
    s3.upload_file(files, 'golfapplication', userid + '/image/' +filename)
def downloadFile(URL):
    filename = '../openpose/examples/media/TestGolf.mp4'
    bucket = 'golfapplication'
    key = URL[56:]

    s3 = boto3.client(
        's3',  # 사용할 서비스 이름, ec2이면 'ec2', s3이면 's3', dynamodb이면 'dynamodb'
        aws_access_key_id="AKIAV7WUXMYC2J5GO6ND",  # 액세스 ID
        aws_secret_access_key="oGPrWSHFA2s9q0/Ow3kPs2vi5vOW3lEBj0Qb6YJj")  # 비밀 엑세스 키
    s3.download_file(bucket, key, filename)
def createFolder(directory):
    try:
        if not os.path.exists(directory):
                os.makedirs(directory)
    except OSError:
         print('Error: Creating directory. ' + directory)
def makeImageFile(image,URL,userid):
    for idx in range(0, 7):
        num = str(idx)
        Suserid = str(userid)
        Iuserid = len(Suserid)
        Fname =  URL[57 + Iuserid:]
        cv2.imwrite(userid + '/' + Fname + '-' + num + '.jpg', image[idx])  # save frame as JPEG file
        uploadFile(Fname + '-' + num + '.jpg',userid + '/' + Fname + '-' + num + '.jpg',userid)