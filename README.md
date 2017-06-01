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
 
# 当上个url返回的isLastQuestion==1时，接下来请求这个url
### /wordtestresult

- 方法：post
- 格式：form
- 参数：同上
  - childID：
  - questionID：
  - answer：
 - 返回：单词测试结果页面，参数childID，pred_age

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

# 当上个url返回的isLastQuestion==1时，接下来请求这个url
### /raventestresult

- 方法：post
- 格式：form
- 参数：同上
  - childID：
  - questionID：
  - answer：
 - 返回：瑞文测试之后的页面，参数childID


### /memory

- 方法：post
- 格式：form
- 参数：
  - childID：整数
  - length：题号 整数，为数字串长度
  - answer：输入的数字串，限制不超过15
- 返回：工作记忆测试页面, 参数childID，length(注：这里事先约定好音频命名规则，如5.MP3表示5个数字音频，则length=5)，isLastQuestion=0/1
  或者返回：结束页面
- 方法：get
- 返回：工作记忆测试页面, 参数childID，length, isLastQuestion=0/1

# 当上个url返回的isLastQuestion==1时，接下来请求这个url
### /memorytestresult
- 方法：post
- 格式：form
- 参数：同上
  - childID：
  - length：
  - answer：
 - 返回：记忆测试之后的页面，参数childID

