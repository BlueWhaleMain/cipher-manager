# :bookmark: CipherManagerGUI 2.1.1

## :tada: 主要变化

* :recycle: 支持输入和设置二进制格式、多行与非ASCII字符的密码
* :bento: 添加了应用程序图标
* 支持查看版本号与在线检查更新
* 支持文件迭代加密

## :children_crossing: 界面与体验优化

* 现在会创建热交换文件用于缓存未保存的更改
* 增加搜索功能，支持简单的文本包含查找
* :recycle: 重新设计并实现了基本行列操作
* 增加了生成RSA私钥的简便方式
* :lipstick: :art: 优化交互与显示、增加图标与快捷键
  * 只有在应用完全失去焦点后才会尝试锁定工作区
  * 进度条优化并支持显示更详细的内容

## :sparkles: 功能变化

* 调整应用崩溃机制，避免闪退
* 支持更多证书后缀

## :bug: 问题修复

* 第一次输入不匹配时，可能无法完成输入 803cb7e8 c04dec1b
* :recycle: 重新梳理界面处理逻辑与异常处理，解决应用在某些条件下闪退的问题
* 解密文件流程缺少CRC校验 803cb7e8
* 导致继发性异常的异常处理 09c2fd5d 803cb7e8
* 极短任务可能使进度条可能进入异常状态 803cb7e8
* 进度条可能会渲染负数时间 803cb7e8
* 多次校验与导入密钥文件，耗时操作未显示进度条 803cb7e8
* 启动屏幕无响应问题 803cb7e8
* 取消加载证书后仍报错 803cb7e8
* 无法区分“忽略自动锁定”与“忽略编辑” 803cb7e8
* 左上角的单元格状态不正确 803cb7e8
* 多个后缀名无法选择到文件 803cb7e8
* 无限进度条对话框无响应问题 803cb7e8
* 修复空单元格导致非对称加密失败的问题 803cb7e8

## :zap: 性能提升

* 使用并发提高了前文不敏感算法（例如PKCS1）的加解密性能
* 提高了验证与导入密钥的速度

## 其他

* :fire: 暂时隐藏不在计划内的功能
* :heavy_plus_sign: Python-Markdown 3.8
* :heavy_plus_sign: PyMdown Extensions 10.14.3
* :globe_with_meridians: 提高i18n内容覆盖面
* :fire: 移除不被支持的keystore格式 803cb7e8

**Full Changelog**: https://github.com/BlueWhaleMain/cipher-manager/compare/CipherManagerGUI-2.0.0.0-preivew...CipherManagerGUI-2.1.1

---

# :bookmark: CipherManagerGUI 2.0.0.0 Preview

## :tada: 2.0

*  更安全的默认加密选项
*  迭代加密
*  无限表格
*  文件加密
* :recycle: Python 3.13 | PyQt6

## :fire: 移除的功能

* 不再维护已过时的控制台版本
* 不再支持1.0格式的PKL与JSON文件

## 其他

* :zap: 加快启动响应速度、部分耗时操作将渲染进度条
* :children_crossing: 优化界面交互与异常处理流程
* :globe_with_meridians: 支持加载qt翻译文件以本地化弹窗按钮文本等

**Full Changelog**: https://github.com/BlueWhaleMain/cipher-manager/compare/CipherManagerGUI-1.0.2.1...CipherManagerGUI-2.0.0.0-preivew

---

# :bookmark: CipherManagerGUI-1.0.2.1

## :ambulance: 紧急修复

1. 异常信息过长将导致卡顿或崩溃
2. 修改单元格不起作用，导致文件无法修改

**Full Changelog**: https://github.com/BlueWhaleMain/cipher-manager/compare/CipherManagerGUI-1.0.2.0...CipherManagerGUI-1.0.2.1

---

# CipherManagerGUI-1.0.2.0

## 新增

1. 视图功能：总在最前、便签模式和自动锁定
2. 关于
3. “重命名/移动“与“另存为”功能
4. 基本类型转换工具
5. 新建界面支持根据当前区域选择字符编码

## 优化

1. 随机密码生成功能
2. 异常处理
3. 编辑、删除
4. 菜单、右键菜单
5. 界面与交互
6. 文件选取逻辑
7. 加密测试

## 修复

1. 删除行越界的问题
2. 公私钥文件处理的问题

## 兼容性

1. 换行符兼容
