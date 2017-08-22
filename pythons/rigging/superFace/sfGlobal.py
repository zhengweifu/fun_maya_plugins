from os.path import dirname, join, abspath

class sfGlobal:
    #GLOBAL_PATH = '//Server-03/d007g/test/facialRigTD/superFace/'
    GLOBAL_PATH = abspath(dirname(__file__)).replace('\\','/') + '/'
    #GLOBAL_PATH = 'e:/superFace/'
    
    ROOT_CTRL_LIB_PATH = GLOBAL_PATH + 'rootCtrlLib'
    GOAL_CTRL_LIB_PATH = GLOBAL_PATH + 'goalCtrlLib'
    SUB_CTRL_LIB_PATH = GLOBAL_PATH + 'subCtrlLib'
    SUB_POSE_LIB_PATH = GLOBAL_PATH + 'subPoseLib'
    ICONS_PATH = GLOBAL_PATH +'Icons'
    
    SCRIPTJOB_CMD = 'scriptjob'
    SCRIPTJOB_FILE = GLOBAL_PATH +'scriptjob.mel'
    
    LEFT_KEY = '_L_'
    RIGHT_KEY = '_R_'

    ROOT_MARK = 'SuperFaceMaker'
    
    '''
    faceCtrlGrp
        rootCtrlGrp
			subCtrlOrienter
        jointCtrlGrp
            eyeConstructionGrp
            	eyeLocGrp
            chinConstructionGrp
            	chinLocGrp
            tongueConstructionGrp
            	tongueLocGrp
            headSkinJntGrp
        goalCtrlGrp
            goalModelGrp
                hide
        subCtrlGrp
            subLocGrp
            subCtrlGrp
            subCtrlListGrp
    '''
    ROOT_GRP = 'faceCtrlGrp'
    
    ROOT_CTRL_GRP = 'rootCtrlGrp'
    
    SUB_CTRL_GRP = 'subCtrlGrp'
    SUB_LOC_GRP = 'subLocGrp'
    CENTER_LOC = 'Center_Loc'
    FACE_LOC_GRP = 'faceLocGRP'
    
    SUB_CTRL_LIST_GRP = 'subCtrlListGrp'
    
    GOAL_CTRL_GRP = 'goalCtrlGrp'
    GOAL_MODEL_GRP = 'goalModelGrp'
    GOAL_MODEL_HIDE_GRP = 'goalModelHideGrp'
    
    JOINT_CTRL_GRP = 'jointCtrlGrp'
    
    EYE_CTRL_GRP = 'eyeConstructionGrp'
    EYE_LOC_GRP = 'eyeLocGrp'
    EYE_RIG_GRP = 'eyeRigGrp'
    
    TONGUE_CTRL_GRP = 'tongueConstructionGrp'
    TONGUE_LOC_GRP = 'tongueLocGrp'
    TONGUE_RIG_GRP = 'tongueRigGrp'
    
    
    CHIN_CTRL_GRP = 'chinConstructionGrp'
    CHIN_LOC_GRP = 'chinLocGrp'
    CHIN_RIG_GRP = 'chinRigGrp'
    
    HEAD_SKIN_JNT_GRP = 'headSkinJntGrp'
    
    DO_NOT_TOUCH = 'DoNotTouch'
    
    ADJUSTER = 'Adjuster'
    
    BASE_MODEL_NAME_POSTFIX = '_face_baseBlendshape_model'
    
    FACE_CTRL_PANEL = 'face_global_ctrl'

    FACE_ROOT_LOC = 'faceRoot'

    SUB_CTRL_ORIENTER = 'subCtrlOrienter'

    MAIN_UI = 'superFaceUI'

g = sfGlobal()