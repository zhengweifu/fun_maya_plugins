import maya.cmds as mc

def createPreLoc():

    locs = ['subBrow_M_Loc', 'subBrow_L_LocA', 'subBrow_L_LocB', 'subBrow_L_LocC', 'subBrow_L_LocD', 'subBrow_L_LocE', 'subBrow_L_LocF', 'subBrow_L_LocG',
    'subEye_L_LocA', 'subEye_L_LocB', 'subEye_L_LocC', 'subEye_L_LocD', 'subEye_L_LocE', 'subEye_L_LocF', 'subEye_L_LocG', 'subEye_L_LocH',
    'subNose_M_Loc', 'subNose_L_Loc',
    'subCheek_M_Loc', 'subCheek_L_LocA', 'subCheek_L_LocB', 'subCheek_L_LocC', 'subCheek_L_LocD', 'subCheek_L_LocE',
    'subMouth_M_LocA', 'subMouth_M_LocB', 'subMouth_L_LocA', 'subMouth_L_LocB', 'subMouth_L_LocC', 'subMouth_L_LocD', 'subMouth_L_LocE']

    pos = [(0, 1.5, 2.4), (0.5, 1.6, 2.32), (1.2, 1.665, 1.997), (1.773, 1.398, 1.436), (1.841, 0.798, 0.913), (1.596, 0.287, 1.365), (1.051, 0.263, 1.814), (0.501, 0.466, 1.923),
    (0.479, 0.864, 1.63), (0.66, 1.003, 1.761), (1.041, 1.08, 1.775), (1.342, 1.02, 1.58), (1.439, 0.817, 1.257), (1.326, 0.778, 1.562), (1.008, 0.734, 1.75), (0.67, 0.797, 1.727),
    (0, -0.089, 2.984), (0.509, -0.094, 2.515),
    (0, -2.377, 2.369), (0.594, 0.156, 2.012), (1.106, -0.38, 1.876), (1.258, -0.992, 1.633), (1.173, -1.732, 1.52), (1.377, -0.151, 1.677),
    (0, -0.795, 2.655), (0, -1.354, 2.523), (0.405, -0.789, 2.467), (0.697, -0.948, 2.082), (0.796, -1.048, 1.885), (0.706, -1.188, 2.068), (0.398, -1.331, 2.39)]

    i = 0

    while (i < len(locs)):

        loc = mc.spaceLocator(n = locs[i])
        locShape = mc.listRelatives(loc, shapes = True)[0]
        mc.setAttr(locShape + '.localScale',0.05,0.05,0.05)
        locG = mc.group(n = locs[i] + '_zero')
        mc.xform(locG, ws=True, t=pos[i])
    
        i += 1

    # Mirror
    obj_L_List = mc.ls('sub*_L_*zero*',type='transform')
    for objL in obj_L_List:
        objR = mc.duplicate(objL,n = objL.replace('_L_','_R_'))
        mc.rename(objR[0]+'|'+objR[1], objR[1].replace('_L_', '_R_'))
        px = mc.getAttr(objL+'.tx')
        mc.setAttr(objR[0] + '.tx',px * -1)
    
    # Group / Parent Constraint / Lock Attr

    zeroList = mc.ls('sub*Loc*zero*', type = 'transform')
    zeroGRP = mc.group(zeroList, n = 'faceLocGRP')


    posZero = mc.getAttr(zeroGRP+'.rotatePivot')
    center = mc.curve(n='Center_Loc', d=1,p = [(0.5, 0.5, -0.5), (0.5, 0.5, 0.5), (0.5, -0.5, 0.5), 
						(0.5, -0.5, -0.5), (0.5, 0.5, -0.5), (-0.5, 0.5, -0.5), 
						(-0.5, -0.5, -0.5), (-0.5, -0.5, 0.5), (-0.5, 0.5, 0.5), 
						(0.5, 0.5, 0.5), (0.5, -0.5, 0.5), (-0.5, -0.5, 0.5), 
						(-0.5, -0.5, -0.5), (0.5, -0.5, -0.5),(0.5, 0.5, -0.5), 
						(-0.5, 0.5, -0.5), (-0.5, 0.5, 0.5), (0.5, 0.5, 0.5), (0.5, 0.5, -0.5)],
						k = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8])
    centerShape = mc.listRelatives(center, s = True)[0]
    mc.rename(centerShape,center + 'Shape')
    null = mc.group(center, n = center + '_zero')
    mc.setAttr(null + '.scale',4, 4.8, 2.5)
    mc.makeIdentity(null, apply = True, t = 0, r = 0, s = 1, n = 0)
    mc.move(0, 1.21, -0.2, center + '.rotatePivot', r =1)
    mc.move(0, 1.21, -0.2, center + '.scalePivot', r =1)
    mc.delete(mc.pointConstraint(zeroGRP, null))
    for zero in zeroList:
        mc.parentConstraint(center, zero,mo = True)
        mc.setAttr(zero + '.t', lock=True)
        mc.setAttr(zero + '.r', lock=True)
        mc.setAttr(zero + '.s', lock=True)
    
    # Set Color

    browShape = mc.ls('subBrow*Loc*Shape*', type = 'shape')
    for cs in browShape:
        mc.setAttr(cs + '.overrideEnabled', 1)
        mc.setAttr(cs + '.overrideColor', 18)
    
    eyeShape = mc.ls('subEye*Loc*Shape*', type = 'shape')
    for cs in eyeShape:
        mc.setAttr(cs + '.overrideEnabled', 1)
        mc.setAttr(cs + '.overrideColor', 14)
    
    eyeShape = mc.ls('subCheek*Loc*Shape*', type = 'shape')
    for cs in eyeShape:
        mc.setAttr(cs + '.overrideEnabled', 1)
        mc.setAttr(cs + '.overrideColor', 6)
    
    eyeShape = mc.ls('subMouth*Loc*Shape*', type = 'shape')
    for cs in eyeShape:
        mc.setAttr(cs + '.overrideEnabled', 1)
        mc.setAttr(cs + '.overrideColor', 13)
    
    noseShape = mc.ls('subNose*Loc*Shape*', type = 'shape')
    for cs in noseShape:
        mc.setAttr(cs + '.overrideEnabled', 1)
        mc.setAttr(cs + '.overrideColor', 17)
    mc.parent(zeroGRP, null)
    mc.select(center)
    return null
# Select The Vertex To Loc
'''
areaVex = mc.ls(sl = True)
createPreLoc()

if len(areaVex) != 0 and mc.nodeType(areaVex[0]) == 'mesh':

    posX = []
    posY = []
    posZ = []
    for vex in areaVex:
        pos = mc.xform(vex, q = True, ws = True, t = True)
        posX.append(pos[0]) 
        posY.append(pos[1]) 
        posZ.append(pos[2])
    minX = min(posX)
    maxX = max(posX)
    
    minY = min(posY)
    maxY = max(posY)
    
    minZ = min(posZ)
    maxZ = max(posZ)

    lengthX = maxX - minX
    lengthY = maxY - minY
    lengthZ = maxZ - minZ

    scaleX = lengthX / 4
    scaleY = lengthY / 4.982
    scaleZ = lengthZ / 2

    cenX = (minX + maxX) / 2
    cenY = (minY + maxY) / 2
    cenZ = (minZ + maxZ) / 2

    # Match The Locators

    mc.xform('Center_Loc_zero', ws = True, t = (cenX, cenY, cenZ))
    mc.scale(scaleX, scaleY, scaleZ, 'Center_Loc_zero', r = True)
    print '# Create Successfully! #'
else:
    print '# The Pre-locators On The Original Position! #'
    
    
# Reset The locators

const = mc.ls('*Loc*_zero_parentConstraint1*')
if len(const) != 0:
    mc.delete(mc.ls('*Loc*_zero_parentConstraint1*'))
else:
    pass
locs = mc.ls('*_L_Loc*zero*', type = 'transform')

k = 0
while (k < len(locs)):
    kid = mc.listRelatives(locs[k],children = True)
    pos = mc.xform(kid[0], q = True, ws = True, t = True)
    mc.setAttr(locs[k] + '.t', lock=False)
    mc.setAttr(locs[k] + '.r', lock=False)
    mc.setAttr(locs[k] + '.s', lock=False)
    mc.xform(locs[k], ws = True, t =( pos[0], pos[1], pos[2]))
    mc.setAttr(kid[0]+'.t',0,0,0)
    k += 1
'''