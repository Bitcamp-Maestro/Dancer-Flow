import os
import cv2
import json

from utils.data_form import Form
from utils.similarity import single_score_similarity 
from utils.scoring import scoring

from mmpose.apis.inference import (inference_top_down_pose_model, init_pose_model, process_mmdet_results, vis_pose_result)
from mmdet.apis.inference import (inference_detector, init_detector)


class Play():
    def __init__(self, option_1=0,option_2=0, option_3=0):
        """
        Input file:
            Model Input
                deet__init__() : config, checkpoint, device \n
                pose__init__() : config, checkpoint, device \n
                video__init__() : 
            User Input
                Video() : file, .mp4,
                Output_phat : 저장될 위치 경로
        """
        self.option_1 = option_1
        self.option_2 = option_2
        self.option_3 = option_3

    def det__init__(self, config, checkpoint, device="cuda:0"):
        """
        Input:
            Detction -> config, checkpoint, device
            객체 인식 : config파일, checkpoint파일, 디바이스 종류
        """
        det_config = config
        det_checkpoint = checkpoint
        det_device = device
        self.det_model = init_detector(det_config, det_checkpoint, device=det_device)

    def pose__init__(self, config, checkpoint, device="cuda:0"):
        """
        Input:
            Pose -> config, checkpoint, device
            포즈 인식 : config파일, checkpoint파일, 디바이스 종류
        """
        pose_config = config
        pose_checkpoint = checkpoint
        pose_device = device
        self.pose_model = init_pose_model(pose_config, pose_checkpoint, device=pose_device)


    def det_Pose_Video(self, user_video,  outpath="result", option=True):
        FACE_BODY_SCORE = 0
        BODY_SCORE = 0
        LEFT_ARM_SCORE = 0
        RIGHT_ARM_SCORE = 0
        LEFT_LEG_SCORE = 0
        RIGHT_LEG_SCORE = 0
        SHOW = True                                 # 보여줄건지 선택 변수
        DET_CAT_ID = 1      # Category id for bounding box detection model
        RESULT_BOX = {}
        RESULT_BOX_2 = {}

        # 3. 영상 파일을 불러오기
        cap = cv2.VideoCapture(user_video)
        fps = cap.get(cv2.CAP_PROP_FPS)
        size = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        videoWriter = cv2.VideoWriter(
            os.path.join(outpath, f'DancerFlow_{os.path.basename(user_video)}'), fourcc, fps, size)
        
        idx = 0
        while cap.isOpened():
            idx += 1
            flag, img = cap.read()
            if not flag:
                break
            
            # test a single image, the resulting box is (x1, y1, x2, y2)
            mmdet_results = inference_detector(self.det_model, img)

            # keep the person class bounding boxes.
            person_results = process_mmdet_results(mmdet_results, DET_CAT_ID)
            # test a single image, with a list of bboxes.
            pose_results, returned_outputs = inference_top_down_pose_model(
                self.pose_model,
                img,
                person_results,
                bbox_thr=0.5,
                format='xyxy',
                return_heatmap=False,
                outputs=None)

            if option == True:
                ## 두개의 영상을 하나로 합칠 때
                # 0.1V 단 한 영상에 한명씩 나올 때  
                bounding_Box_1 = pose_results[0]["bbox"]
                bounding_Box_2 = pose_results[1]["bbox"]
                result_dict_1={}
                result_dict_2={}
                for i1, p1_point in enumerate(pose_results[0]["keypoints"]):
                    result_dict_1 = Form.data_form(dict=result_dict_1, i = i1, keypoint = p1_point)
                data_1 = Form.make_dic(idx, bounding_Box_1, result_dict_1)
                # print(result_dict)
                RESULT_BOX[idx] = (data_1)
                for i2, p2_point in enumerate(pose_results[1]["keypoints"]):
                    result_dict_2 = Form.data_form(dict=result_dict_2, i = i2, keypoint = p2_point)
                data_2 = Form.make_dic(idx, bounding_Box_2, result_dict_2)
                RESULT_BOX_2[idx] = (data_2)
            else:
                ## 단일 영상을 불러 올 때
                # 단 target의 경우 좌표 값을 불러와야 한다.
                # mongodb와 연결해서 불러올 것
                bounding_Box = pose_results[0]["bbox"]
                result_dict={}
                for i, p_point in enumerate(pose_results[0]["keypoints"]):
                    result_dict = Form.data_form(dict=result_dict, i = i, keypoint = p_point)
                data_1 = Form.make_dic(idx, bounding_Box, result_dict)
                RESULT_BOX[idx] = (data_1)
                data_2 = ""

            ################### 유사도 측정 알고리즘 추가 ##################################
            similarity_score = single_score_similarity(
                                    user_pose_result= data_1,
                                    target_pose_result= data_2,
                                    user_frame=0,
                                    target_frame=0)
            # Scoring 
            FACE_BODY_SCORE = scoring(similarity_score["face_body_score"], FACE_BODY_SCORE)
            # BODY_SCORE = scoring(similarity_score["body_score"], BODY_SCORE)
            LEFT_ARM_SCORE = scoring(similarity_score["left_arm_score"], LEFT_ARM_SCORE)
            RIGHT_ARM_SCORE = scoring(similarity_score["right_arm_score"], RIGHT_ARM_SCORE)
            LEFT_LEG_SCORE = scoring(similarity_score["left_leg_score"], LEFT_LEG_SCORE)
            RIGHT_LEG_SCORE = scoring(similarity_score["right_leg_score"], RIGHT_LEG_SCORE)
            # print(RESULT_BOX_2)
            print("얼굴+몸 점수 : ",FACE_BODY_SCORE)
            print("왼쪽 팔 점수 : ",LEFT_ARM_SCORE)
            print("오른 팔 점수 : ",RIGHT_ARM_SCORE)
            print("왼쪽 발 점수 : ",LEFT_LEG_SCORE)
            print("오른 발 점수 : ",RIGHT_LEG_SCORE)
            ############################################################################

            # show the results
            vis_img = vis_pose_result(
                self.pose_model,
                img,
                pose_results,
                kpt_score_thr=0.5,
                radius=4,               # 원 크기
                thickness=2,            # 관절 두께
                show=False)

            if SHOW == True:
                cv2.imshow('Image', vis_img)
            videoWriter.write(vis_img)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            
        cap.release()
        videoWriter.release()
        cv2.destroyAllWindows()

        ## 결과값을 json파일로 저장
        with open("./sample.json", "w") as outfile:
            json.dump(RESULT_BOX, outfile, indent=4)
        
        return RESULT_BOX

if __name__ == '__main__':
    
    # Detction 설정
    DET_CONFIG_FASTER_R_CNN_R50_FPN_COCO = "configs/detection/faster_rcnn_r50_fpn_coco.py"                                                                                                        # Detection config 파일
    DET_CHECKPOINT_FASTER_R_CNN_R50_FPN_COCO = "https://download.openmmlab.com/mmdetection/v2.0/faster_rcnn/faster_rcnn_r50_fpn_1x_coco/faster_rcnn_r50_fpn_1x_coco_20200130-047c8118.pth"        # Detection 훈련 모델 파일
    
    # Pose 설정
    POSE_CONFIG_HRNET_W48_COCO_256X192 = "configs/pose/body/2d_kpt_sview_rgb_img/topdown_heatmap/coco/hrnet_w48_coco_256x192.py"                                                               # Pose config 파일
    POSE_CHECKPOINT_HRNET_W48_COCO_256X192 = "https://download.openmmlab.com/mmpose/checkpoints/pose/hrnet_w48_coco_256x192-b9e0b3ab_20200708.pth"                                             # Pose 훈련 모델 파일
    
    # 영상 경로
    VIDEO_1 = "./sample_data/test.mp4" # 유저 업로드 영상

    play= Play()
    play.det__init__(DET_CONFIG_FASTER_R_CNN_R50_FPN_COCO, DET_CHECKPOINT_FASTER_R_CNN_R50_FPN_COCO, device="cuda:0")
    play.pose__init__(POSE_CONFIG_HRNET_W48_COCO_256X192, POSE_CHECKPOINT_HRNET_W48_COCO_256X192, device="cuda:0")
    play.det_Pose_Video(VIDEO_1, outpath="result")