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

span=11
C40='C40'
C30='C30'

session.journalOptions.setValues(replayGeometry=COORDINATE,recoverGeometry=COORDINATE)

#create model
myModel = mdb.Model(name=modelName)

#create sketch
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

#create material
#deck material
mdb.models[modelName].Material(name=C40)
mdb.models[modelName].materials[C40].Elastic(table=((3.25e10, 0.2), 
    ))
#pavemoent material
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

##create assembly
a = mdb.models[modelName].rootAssembly

p = mdb.models[modelName].parts[deckName]

a.Instance(name='Plate-1', part=p, dependent=OFF)

#create partition
f1 = a.instances['Plate-1'].faces
pickedFaces = f1.findAt(((7.333333, 4.333333, 0.0), ))
e1 = a.instances['Plate-1'].edges
a.PartitionFaceByShortestPath(faces=pickedFaces, 
    point1=a.instances['Plate-1'].InterestingPoint(edge=e1.findAt(coordinates=(
    5.5, 14.25, 0.0)), rule=MIDDLE), 
    point2=a.instances['Plate-1'].InterestingPoint(edge=e1.findAt(coordinates=(
    16.5, 0.0, 0.0)), rule=MIDDLE))

#create boundry set
e1 = a.instances['Plate-1'].edges

#left
edges1 = e1.findAt(((0.0, 1.0, 0.0), ))
a.Set(edges=edges1, name='End-1')

#middle
edges1 = e1.findAt(((span, 1.0, 0.0), ))
a.Set(edges=edges1, name='End-2')

#right
edges1 = e1.findAt(((2*span, 1.0, 0.0), ))
a.Set(edges=edges1, name='End-3')

#Create Step
mdb.models[modelName].StaticStep(name='ApplyLoad', previous='Initial')
#set field output
mdb.models['FuzhouHouyuRoad'].fieldOutputRequests['F-Output-1'].setValues(
    variables=('S', 'PE', 'PEEQ', 'PEMAG', 'LE', 'U', 'RF', 'CF', 'SF', 
    'CSTRESS', 'CDISP'))

#create boundry
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
currPos=0.5
while currPos<2*span:

    tuplePoint=((currPos,3.0,0),)

    tupleLoad=(-1,)

    for i in range(0,len(tuplePoint)):
        ref1=a.ReferencePoint(point=tuplePoint[i])
        r1 = a.referencePoints
        refPoints1=(r1[ref1.id], )
        region1=a.Set(referencePoints=refPoints1, name='m_Set-'+str(i+30))
        s1 = a.instances['Plate-1'].faces

        #TODO: according to tuplePoint to find faces
        side1Faces1 = s1.findAt(((currPos-0.1, 5.0, 0), ))

        region2=a.Surface(side1Faces=side1Faces1, name='s_Surf-'+str(i+30))
        mdb.models[modelName].Coupling(name='Constraint-RP'+str(i+1), 
            controlPoint=region1, surface=region2, influenceRadius=0.1, 
            couplingType=DISTRIBUTING, weightingMethod=UNIFORM, localCsys=None, u1=ON, 
            u2=ON, u3=ON, ur1=ON, ur2=ON, ur3=ON)

        region = regionToolset.Region(referencePoints=refPoints1)
        mdb.models[modelName].ConcentratedForce(name='Load-'+str(i+1), 
            createStepName='ApplyLoad', region=region, cf3=tupleLoad[i], 
            distributionType=UNIFORM, field='', localCsys=None)

    #create mesh
    partInstances =(a.instances['Plate-1'], )
    a.seedPartInstance(regions=partInstances, size=0.2, deviationFactor=0.1, 
        minSizeFactor=0.1)
    a = mdb.models[modelName].rootAssembly
    partInstances =(a.instances['Plate-1'], )
    a.generateMesh(regions=partInstances)

    #job
    mdb.Job(name='Job-2', model=modelName, description='', type=ANALYSIS, 
        atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90, 
        memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True, 
        explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, 
        modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', 
        scratch='', resultsFormat=ODB, multiprocessingMode=DEFAULT, numCpus=1, 
        numGPUs=0)
    mdb.jobs['Job-2'].submit(consistencyChecking=OFF)


    #post

    from odbAccess import *
    jobName='Job-2'
    mdb.jobs['Job-2'].waitForCompletion()

    #ms=myJob.messages[-1]

    instanceName='Plate-1'
    stepName='ApplyLoad'

    frame=1

    x,y=[],[]

    #if ms.type==JOB_COMPLETED:
    odbPath=jobName+'.odb'
    o=openOdb(path=odbPath,readOnly=True)
    #ns=o.rootAssembly.instances[instanceName.upper()].nodes
    fopSM=o.steps[stepName].getFrame(frameValue=frame).fieldOutputs['SM'].values    #SM1

    (sm1, sm2, sm3) = fopSM[6689].data

    #print str(u2)

    with open("sm.txt","a") as f:
        f.write(str(sm2))
        f.write('\n')

    o.close()

    currPos=currPos+0.5

