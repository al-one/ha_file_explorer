import logging, time, importlib, base64, json, string, sys, requests, urllib, aiohttp, subprocess, tempfile
from aiohttp import web
from homeassistant.components.http import HomeAssistantView

from .const import DOMAIN, VERSION, URL, ROOT_PATH

class HAView(HomeAssistantView):

    url = URL
    name = DOMAIN
    requires_auth = True
    
    ''' 查询接口 '''
    async def get(self, request):
        hass = request.app["hass"]
        fileExplorer = hass.data[DOMAIN]
        res = await request.json()
        _type = res.get('type', '')
        _path = hass.config.path('./' + res.get('path', ''))
        if _type == 'get':
            # 获取目录和文件
            _json = fileExplorer.getDirectory(_path)
            return self.json(_json)
        elif _type == 'content':
            # 获取文件内容
            try:
                _text = fileExplorer.getContent(_path)
                return self.json({ 'code': 0, 'data': _text})
            except Exception as ex:
                return self.json({'code': 1, 'msg': '出现异常'})
        elif _type == 'upload-list':
            try:
                res = await fileExplorer.q.get_list(None)
                # print('测试一下：', res)
                return self.json({ 'code': 0, 'msg': '获取备份列表', 'data': res})
            except Exception as e:
                print(e)
                return self.json({ 'code': 1, 'msg': '备份列表获取异常，请检查是否正确配置七牛云密钥'})

    ''' 推送接口 '''
    async def put(self, request):
        hass = request.app["hass"]
        fileExplorer = hass.data[DOMAIN]
        try:
            reader = await request.multipart()
            # print(reader)
            # 读取路径
            res_path = await reader.next()
            res_path_value = await res_path.text()
            # print(res_path_value)
            # 读取名称
            res_file = await reader.next()
            res_file_value = await res_file.text()
            # print(res_file_value)
            # 保存文件
            file = await reader.next()
            # 生成文件
            _path = hass.config.path('./' + res_path_value)
            if os.path.isdir(_path) == False:
                fileExplorer.mkdir(_path)
            filename =  _path + '/' + res_file_value
            size = 0
            with open(filename, 'wb') as f:
                while True:
                    chunk = await file.read_chunk()  # 默认是8192个字节。
                    if not chunk:
                        break
                    size += len(chunk)
                    f.write(chunk)
            return self.json({ 'code': 0, 'msg': '上传成功'})
        except Exception as e:
            print(e)

    ''' 删除接口 '''
    async def delete(self, request):
        hass = request.app["hass"]
        fileExplorer = hass.data[DOMAIN]
        res = await request.json()
        _type = res.get('type', '')
        _path = hass.config.path('./' + res.get('path', ''))
        if _type == 'delete':
            # 这是过滤掉主文件，不让删除
            fileExplorer.delete(_path)
            return self.json({ 'code': 0, 'msg': '删除成功'})
        elif _type == 'delete-qiniu':
            await fileExplorer.q.delete(res.get('key'))
            return self.json({ 'code': 0, 'msg': '删除成功'})

    ''' 修改接口 '''
    async def post(self, request):
        res = await request.json()
        _type = res.get('type', '')
        _path = hass.config.path('./' + res.get('path', ''))
        _name = res.get('name', '')
        if _type == 'set':
            fileExplorer.setContent(_path, res['data'])
            return self.json({ 'code': 0, 'msg': '保存成功'})
        elif _type == 'new-file':
            fileExplorer.setContent(_path + '/' + _name, '')
            return self.json({ 'code': 0, 'msg': '新建成功'})
        elif _type == 'new-dir':
            fileExplorer.mkdir(_path + '/' + _name)
            return self.json({ 'code': 0, 'msg': '新建成功'})
        elif _type == 'upload':
            if fileExplorer.q is None:
                return self.json({ 'code': 1, 'msg': '请配置七牛云相关密钥信息'})
            
            if 'path' in res:
                zf = fileExplorer.zipdir(res['path'])
            elif 'list' in res:
                # 压缩多个文件
                zf = fileExplorer.zip(res['list'])
            
            try:
                await fileExplorer.q.upload(zf)
                # 上传成功，删除文件
                fileExplorer.delete(zf)
                return self.json({ 'code': 0, 'msg': '上传成功'})
            except Exception as ex:
                print(ex)
                return self.json({ 'code': 1, 'msg': '上传错误，一般是七牛云不能创建配置文件的权限问题'})
        elif _type == 'download':
            try:
                _url = res['url']
                print(_url)
                down_res = None
                async with aiohttp.request('GET', _url) as r:
                    down_res = await r.read()
            except Exception as e:
                return self.json({'code':1, 'msg': '下载文件出现异常：' + str(e)})
            # 如果有path，则代表是下载URL到指定目录
            if 'path' in res:
                backup_path = _path + '/' + os.path.basename(_url)
                with open(backup_path, "wb") as code:
                    code.write(down_res)
                return self.json({'code':0, 'msg': '下载成功'})
            else:
                # 获取临时文件目录
                _path = tempfile.gettempdir()
                backup_path = _path + '/ha_file_explorer_backup.zip'
                with open(backup_path, "wb") as code:
                    code.write(down_res)
                # 解压文件
                fileExplorer.unzip(backup_path, _path + '/ha_file_explorer_backup')
                # 删除下截的备份文件
                fileExplorer.delete(backup_path)
                # 返回文件夹里的数据
                return self.json({'code':0, 'data': fileExplorer.getAllFile(_path + '/ha_file_explorer_backup') , 'msg': '下载成功'})        
        elif _type == 'reset':
            # 替换指定文件
            fileExplorer.move(res['list'])
            await fileExplorer.notify("还原成功")
            return self.json({'code':0, 'msg': '还原成功'})
        elif _type == 'update':
            _domain = res['domain']
            _url = res['url']
            _path =  hass.config.path("custom_components").replace('\\','/')
            # https://github.com.cnpmjs.org/shaonianzhentan/$DOMAIN
            with open(_path + '/' + DOMAIN + '/update.sh', 'r', encoding='utf-8') as f:
                arr = _url.split('/')
                content = f.read().replace('$PATH', _path).replace('$DOMAIN', _domain).replace('$URL', _url).replace('$PROJECT', arr[len(arr)-1])
            # 获取临时文件目录
            tmp_path = tempfile.gettempdir()
            _sh =  tmp_path + '/' + _domain + '.sh'
            with open(_sh, 'w', encoding='utf-8') as f:
                f.write(content)
            # 如果是windows则直接运行
            _cmd = 'bash ' + _sh
            if os.name == 'nt':
                _cmd = _sh
            subprocess.Popen(_cmd, shell=True)
            return self.json({'code':0, 'msg': '正在异步拉取代码，请自行查看是否成功'})
        return self.json(res)