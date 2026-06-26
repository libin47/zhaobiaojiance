from DrissionPage import ChromiumOptions
# 请改为你电脑内Chrome可执行文件路径
# edge浏览器可访问 edge://version/，复制其可执行文件路径
# 其他浏览器类似
path = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
ChromiumOptions().set_browser_path(path).save()