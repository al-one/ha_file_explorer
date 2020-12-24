import datetime, shutil, json, re, zipfile, time, os, uuid, sys, tempfile

from os         import listdir, stat, remove
from os.path    import exists, isdir, isfile, join
class FileExplorer():
    def __init__(self, hass):
        self.hass = hass

    def getAllFile(self, dir):
        allcontent = listdir(dir)
        dirItem    = [] 

        for item in allcontent:
            hashInfo = {}
            filePath = join(dir,item)
            if exists(filePath) == False:
                continue
            # 过滤指定目录
            if item == '__pycache__':
                continue
            listInfo = stat(filePath)
            hashInfo['name'] = item
            hashInfo['url']  = filePath
            if isdir(filePath):
                hashInfo['child'] = self.getAllFile(filePath)
            dirItem.append(hashInfo)
        return dirItem

    def getDirectory(self, dir):
        allcontent = listdir(dir)
        dirItem    = [] 

        for item in allcontent:
            hashInfo = {}
            '''
            print(item)
            if item.startswith('.'):
                continue
            '''
            if exists(join(dir,item)) == False:
                continue
            listInfo = stat(join(dir,item))
            hashInfo['name'] = item
            hashInfo['url']  = item
            hashInfo['edit'] = datetime.datetime.fromtimestamp(int(listInfo.st_mtime)).strftime('%Y-%m-%d %H:%M:%S')
                        
            if isfile(join(dir,item)):
                hashInfo['type'] = 'file'
                hashInfo['size'] = int(listInfo.st_size)
            if isdir(join(dir,item)):
                hashInfo['type'] = 'dir'
                hashInfo['size'] = self.get_dir_size(join(dir,item))
            dirItem.append(hashInfo)

        dirItem.sort(key=lambda x: x['name'], reverse=True)
        return dirItem
    
    def getContent(self, _path):        
        fp = open(_path, 'r', encoding='UTF-8')
        content = fp.read()
        fp.close()
        return content

    def setContent(self, _path, _content):
        fp = open(_path, 'w+', encoding='UTF-8')
        fp.write(_content)
        fp.close()
        
    def delete(self, _path):
        if exists(_path):
            if isfile(_path):
                # 删除文件
                remove(_path)
            elif isdir(_path):
                # 删除目录
                shutil.rmtree(_path, ignore_errors=True)

    # 获取文件夹大小
    def get_dir_size(self, dir):
        size = 0
        for root, dirs, files in os.walk(dir):
            size += sum([os.path.getsize(os.path.join(root, name)) for name in files])
        return size

    # 创建文件夹
    def mkdir(self, path):
        folders = []        
        while not os.path.isdir(path):
            path, suffix = os.path.split(path)
            folders.append(suffix)
        for folder in folders[::-1]:
            path = os.path.join(path, folder)
            os.mkdir(path)
    
    # 替换文件
    def move(self, _list):
        tmp_path = tempfile.gettempdir() + '/ha_file_explorer_backup'
        try:
            for src in _list:
                # 将要还原的目录替换为空
                _dst = src.replace(tmp_path, self.hass.config.path("./"))
                # print(src)
                # print(_dst)
                # 创建目录
                lastIndex = _dst.replace('\\','/').rindex('/')
                _dir = _dst[0:lastIndex]
                if os.path.isdir(_dir) == False:
                    self.mkdir(_dir)
                    print(_dir)
                shutil.copy2(src, _dst)
        except Exception as ex:
            print(ex)        

    # 压缩单个项
    def zipdir(self, dirname):
        hass = self.hass
        local = tempfile.gettempdir()
        zipfilename = local + '/' + time.strftime('_%m_%d_%H%M%S',time.localtime(time.time())) + '+' + str(dirname.replace('\\','+').replace('/','+')) + ".zip"
        print(zipfilename)
        filelist = []
        dirname = hass.config.path('./' + dirname)
        if os.path.isfile(dirname):
            filelist.append(dirname)
        else :
            for root, dirs, files in os.walk(dirname):
                for name in files:
                    filelist.append(os.path.join(root, name))
        zf = zipfile.ZipFile(zipfilename, "w", zipfile.ZIP_DEFLATED)
        for tar in filelist:
            arcname = tar[len(dirname):]
            #print arcname
            zf.write(tar,arcname)
        zf.close()

        return zipfilename

    # 压缩
    def zip(self, _list, filter_dir=None):
        hass = self.hass
        root_path = hass.config.path('./')
        local = tempfile.gettempdir()
        zf = local + '/' + time.strftime('_%m_%d_%H%M%S',time.localtime(time.time())) + ".zip"
        with zipfile.ZipFile(zf, 'w', zipfile.ZIP_DEFLATED) as zip:
            for item in _list:
                try:
                    dirpath = hass.config.path('./' + item)
                    # 压缩目录
                    if isdir(dirpath):
                        for path,dirnames,filenames in os.walk(dirpath):
                            # 去掉目标跟路径，只对目标文件夹下边的文件及文件夹进行压缩
                            fpath = path.replace(root_path,'')                            
                            # 如果过滤的文件
                            if filter_dir is not None and len(list(filter(lambda x: x in fpath, filter_dir))) > 0:
                                continue
                            # print('压缩目录：' + fpath)
                            for filename in filenames:
                                zip.write(os.path.join(path,filename), os.path.join(fpath,filename))
                    else:
                        zip.write(dirpath, item)
                except Exception as ex:
                    print(ex)
                    pass                
        return zf

    # 解压
    def unzip(self, src_file, dest_dir):
        zf = zipfile.ZipFile(src_file)
        try:
           zf.extractall(path=dest_dir)
        except RuntimeError as e:
           print(e)
        zf.close()

    async def notify(self, message):
        await self.hass.services.async_call('persistent_notification', 'create', {"message": message, "title": "文件管理", "notification_id": "ha_file_explorer"})
