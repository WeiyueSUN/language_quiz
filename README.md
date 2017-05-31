# language_quiz

This is a SRT project in Tsinghua University, supervised by Prof. M. Zhang



***router table***

### /

- 方法:：get
- 返回：首页'index.html' 


### /info

- 方法：get
- 返回：基本信息选择页面'info.html' 


### /begin

- 方法：post
- 格式：form
- 参数：
  - sex: 'f'/'m'
  - age:0.5/1/1.5/…...
  - edu1~edu7:'0'/'1'
- 返回：单词测试页面，参数childID，questionID，correct，word0~word3, isLastQuestion=0/1
  



### /wordtest

- 方法：post
- 格式：form
- 参数：
  - childID：整数
  - questionID：题号 整数
  - answer：选择的单词（英文字母形式）
 - 返回：单词测试页面，参数childID，questionID，correct，word0~word3, isLastQuestion=0/1

### /wordtestresult

- 方法：post
- 格式：form
- 参数：
  - childID：整数
  - questionID：题号 整数
  - answer：选择的单词（英文字母形式）
 - 返回：单词测试结果页面，参数childID，pred_age，correct

### /survey

- 方法：post
- 格式：form
- 参数：
  - childID：整数
  - A11 A12 A13 分别为每题的答案
  - A21 A22 A23
  - A31 A32 A33
  - A4 A5 A6 A7
  
### /raventest

- 方法：post
- 格式：form
- 参数：
  - childID：整数
  - questionID：题号 整数
  - answer：选择的答案（能直接对应一个选项的图片，需事先约定好图片的编号，例如25.jpg为第2题第5个选项的图片，则questionID为2，answer为5）
- 返回：瑞文测试页面，参数childID，questionID，isLastQuestion=0/1

- 方法：get
- 返回：瑞文测试页面，参数childID，questionID，isLastQuestion=0/1


### /memory

- 方法：post
- 格式：form
- 参数：
  - childID：整数
  - lenth：题号 整数
  - answer：输入的数字串，限制不超过15
- 返回：工作记忆测试页面, 参数childID，lenth(注：这里事先约定好音频命名规则，如5.MP3表示5个数字音频，则lenth=5)
  或者返回：结束页面
- 方法：get
- 返回：工作记忆测试页面, 参数childID，lenth
