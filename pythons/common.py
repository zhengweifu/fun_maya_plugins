import maya.OpenMaya as om
import hashlib, uuid, time
import maya.cmds as cmds
class Common(object):
    @classmethod
    def MMatrixToArray(self, mMatrix):
        result = []
        for i in range(4):
            for j in range(4):
                result.append(om.MScriptUtil.getDoubleArrayItem(mMatrix[i], j))
        return result
    @classmethod
    def GetMDagPathFromName(self, name):
        if not cmds.objExists(name):
            print "No object called \" %s \""%name
            return None
        selected = om.MSelectionList()
        selected.add(name)
        
        dagPath = om.MDagPath()
        selected.getDagPath(0, dagPath)
        return dagPath
    @classmethod
    def List2ToList1(self, l):
        return [y for x in l for y in x]
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
    @classmethod
    def listMultiplyValue(self, l, v):
        return [x * v for x in l]
    @classmethod
    def fileSha1(self, url):
        with open(url, 'rb') as f:
            sha1obj = hashlib.sha1()
            sha1obj.update(f.read())
            hash = sha1obj.hexdigest()
            # print(hash)
            return hash
    @classmethod
    def sha1(self, content):
        sha1obj = hashlib.sha1()
        sha1obj.update(content)
        hash = sha1obj.hexdigest()
        # print(hash)
        return hash
    @classmethod
    def fileMD5(self, url):
        with open(url, 'rb') as f:
            md5obj = hashlib.md5()
            md5obj.update(f.read())
            hash = md5obj.hexdigest()
            # print(hash)
            return hash
    @classmethod
    def MD5(self, content):
        md5obj = hashlib.md5()
        md5obj.update(content)
        hash = md5obj.hexdigest()
        # print(hash)
        return hash

    @classmethod
    def MD532ToUUID(self, md5):
        if len(md5) == 32:
            return '-'.join([md5[:8], md5[8:12], md5[12:16], md5[16:20], md5[20:32]])
        else:
            return md5

    @classmethod
    def Uuid(self):
        str(uuid.uuid3(uuid.NAMESPACE_DNS, `time.time()`))

    @classmethod
    def StrToUnicode(self, strInput):
        if isinstance(strInput, unicode):
            return strInput

        codes = ['utf8', 'utf-8', 'gbk']
        
        for c in codes:
            try:
                return strInput.decode(c)
            except:
                pass

        return None