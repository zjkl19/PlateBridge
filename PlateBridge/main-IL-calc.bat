
set fileName=PlateBridge-IL-calc
set fromPath=D:\vsProjects\PlateBridge\PlateBridge
set toPath=D:\simulia\temp\

xcopy %fromPath% %toPath%  /e /h /y
abaqus cae noGUI=%toPath%%fileName%

