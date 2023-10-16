<p align="center"><img src="https://github.com/Annjieun/falko/assets/87294962/0fb4cc05-7a3c-4c0c-80d3-70ddf7184e4a"></p>

# Falko
#### YOLO를 이용한 무단 착석 감지 프로그램

<br><br>

#### Note
이 레포지토리는 개인 정보가 포함된 소스코드는 제외되어 있습니다.
<br><br>

## ☑️ Contents

[1. Project Summary](#1-project-summary)

[2. Project Purpose](#2-project-purpose)

[3. Project Target](#3-project-target)

[4. Project structure](#4-project-structure)

[5. Main Features](#5-main-features)

[6. Extra Features](#6-extra-features)

[7. Development Schedule](#7-development-schedule)

[8. Contributor](#8-contributor)

<br>

## 1. Project Summary
<p align="center"><img src="https://github.com/Annjieun/falko/assets/87294962/c7f2430b-0e0e-46dc-aef3-79d8e396f3d7" width="450" ></p>

Falko는 영화관이나 기차 등에서 발생하는 무단 착석을 실시간 모니터링을 통해 감지할 수 있는 프로그램입니다. 사용자가 버튼을 누르면 컴퓨터와 연결된 카메라를 통해 좌석 인식 및 라벨링을 진행한 후, 해당 좌석 정보를 기반으로 무단 착석을 감지할 수 있습니다. 한 구역 뿐만 아니라 동시에 여러 구역에서 모니터링이 가능하며 무단 착석이 감지되면 해당 좌석에 빨간 박스로 표시됩니다.

<br>

## 2. Project Purpose
Falko 목적은 비대면 및 최소한의 인력으로 실시간 모니터링만을 통해 언제나 무단 착석을 감지할 수 있도록 하는 데에 있습니다. 기존에 사람이 수행하던 무단 착석 감지 작업을, 카메라를 통해 여러 공간을 동시에 모니터링하며 무단 착석을 직관적으로 감지할 수 있는 시스템으로 대체하는 것이 목적입니다. 

기차나 영화관 등 예약 여부가 존재하고, 지정된 좌석에 착석을 하는 곳이라면 해당 시스템을 이용할 수 있도록 합니다. 또한 기존보다 적은 인력으로 무단 착석 감지가 가능함으로써, 영화관이나 코레일 등의 입장에서 적은 자본으로 높은 효율을 얻도록 합니다.

<br>

## 3. Project Target
영화관이나 극장을 운영하는 기업과 교통수단 관련 기업을 타겟으로 설정하였습니다.

<br>

## 4. Project structure
<p align="center"><img src="https://github.com/Annjieun/falko/assets/87294962/684ba726-2f26-4705-b437-ba960120fb2b" width="450" ></p>
<br>
고객이 영화 사이트를 통해 영화를 예매하면, 예매된 좌석 번호가 데이터베이스에 저장됩니다. Falko에서는 해당 영화 사이트의 API를 호출하여 데이터베이스에 저장된 예매 좌석 번호를 가져옵니다. 이러한 정보를 기반으로, Falko는 카메라를 통해 무단 착석 감지를 실시합니다.

<p align="center"><img src="https://github.com/Annjieun/falko/assets/87294962/d8596cf1-5529-4acb-969e-fbb18378fb89" width="450" ></p>



<br>

## 5. Main Features
<p align="center"><img src="https://github.com/Annjieun/falko/assets/87294962/86b89406-6ea4-4a28-853b-939d0d7e1514" width="450" ></p>

메인 화면입니다.

### 5.1 좌석 위치 정보 생성 - 좌석 인식 & 좌석 라벨
<p align="center"><img src="https://github.com/Annjieun/falko/assets/87294962/372897a1-63c0-4e59-9238-156907f06959" width="450" ></p>
<p align="center"><img src="https://github.com/Annjieun/falko/assets/87294962/6e227841-b863-4fa0-bf6d-27f024d5ff09" width="450" ></p>

영화 사이트에 접속하여 영화를 예매합니다.

<p align="center"><img src="https://github.com/Annjieun/falko/assets/87294962/6422398b-5bfa-4155-9d1d-5edd736e52ef" width="450" ></p>

Capture – Seat Capture(혹은 Ctrl + Alt + C)를 클릭합다.

<p align="center"><img src="https://github.com/Annjieun/falko/assets/87294962/4c3c09ee-4fca-452c-afc0-c2e9af4cd477" width="450" ></p>

폴더 버튼을 눌러 좌석 정보 텍스트 파일을 저장할 경로를 선택합니다.

<p align="center"><img src="https://github.com/Annjieun/falko/assets/87294962/8a13be30-951f-4cef-817f-fbd66b84fb55" width="450" ></p>
<p align="center"><img src="https://github.com/Annjieun/falko/assets/87294962/66f57c4d-7106-4fe3-a77c-afee881aee2a" width="450" ></p>

좌석 정보가 필요한 카메라 버튼을 클릭하면 falko가 인식한 좌석 정보가 제공됩다.

<p align="center"><img src="https://github.com/Annjieun/falko/assets/87294962/676010fa-4d7c-426e-8c35-1cfb7a6b9dd9" width="450" ></p>
<p align="center"><img src="https://github.com/Annjieun/falko/assets/87294962/6a743b42-cf1d-4458-bb86-79be1ecbb3f2" width="450" ></p>

Destination Folder 아래, 좌석 위치 정보가 저장되어있는 텍스트 파일이 “[자신이 선택한 카메라 알파벳]_seat_informaion.txt”의 제목으로 저장됩니다.

<br>

### 5.2 좌석 위치 정보 설정
<p align="center"><img src="https://github.com/Annjieun/falko/assets/87294962/f2be5411-c166-4431-b231-9065375e71d9" width="450" ></p>

Settings - Seat Setting(혹은 Ctrl + Alt + S)을 클릭합니다.

<p align="center"><img src="https://github.com/Annjieun/falko/assets/87294962/8b3219b4-d449-4e3e-ab0d-dbebd020ebd3" width="450" ></p>
<p align="center"><img src="https://github.com/Annjieun/falko/assets/87294962/877f454a-49ea-4bc4-b3c1-b58e98a02079" width="450" ></p>

각 카메라의 폴더 버튼을 클릭하여 이전에 생성한 좌석 위치 정보 텍스트 파일을 불러옵옵니다.

<br>

### 5.3 무단 착석 감지

<p align="center"><img src="https://github.com/Annjieun/falko/assets/87294962/86caa01a-4737-493f-a953-3ab4b670c934" width="450" ></p>

카메라 ON 버튼을 누르면 해당 공간의 무단 착석 감지를 시작합니다.

<p align="center"><img src="https://github.com/Annjieun/falko/assets/87294962/2a3d976d-b6e3-44d1-b45e-500f27cb3d72" width="450" ></p>
** 이때 좌석 위치 정보 설정(5.2)을 하지 않고 카메라를 킬 경우 아래와 같은 경고창이 나타나게 됩니다. 

<p align="center"><img src="https://github.com/Annjieun/falko/assets/87294962/394fac41-f28c-48c3-9e7d-3a3d591a3851" width="450" ></p>

① 무단으로 착석하면 해당 좌석 영역에 빨간 박스가 나타납니다.

② Unauthorized seat에 무단 착석자가 앉아있는 좌석 번호가 나타납니다.

③ 해당 공간의 예약된 좌석 수와 현재 사람 수 정보가 제공됩니다.

<p align="center"><img src="https://github.com/Annjieun/falko/assets/87294962/90942e25-8349-4169-aa78-450ddb62e370" width="450" ></p>

카메라 OFF 버튼을 누르면 무단 착석 감지가 종료됩니다. 이때, 무단 착석자가 앉은 좌석 정보를 띄우는 Unauthorized Seat 칸이 리셋되며 예약된 좌석 수와 현재 사람 수 count 값은 0으로 리셋됩다.

<p align="center"><img src="https://github.com/Annjieun/falko/assets/87294962/8dcc9e57-b440-40e2-8b83-44774c23ddcc" width="450" ></p>

4개의 카메라 공간에서 무단 착석을 동시에 감지할 수 있습니다.

<br><br>

## 6. Extra Features
### 6.1 무단 착석자가 앉은 좌석 번호 저장

<p align="center"><img src="https://github.com/Annjieun/falko/assets/87294962/34cdd0f9-9b83-4349-b81e-fc1522236fca" width="450" ></p>
<p align="center"><img src="https://github.com/Annjieun/falko/assets/87294962/89739a7b-d14e-4c97-8b5b-f40222da208e" width="450" ></p>

File – Save를 클릭하여 좌석 번호를 저장할 폴더를 선택하고, 파일명을 적은 후 저장 버튼을 누릅니다.

<p align="center"><img src="https://github.com/Annjieun/falko/assets/87294962/0fe62eb9-852c-4403-a144-981218efcacf" width="450" ></p>

Save를 누른 시점의 무단 착석 좌석 번호가 각 카메라 영역 별로 저장됩니다.

<br>

### 6.2 Falko 정보 및 사용법
<p align="center"><img src="https://github.com/Annjieun/falko/assets/87294962/b8dfd1e2-711d-42fd-b7c5-55fe0e800cce" width="450" ></p>
<p align="center"><img src="https://github.com/Annjieun/falko/assets/87294962/e2322a39-fb9a-491d-ae22-a1297295894c" width="450" ></p>

Help – falko Information을 클릭하면 Falko에 대한 간단한 설명과 제작자를 확인할 수 있습니다.

<p align="center"><img src="https://github.com/Annjieun/falko/assets/87294962/26886868-fa3a-4395-ab54-b8f505abf05e" width="450" ></p>
<p align="center"><img src="https://github.com/Annjieun/falko/assets/87294962/e26009d8-bf56-4bf3-b9b5-78fe79dafbff" width="450" ></p>

Help – Join Us on Git을 클릭하면 Github 링크로 이동하면서 Falko 사용법에 관한 정보를 확인할 수 있습니다.

<br><br>

## 7. Development Schedule
- 2022.09 ~ 2022.12 : 주제 선정 및 개발 구성 & 관련 내용 학습
- 2023.01 ~ 2023.02 : YOLO 모델 학습 및 선정
- 2023.02 ~ 2023.03 : 영화 사이트 수정 및 DB 관리
- 2023.03 ~ 2023.04 : 무단 착석 알고리즘
- 2023.04 ~ 2023.06 : 영화 사이트 배포 & 무단 착석 감지 테스트
- 2023.05 ~ 2023.06 : GUI 제작 & 실행파일 배초
- 2023.06 : 최종 마무리 및 보고서 작성

<br><br>

## 8. Contributor
안지은, 이세영, 이지은
