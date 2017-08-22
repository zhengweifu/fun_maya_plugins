import maya.cmds as cmds

def main(log=None):
    if not log:
        import logging
        log = logging.getLogger()

    edge5 = set()
    dagNode = cmds.ls(dag = True, l=True, lf=True, type = 'mesh')
    for dag in dagNode:
        cmds.select(dag)
        numFace = cmds.polyEvaluate(f = True)
        for f in range(0, numFace):
            allEdge = []
            cmds.select(cl = True)
            cmds.select(dag + '.f[' + str(f) + ']')
            edgeNum = cmds.polyInfo(fe = True)
            eSplit1 = edgeNum[0].split(':')
            eSplit2 = eSplit1[1].split(' ')
            for e in eSplit2:
                if(e != ''):
                    allEdge.append(e)
            if(len(allEdge) > 5):
                edge5.add('%s.f[%s]' %(dag, f))
                
    if edge5:
        log.warning("more than four edge:\n%s" % (' '.join(edge5)) )