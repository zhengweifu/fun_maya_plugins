import maya.OpenMaya as om

class Common(object):
    @classmethod
    def MMatrixToArray(self, mMatrix):
        result = []
        for i in range(4):
            for j in range(4):
                result.append(om.MScriptUtil.getDoubleArrayItem(mMatrix[i], j))
        return result
    @classmethod
    def getRelativePath(self, url, sAbs):
        url_n = url.replace("\\", "/")
        url_n_l = url_n.split("/")
    
        sAbs_n = sAbs.replace("\\", "/")
        sAbs_n_l = sAbs_n.split("/")
    
        len_url = len(url_n_l)
        len_sAbs = len(sAbs_n_l)

        ref = None
    
        for i in range(len_url-1):
            if(i<len_sAbs):
                if(url_n_l[i] != sAbs_n_l[i]) :
                    ref = i
                    break
                else :
                    if(i == len_url -2):
                        ref = i+1

    
        if(ref == None and ref < 0):
            return sAbs
    
        split = []
        for i in range(ref, len_url-1):
            split.append("..")
    
        for i in range(ref,len_sAbs):
            split.append(sAbs_n_l[i])

        return "/".join(split)