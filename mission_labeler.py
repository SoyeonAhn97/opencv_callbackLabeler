import cv2, sys
import numpy as np
from glob import glob
import os

# 0. 파일 목록 읽기 (data 폴더) *.jpg -> 리스트
# 1. 이미지 불러오기
# 2. 마우스 콜백함수 생성
# 3. 콜백함수 안에서 박스를 그리고, 박스 좌표를 뽑아낸다. (마우스 좌표 2개)
#    참고로 YOLO에서는 박스의 중심좌표(x, y) w, h
# 4. 이미지 파일명과 동일한 파일명으로 (확장자만 빼고) txt파일 생성
#  추가 기능0 : 박스를 잘못 쳤을 때 'c'를 누르면 현재 파일의 박스 내용 초기화
#  추가 기능1 : 화살표(->)를 누르면 다음 이미지 로딩되고(1~4번 반복)
#  추가 기능2 : 화살표(<-)를 눌렀을 때 txt파일이 있다면 박스를 이미지 위에 띄워주면
#  (( 추천 )) 개별 함수 기능으로 만들어보기



# 현재 작업 디렉토리에서 images 폴더에 있는 모든 .jpg 파일을 찾아 리스트로 반환
# 이미지 파일들을 불러올 때 사용
def getImageList():
    #현재 작업 디렉토리 확인
    basePath = os.getcwd()
    dataPath = os.path.join(basePath,'images')
    fileNames = glob(os.path.join(dataPath,'*.jpg'))

    return fileNames



# 이미지 위에 기존의 박스를 그리고,
# 마우스를 이동 중일 때는 실시간으로 초록색 박스를 추가로 표시
# corners : 좌표(startPt, endPt)
# 2개 좌표를 이용해서 직사각형 그리기
def drawROI(cpy, boxList, currentBox=None):
    # 박스를 그릴 레이어를 생성 : cpy
    cpy = cpy.copy()
    line_c = (128,128,255) #직선의 색상
    lineWidth = 2
    for corners in boxList:
        cv2.rectangle(cpy, tuple(corners[0]), tuple(corners[1]), color=line_c, thickness=lineWidth)
    # currentBox는 사용자가 현재 마우스로 선택 중인 박스의 좌표,
    # 이 박스는 초록색으로 표시됨
    if currentBox:
        cv2.rectangle(cpy, tuple(currentBox[0]), tuple(currentBox[1]), color = (0, 255, 0), thickness = lineWidth)

    # alpha=0.3, beta=0.7, gamma=0
    disp = cv2.addWeighted(img, 0.3, cpy, 0.7, 0)
    return disp



# 마우스 콜백 함수 정의
def onMouse(event, x, y, flags, param):
    global startPt, img, boxList, cpy, txtWrData
    
    cpy = img.copy()
    # 마우스 왼쪽 버튼이 눌렸을 때 시작 좌표를 기록
    if event == cv2.EVENT_LBUTTONDOWN: 
        startPt=(x,y)
    # 마우스 왼쪽 버튼이 떼어지면 좌표를 기록하여 boxList에 추가
    # 사각형을 이미지에 그린다
    elif event == cv2.EVENT_LBUTTONUP: 
        ptList = [startPt,(x,y)]
        boxList.append(ptList)
        txtWrData = str(boxList)
        cpy = drawROI(cpy, boxList)
        startPt = None
        cv2.imshow('label', cpy)
    # 마우스가 움직일 때, 시작 좌표가 있을 경우 실시간으로 박스를 그리며,
    # 미완성 박스는 초록색으로 표시
    elif event == cv2.EVENT_MOUSEMOVE:
        if startPt:
            currentBox = [startPt, (x, y)]
            cpy = drawROI(cpy, boxList, currentBox)
            cv2.imshow('label',cpy)



# 좌표를 텍스트 파일로 저장
def saveBoxData(filename):
    txtFilename = filename + '.txt'
    with open(txtFilename, 'w') as f:
        for box in boxList:
            f.write(f"{box[0][0]}, {box[0][1]}, {box[1][0]}, {box[1][1]}\n")
        print(f"Saved to {txtFilename}")


# 초기 전역변수 설정
# boxList -> 그린 박스의 좌표를 저장하는 리스트
# startPt -> 마우스 왼쪽 버튼이 눌린 후 시작 좌표를 저장
# cpy -> 이미지의 사본을 저장하는 변수
# txtWrData -> 텍스트 파일로 저장할 좌표 데이터를 문자열 형태로 저장

# 마우스가 눌리지 않으면 좌표값은 없음
boxList = [] # 빈 리스트
startPt = None
txtWrData = None
currentIndex = 0 # 현재 이미지 인덱스


# getImageList() 함수를 통해 첫 번째 이미지를 불러와 창에 표시하고
# 마우스 콜백 함수를 설정하여 마우스로 박스를 그릴 수 있게 함
fileNames = getImageList()


# 이미지 불러오기 및 윈도우 설정
def loadImage(index):
    global img, boxList, cpy
    img = cv2.imread(fileNames[index])  # 파일 불러오기
    boxList = []  # 박스 리스트 초기화
    cpy = img.copy()  # 이미지 복사본 만들기
    cv2.imshow('label', cpy)  # 이미지 띄우기

cv2.namedWindow('label')
cv2.setMouseCallback('label', onMouse)

loadImage(currentIndex)  # 첫 번째 이미지 로드



while True:
    key = cv2.waitKey(0)
    
    # print(f"Key pressed: {key}") # 디버깅용: 눌린 키 값 출력
    
    if key==27: # ESC 키를 누르면 프로그램을 종료
        break
    elif key==ord('s'): # s 키를 누르면 현재 이미지의 사각형 좌표를 텍스트 파일로 저장
        filename, ext = os.path.splitext(fileNames[currentIndex])
        saveBoxData(filename)
    elif key == ord('c'): # c키를 누르면 모든 박스 초기화
        boxList = []
        cpy = img.copy()
        cv2.imshow('label', cpy)
    elif key == 0: # 오른쪽 화살표 (->) 키 입력
        if currentIndex < len(fileNames) - 1:
            filename, ext = os.path.splitext(fileNames[currentIndex])
            saveBoxData(filename) # 현재 이미지 좌표 저장
            currentIndex += 1
            loadImage(currentIndex) # 다음 이미지 로드
    # elif key == ord('81'): # 왼쪽 화살표(<-) 키 입력

cv2.destroyAllWindows()