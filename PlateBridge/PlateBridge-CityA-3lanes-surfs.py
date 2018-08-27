# -*- coding: mbcs -*-
#
# Abaqus/CAE Release 6.14-1
# Internal Version: 2014_06_05-06.11.02 134264
# Run by eamdf on Tue Aug 21 16:58:48 2018
#

# from driverUtils import executeOnCaeGraphicsStartup
# executeOnCaeGraphicsStartup()
#: Executing "onCaeGraphicsStartup()" in the site directory ...

from abaqus import *
from abaqusConstants import *
from caeModules import *
from driverUtils import executeOnCaeStartup

modelName='FuzhouHouyuRoad'
deckName='BridgeDeck'
pavedeckName='PaveDeck'

span=11
C40='C40'
C30='C30'

session.journalOptions.setValues(replayGeometry=COORDINATE,recoverGeometry=COORDINATE)

#create model
myModel = mdb.Model(name=modelName)

#create sketch
#bridgedeck
s1 = mdb.models[modelName].ConstrainedSketch(name='__profile__', sheetSize=4.0)
g, v, d, c = s1.geometry, s1.vertices, s1.dimensions, s1.constraints
s1.Line(point1=(0.0, 0.0), point2=(0.0, 13))
s1.Line(point1=(0.0, 13), point2=(22,18))
s1.Line(point1=(22, 18), point2=(22, 0.0))
s1.Line(point1=(22, 0.0), point2=(0.0, 0.0))

#create part
p = mdb.models[modelName].Part(name=deckName, dimensionality=THREE_D, 
    type=DEFORMABLE_BODY)
p = mdb.models[modelName].parts[deckName]
p.BaseShell(sketch=s1)

#del sketch
del mdb.models[modelName].sketches['__profile__']

#pave
s1 = mdb.models[modelName].ConstrainedSketch(name='__profile__', sheetSize=4.0)
g, v, d, c = s1.geometry, s1.vertices, s1.dimensions, s1.constraints
s1.Line(point1=(0.0, 15-3.5), point2=(2*span, 20-5.7))
s1.Line(point1=(2*span, 20-5.7), point2=(2*span,20))
s1.Line(point1=(2*span, 20), point2=(0, 15))
s1.Line(point1=(0, 15), point2=(0.0, 15-3.5))

#create part
p = mdb.models[modelName].Part(name=pavedeckName, dimensionality=THREE_D, 
    type=DEFORMABLE_BODY)
p = mdb.models[modelName].parts[pavedeckName]
p.BaseShell(sketch=s1)

#del sketch
del mdb.models[modelName].sketches['__profile__']

#create material
#deck material
mdb.models[modelName].Material(name=C40)
mdb.models[modelName].materials[C40].Elastic(table=((3.25e10, 0.2), 
    ))
#pavement material
mdb.models[modelName].Material(name=C30)
mdb.models[modelName].materials[C30].Elastic(table=((3.00e10, 0.2), 
    ))

mdb.models[modelName].HomogeneousShellSection(name='DeckSection', 
    preIntegrate=ON, material=C40, thicknessType=UNIFORM, thickness=0.50, 
    thicknessField='', idealization=NO_IDEALIZATION, poissonDefinition=DEFAULT, 
    thicknessModulus=None, useDensity=OFF)
#assign section
p = mdb.models[modelName].parts[deckName]
f = p.faces
faces = f.findAt(((1.0,1.0, 0.0), ))
region = regionToolset.Region(faces=faces)

p.SectionAssignment(region=region, sectionName='DeckSection', offset=0.0, 
    offsetType=MIDDLE_SURFACE, offsetField='', 
    thicknessAssignment=FROM_SECTION)

#calc thickness approximately
mdb.models[modelName].HomogeneousShellSection(name='PaveSection', 
    preIntegrate=ON, material=C30, thicknessType=UNIFORM, thickness=0.30, 
    thicknessField='', idealization=NO_IDEALIZATION, poissonDefinition=DEFAULT, 
    thicknessModulus=None, useDensity=OFF)

p = mdb.models[modelName].parts[pavedeckName]
f = p.faces
faces = f.findAt(((1.0,14.0, 0.0), ))
region = regionToolset.Region(faces=faces)

p.SectionAssignment(region=region, sectionName='PaveSection', offset=0.0, 
    offsetType=MIDDLE_SURFACE, offsetField='', 
    thicknessAssignment=FROM_SECTION)



##create assembly
a = mdb.models[modelName].rootAssembly

p = mdb.models[modelName].parts[deckName]

a.Instance(name='Plate-1', part=p, dependent=OFF)

p = mdb.models[modelName].parts[pavedeckName]
a.Instance(name='Plate-2', part=p, dependent=OFF)


#: The instance Plate-2 was translated by 0., 0., 400.E-03 with respect to the assembly coordinate system
#0.40=0.30/2+0.50/2
a = mdb.models[modelName].rootAssembly
a.translate(instanceList=('Plate-2', ), vector=(0.0, 0.0, 0.4))

#create set
#left
e1 = a.instances['Plate-1'].edges
edges1 = e1.findAt(((0.0, 3.875, 0.0), ))
a.Set(edges=edges1, name='End-1')
region = a.sets['End-1']

#middle
#edges1 = e1.findAt(((span, 1.0, 0.0), ))
#a.Set(edges=edges1, name='End-2')

#right
edges1 = e1.findAt(((2*span, 1.0, 0.0), ))
a.Set(edges=edges1, name='End-3')

s1 = a.instances['Plate-1'].faces
side1Faces1 = s1.findAt(((7.333333, 5.333333, 0.0), ))
a.Surface(side1Faces=side1Faces1, name='s_Surf-Plate1')

#create partition
#f1 = a.instances['Plate-1'].faces
#pickedFaces = f1.findAt(((7.333333, 4.333333, 0.0), ))
#e1 = a.instances['Plate-1'].edges
#a.PartitionFaceByShortestPath(faces=pickedFaces, 
#    point1=a.instances['Plate-1'].InterestingPoint(edge=e1.findAt(coordinates=(
#    5.5, 14.25, 0.0)), rule=MIDDLE), 
#    point2=a.instances['Plate-1'].InterestingPoint(edge=e1.findAt(coordinates=(
#    16.5, 0.0, 0.0)), rule=MIDDLE))

#create DatumPoint on Plate-1 by proj
a = mdb.models[modelName].rootAssembly
v1 = a.instances['Plate-2'].vertices
f1 = a.instances['Plate-1'].faces
dP1=a.DatumPointByProjOnFace(point=v1.findAt(coordinates=(0.0, 11.5, 0.4)), 
    face=f1.findAt(coordinates=(7.333333, 9.5, 0.0)))

v11 = a.instances['Plate-2'].vertices
f11 = a.instances['Plate-1'].faces
dP2=a.DatumPointByProjOnFace(point=v11.findAt(coordinates=(22.0, 14.3, 0.4)), 
    face=f11.findAt(coordinates=(14.666667, 5.166667, 0.0)))

#create DatumPoint on Plate-2 by proj
v1 = a.instances['Plate-1'].vertices
f1 = a.instances['Plate-2'].faces
dP3=a.DatumPointByProjOnFace(point=v1.findAt(coordinates=(0.0, 13.0, 0.0)), 
    face=f1.findAt(coordinates=(7.333333, 13.6, 0.4)))

v11 = a.instances['Plate-1'].vertices
f11 = a.instances['Plate-2'].faces
dP4=a.DatumPointByProjOnFace(point=v11.findAt(coordinates=(22.0, 18.0, 0.0)), 
    face=f11.findAt(coordinates=(7.333333, 13.6, 0.4)))

#create partition
f1 = a.instances['Plate-1'].faces
pickedFaces = f1.findAt(((14.666667, 5.166667, 0.0), ))
d1 = a.datums
a.PartitionFaceByShortestPath(point1=d1[dP1.id], point2=d1[dP2.id], faces=pickedFaces)

f1 = a.instances['Plate-2'].faces
pickedFaces = f1.findAt(((7.333333, 13.6, 0.4), ))
d11 = a.datums
a.PartitionFaceByShortestPath(point1=d11[dP3.id], point2=d11[dP4.id], 
    faces=pickedFaces)

#create interaction
a = mdb.models[modelName].rootAssembly
s1 = a.instances['Plate-1'].faces
side1Faces1 = s1.findAt(((7.333333, 12.933333, 0.0), ))
region1=regionToolset.Region(side1Faces=side1Faces1)
a = mdb.models[modelName].rootAssembly
s1 = a.instances['Plate-2'].faces
side2Faces1 = s1.findAt(((14.666667, 15.1, 0.4), ))
region2=regionToolset.Region(side2Faces=side2Faces1)
mdb.models[modelName].Tie(name='Constraint-1', master=region1, 
    slave=region2, positionToleranceMethod=COMPUTED, adjust=ON, 
    tieRotations=ON, thickness=ON)

#create middle partition
a = mdb.models[modelName].rootAssembly
f1 = a.instances['Plate-1'].faces
pickedFaces = f1.findAt(((7.333333, 12.933333, 0.0), ), ((14.666667, 8.6, 0.0), 
    ))
e11 = a.instances['Plate-1'].edges
a.PartitionFaceByShortestPath(faces=pickedFaces, 
    point1=a.instances['Plate-1'].InterestingPoint(edge=e11.findAt(
    coordinates=(16.5, 0.0, 0.0)), rule=MIDDLE), 
    point2=a.instances['Plate-1'].InterestingPoint(edge=e11.findAt(
    coordinates=(5.5, 14.25, 0.0)), rule=MIDDLE))

#middle
e1 = a.instances['Plate-1'].edges
edges1 = e1.findAt(((span, 1.0, 0.0), ), ((span, 14.2, 0.0), ))
a.Set(edges=edges1, name='End-2')

f1 = a.instances['Plate-2'].faces
pickedFaces = f1.findAt(((7.333333, 15.333333, 0.4), ), ((14.666667, 15.1, 
    0.4), ))
e1 = a.instances['Plate-2'].edges
a.PartitionFaceByShortestPath(faces=pickedFaces, 
    point1=a.instances['Plate-2'].InterestingPoint(edge=e1.findAt(coordinates=(
    5.5, 12.2, 0.4)), rule=MIDDLE), 
    point2=a.instances['Plate-2'].InterestingPoint(edge=e1.findAt(coordinates=(
    16.5, 18.75, 0.4)), rule=MIDDLE))

#create vehicle lane
laneWidth=3.5

dP11=a.DatumPointByCoordinate(coords=(0, 3-laneWidth/2, 0))
dP12=a.DatumPointByCoordinate(coords=(0, 3+3.5-laneWidth/2, 0))
dP13=a.DatumPointByCoordinate(coords=(0, 3+3.5+3.5-laneWidth/2, 0))
dP14=a.DatumPointByCoordinate(coords=(0, 3+3.5+3.5+laneWidth/2, 0))

dP21=a.DatumPointByCoordinate(coords=(22, 3-laneWidth/2, 0))
dP22=a.DatumPointByCoordinate(coords=(22, 3+3.5-laneWidth/2, 0))
dP23=a.DatumPointByCoordinate(coords=(22, 3+3.5+3.5-laneWidth/2, 0))
dP24=a.DatumPointByCoordinate(coords=(22, 3+3.5+3.5+laneWidth/2, 0))

f1 = a.instances['Plate-1'].faces
pickedFaces = f1.findAt(((7.333333, 3-laneWidth/2-0.1, 0.0), ), ((14.666667, 3-laneWidth/2-0.1, 0.0), 
    ))
d1 = a.datums
a.PartitionFaceByShortestPath(point1=d1[dP11.id], point2=d1[dP21.id], faces=pickedFaces)

f1 = a.instances['Plate-1'].faces
pickedFaces = f1.findAt(((3.666667, 3+3.5-laneWidth/2-0.1, 0.0), ), ((14.666667, 3+3.5-laneWidth/2-0.1, 0.0), 
    ))
d11 = a.datums
a.PartitionFaceByShortestPath(point1=d11[dP12.id], point2=d11[dP22.id], 
    faces=pickedFaces)

f1 = a.instances['Plate-1'].faces
pickedFaces = f1.findAt(((3.666667, 3+3.5+3.5-laneWidth/2-0.1, 0.0), ), ((14.666667, 3+3.5+3.5-laneWidth/2-0.1, 
    0.0), ))
d1 = a.datums
a.PartitionFaceByShortestPath(point1=d1[dP13.id], point2=d1[dP23.id], faces=pickedFaces)

f1 = a.instances['Plate-1'].faces
pickedFaces = f1.findAt(((3.666667, 3+3.5+3.5+laneWidth/2-0.1, 0.0), ), ((14.666667, 3+3.5+3.5+laneWidth/2-0.1, 
    0.0), ))
d1 = a.datums
a.PartitionFaceByShortestPath(point1=d1[dP14.id], point2=d1[dP24.id], faces=pickedFaces)

#create rp point
#concentrated load
e11 = a.instances['Plate-1'].edges
#rp1~3
rp11=a.ReferencePoint(point=(5.5, 3.0, 0.0))
e1 = a.instances['Plate-1'].edges
rp12=a.ReferencePoint(point=(5.5, 6.5, 0.0))
e11 = a.instances['Plate-1'].edges
rp13=a.ReferencePoint(point=(5.5, 10.0, 0.0))

##line load
##rp4~6
#e11 = a.instances['Plate-1'].edges
#rp21=a.ReferencePoint(point=a.instances['Plate-1'].InterestingPoint(edge=e11.findAt(
#    coordinates=(8.25, 3.0, 0.0)), rule=MIDDLE))
#e1 = a.instances['Plate-1'].edges
#rp22=a.ReferencePoint(point=a.instances['Plate-1'].InterestingPoint(edge=e1.findAt(
#    coordinates=(8.25, 6.5, 0.0)), rule=MIDDLE))
#e11 = a.instances['Plate-1'].edges
#rp23=a.ReferencePoint(point=a.instances['Plate-1'].InterestingPoint(edge=e11.findAt(
#    coordinates=(8.25, 10.0, 0.0)), rule=MIDDLE))

#a = mdb.models['FuzhouHouyuRoad'].rootAssembly
#s1 = a.instances['Plate-1'].faces
#side1Faces1 = s1.findAt(((3.666667, 12.466667, 0.0), ), ((14.666667, 14.233333, 
#    0.0), ))
#region1=a.Surface(side1Faces=side1Faces1, name='m_Surf-13')
#a = mdb.models['FuzhouHouyuRoad'].rootAssembly
#s1 = a.instances['Plate-2'].faces
#side2Faces1 = s1.findAt(((14.666667, 15.1, 0.4), ))
#region2=a.Surface(side2Faces=side2Faces1, name='s_Surf-13')
#mdb.models['FuzhouHouyuRoad'].Tie(name='Constraint-13', master=region1, 
#    slave=region2, positionToleranceMethod=COMPUTED, adjust=ON, 
#    tieRotations=ON, thickness=ON)


##create boundry set


#left
#edges1 = e1.findAt(((0.0, 1.0, 0.0), ))
#a.Set(edges=edges1, name='End-1')
#e1 = a.instances['Plate-1'].edges
#edges1 = e1.findAt(((0.0, 10.375, 0.0), ), ((0.0, 7.375, 0.0), ), ((0.0, 3.875, 
#    0.0), ), ((0.0, 0.75, 0.0), ), ((0.0, 11.875, 0.0), ))
#a.Set(edges=edges1, name='End-1')

##middle
##edges1 = e1.findAt(((span, 1.0, 0.0), ))
##a.Set(edges=edges1, name='End-2')

#edges1 = e1.findAt(((11.0, 9.125, 0.0), ), ((11.0, 12.175, 0.0), ), ((11.0, 
#    5.625, 0.0), ), ((11.0, 2.25, 0.0), ), ((11.0, 14.85, 0.0), ))
#a.Set(edges=edges1, name='End-2')

##right
##edges1 = e1.findAt(((2*span, 1.0, 0.0), ))
##a.Set(edges=edges1, name='End-3')
#edges1 = e1.findAt(((22.0, 9.125, 0.0), ), ((22.0, 5.625, 0.0), ), ((22.0, 
#    2.25, 0.0), ), ((22.0, 17.075, 0.0), ), ((22.0, 13.225, 0.0), ))
#a.Set(edges=edges1, name='End-3')

#Create Step
mdb.models[modelName].StaticStep(name='ApplyLoad', previous='Initial')
#set field output
mdb.models['FuzhouHouyuRoad'].fieldOutputRequests['F-Output-1'].setValues(
    variables=('S', 'PE', 'PEEQ', 'PEMAG', 'LE', 'U', 'RF', 'CF', 'SF', 
    'NFORC', 'CSTRESS', 'CDISP'))

##create boundry
region = a.sets['End-1']
mdb.models[modelName].DisplacementBC(name='BC-1', createStepName='ApplyLoad', 
    region=region, u1=0.0, u2=0.0, u3=0.0, ur1=0.0, ur2=UNSET, ur3=0.0, 
    amplitude=UNSET, fixed=OFF, distributionType=UNIFORM, fieldName='', 
    localCsys=None)

region = a.sets['End-2']
mdb.models[modelName].DisplacementBC(name='BC-2', createStepName='ApplyLoad', 
    region=region, u1=0.0, u2=0.0, u3=0.0, ur1=0.0, ur2=UNSET, ur3=0.0, 
    amplitude=UNSET, fixed=OFF, distributionType=UNIFORM, fieldName='', 
    localCsys=None)

region = a.sets['End-3']
mdb.models[modelName].DisplacementBC(name='BC-3', createStepName='ApplyLoad', 
    region=region, u1=0.0, u2=0.0, u3=0.0, ur1=0.0, ur2=UNSET, ur3=0.0, 
    amplitude=UNSET, fixed=OFF, distributionType=UNIFORM, fieldName='', 
    localCsys=None)

#create load
largeNum=50
#create cload
rPoint=(rp11,rp12,rp13)
tupleLoad=(-204000,-204000,-204000)

for i in range(0,len(rPoint)):

    r1 = a.referencePoints
    refPoints1=(r1[rPoint[i].id], )
    region1=a.Set(referencePoints=refPoints1, name='m_Set-'+str(i+largeNum))
    s1 = a.instances['Plate-1'].faces

    #TODO:using set
    side1Faces1 = s1.findAt(((18.333333, 8.833333, 0.0), ), ((3.666667, 10.5, 0.0), 
        ), ((18.333333, 5.333333, 0.0), ), ((7.333333, 8.833333, 0.0), ), ((
        18.333333, 2.0, 0.0), ), ((7.333333, 5.333333, 0.0), ), ((7.333333, 2.0, 
        0.0), ), ((7.333333, 13.8, 0.0), ), ((14.666667, 14.233333, 0.0), ), ((
        14.666667, 10.966667, 0.0), ))

    region2=a.Surface(side1Faces=side1Faces1, name='s_Surf-'+str(i+largeNum))
    mdb.models[modelName].Coupling(name='Constraint-RP'+str(i+1), 
        controlPoint=region1, surface=region2, influenceRadius=0.1, 
        couplingType=DISTRIBUTING, weightingMethod=UNIFORM, localCsys=None, u1=ON, 
        u2=ON, u3=ON, ur1=ON, ur2=ON, ur3=ON)

    region = regionToolset.Region(referencePoints=refPoints1)
    mdb.models[modelName].ConcentratedForce(name='Load-'+str(i+1), 
        createStepName='ApplyLoad', region=region, cf3=tupleLoad[i], 
        distributionType=UNIFORM, field='', localCsys=None)

a = mdb.models[modelName].rootAssembly
s1 = a.instances['Plate-1'].faces
side2Faces1 = s1.findAt(((7.333333, 3.583333, 0.0), ))
region = a.Surface(side2Faces=side2Faces1, name='Surf-7')
mdb.models[modelName].Pressure(name='Load-4', 
    createStepName='ApplyLoad', region=region, distributionType=UNIFORM, 
    field='', magnitude=-3000.0, amplitude=UNSET)

s1 = a.instances['Plate-1'].faces
side2Faces1 = s1.findAt(((7.333333, 7.083333, 0.0), ))
region = a.Surface(side2Faces=side2Faces1, name='Surf-8')
mdb.models[modelName].Pressure(name='Load-5', 
    createStepName='ApplyLoad', region=region, distributionType=UNIFORM, 
    field='', magnitude=-3000.0, amplitude=UNSET)

s1 = a.instances['Plate-1'].faces
side2Faces1 = s1.findAt(((7.988095, 10.583333, 0.0), ))
region = a.Surface(side2Faces=side2Faces1, name='Surf-9')
mdb.models[modelName].Pressure(name='Load-6', 
    createStepName='ApplyLoad', region=region, distributionType=UNIFORM, 
    field='', magnitude=-3000.0, amplitude=UNSET)

##create line cload
#q=10.5
#rPoint=(rp21,rp22,rp23)
#tupleLoad=(-q*span*1000,-q*span*1000,-q*span*1000)
#edgeTuple=((8.25, 3.0, 0.0),(8.25, 6.5, 0.0),(8.25, 10.0, 0.0))

#for i in range(0,len(rPoint)):
#    r1 = a.referencePoints
#    refPoints1=(r1[rPoint[i].id], )
#    region1=a.Set(referencePoints=refPoints1, name='m_Set-'+str(i+largeNum+3))
#    e1 = a.instances['Plate-1'].edges
#    edges1 = e1.findAt((edgeTuple[i], ))
#    region2=a.Set(edges=edges1, name='s_Set-'+str(i+largeNum+3))
#    mdb.models[modelName].Coupling(name='Constraint-RP'+str(i+largeNum+3), 
#        controlPoint=region1, surface=region2, influenceRadius=WHOLE_SURFACE, 
#        couplingType=DISTRIBUTING, weightingMethod=UNIFORM, localCsys=None, u1=ON, 
#        u2=ON, u3=ON, ur1=ON, ur2=ON, ur3=ON)
#    region = regionToolset.Region(referencePoints=refPoints1)
#    mdb.models[modelName].ConcentratedForce(name='Load-'+str(i+1+3), 
#        createStepName='ApplyLoad', region=region, cf3=tupleLoad[i], 
#        distributionType=UNIFORM, field='', localCsys=None)

#1	5.5,1.5,0
#2	5.5,3.4,0
#3	4.1,1.5,0
#4	4.1,3.4,0
#5	0.3,1.5,0
#6	0.3,3.4,0
#7	5.5,4.8,0
#8	5.5,6.2,0
#9	4.1,4.8,0
#10	4.1,6.2,0
#11	0.3,4.8,0
#12	0.3,6.2,0

#-90
#-90
#-90
#-90
#-45
#-45
#-90
#-90
#-90
#-90
#-45
#-45

#tuplePoint=((5.5,1.5,0),(5.5,3.4,0),(4.1,1.5,0),(4.1,3.4,0),(0.3,1.5,0),(0.3,3.4,0),
#    (5.5,4.8,0),(5.5,6.2,0),(4.1,4.8,0),(4.1,6.2,0),(0.3,4.8,0),(0.3,6.2,0))

#tupleLoad=(-90000,-90000,-90000,-90000,-45000,-45000,
#    -90000,-90000,-90000,-90000,-45000,-45000)

#for i in range(0,len(tuplePoint)):
#    ref1=a.ReferencePoint(point=tuplePoint[i])
#    r1 = a.referencePoints
#    refPoints1=(r1[ref1.id], )
#    region1=a.Set(referencePoints=refPoints1, name='m_Set-'+str(i+30))
#    s1 = a.instances['Plate-1'].faces
#    #TODO: according to tuplePoint to find faces
#    side1Faces1 = s1.findAt(((5.0, 5.0, 0), ))
#    region2=a.Surface(side1Faces=side1Faces1, name='s_Surf-'+str(i+30))
#    mdb.models[modelName].Coupling(name='Constraint-RP'+str(i+1), 
#        controlPoint=region1, surface=region2, influenceRadius=0.1, 
#        couplingType=DISTRIBUTING, weightingMethod=UNIFORM, localCsys=None, u1=ON, 
#        u2=ON, u3=ON, ur1=ON, ur2=ON, ur3=ON)

#    region = regionToolset.Region(referencePoints=refPoints1)
#    mdb.models[modelName].ConcentratedForce(name='Load-'+str(i+1), 
#        createStepName='ApplyLoad', region=region, cf3=tupleLoad[i], 
#        distributionType=UNIFORM, field='', localCsys=None)

##create mesh
#partInstances =(a.instances['Plate-1'], )
#a.seedPartInstance(regions=partInstances, size=0.2, deviationFactor=0.1, 
#    minSizeFactor=0.1)
#a = mdb.models[modelName].rootAssembly
#partInstances =(a.instances['Plate-1'], )
#a.generateMesh(regions=partInstances)

##job
#mdb.Job(name='Job-2', model=modelName, description='', type=ANALYSIS, 
#    atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90, 
#    memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True, 
#    explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, 
#    modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', 
#    scratch='', resultsFormat=ODB, multiprocessingMode=DEFAULT, numCpus=1, 
#    numGPUs=0)
#mdb.jobs['Job-2'].submit(consistencyChecking=OFF)

#a = mdb.models['LinearPlate'].rootAssembly
#partInstances =(a.instances['Plate-1'], )
#a.generateMesh(regions=partInstances)

#mdb.jobs['SkewPlate'].submit(consistencyChecking=OFF)



#a1 = mdb.models['LinearPlate'].rootAssembly
#a1.regenerate()
#a = mdb.models['LinearPlate'].rootAssembly
#session.viewports['Viewport: 1'].setValues(displayedObject=a)
#mdb.jobs['SkewPlate'].submit(consistencyChecking=OFF)
##: The job input file "SkewPlate.inp" has been submitted for analysis.
##: Job SkewPlate: Analysis Input File Processor completed successfully.
##: Job SkewPlate: Abaqus/Standard completed successfully.
##: Job SkewPlate completed successfully. 
