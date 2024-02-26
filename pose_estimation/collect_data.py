"""
使用MP采集各种人体姿态训练素材
保存姿态托，以及
"""
import torch
import cv2
import numpy as np
import mediapipe as mp
mp_drawing=mp.solutions.drawing_utils
mp_drawing_styles=mp.solutions.drawing_styles
import time

class Mpkeypoints:
    """
    获取人体关键点
    """
    def __init__(self):
        self.mp_pose=mp.solutions.pose
        self.pose=self.mp_pose.Pose(min_detection_confidence=0.5,min_tracking_confidence=0.5)
        self.save_count=1
    def getFramePose(self, image):
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        # 检测人体关键点
        results = self.pose.process(image_rgb)
        return results.pose_landmarks,self.mp_pose.POSE_CONNECTIONS,results
    def landmark_to_csv(self,frame,frame_index):
        """
        获取特征
        1.获取6个关键点
        2.特征保存到csv文件，原图，渲染图，保存到文件夹
        """
        frame_copy=frame.copy()
        frame_h,frame_w=frame_copy.shape[:2]
        #获取关键点
        pose_landmarks,conns,results=self.getFramePose(frame)
        if pose_landmarks:
            p_list=[[landmark.x,landmark.y] for landmark in pose_landmarks.landmark[11:17]]
            #转为numpy 才能广播计算
            p_list=np.asarray(p_list)
            resize_points =[]
            for x,y in p_list:
                p_x=int(x*frame_w)
                p_y=int(y*frame_h)
                cv2.circle(frame_copy,(p_x,p_y),10,(0,255,0),-1)
                resize_points.append(x)
                resize_points.append(y)
            if frame_index%2==0:
                file_name='./data/pose/raw/raw_{}.jpg'.format(frame_index)
                cv2.imwrite(file_name,frame)
                file_name = './data/pose/render/render_{}.jpg'.format(frame_index)
                cv2.imwrite(file_name, frame_copy)
                file_name = './data/pose/txt/frame_{}.txt'.format(frame_index)
                with open(file_name,'w') as f:
                    for p in resize_points:
                        f.write('%s\n' % p)
                print('成功保存：第{}帧，共保存了{}个'.format(frame_index,self.save_count))
                self.save_count+=1
        return frame_copy
class Pose_detect:
    def __init__(self):
        self.model=torch.hub.load('./yolov5','custom',path='./weights/yolov5m.pt',source='local')
        self.model.conf=0.4 #置信度阈值
        self.cap=cv2.VideoCapture(0)
        self.frame_w=int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frame_h = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.mp_keypoints=Mpkeypoints()
    def detect(self):
        #帧数
        frame_index=0
        while True:
            ret,frame=self.cap.read()
            if frame is None:
                break
            img_cvt=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
            results=self.model(img_cvt)

            pd=results.pandas().xyxy[0]
            person_list=pd[pd['name']=='person'].to_numpy()

            #遍历每个人
            for person in person_list:
                l,t,r,b =person[:4].astype('int')

                frame_crop=frame[t:b,l:r]
                frame_back =self.mp_keypoints.landmark_to_csv(frame_crop,frame_index)
                cv2.rectangle(frame,(l,t),(r,b),(0,255,0),5)
                cv2.imshow('demo',frame_back)
                if cv2.waitKey(10)&0xFF==ord('q'):
                    break
            frame_index+=1

        self.cap.release()
        cv2.destroyAllWindows()
plate=Pose_detect()
plate.detect()

