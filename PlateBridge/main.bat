
set fileName=GuanglinzhongBridgeEntity.py
set fromPath=D:\vsProjects\GuanglinzhongBridgeEntity\GuanglinzhongBridgeEntity
set toPath=D:\simulia\temp\

xcopy %fromPath% %toPath%  /e /h /y
abaqus cae noGUI=%toPath%%fileName%

