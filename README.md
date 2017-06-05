# language_quiz

This is a SRT project in Tsinghua University, supervised by Prof. M. Zhang


新添了传输参数：时间time，一律秒为单位，保留两位小数
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
  - time: 从进入/info（或第一次点击一个选项）到提交的时间
- 返回：单词测试页面，参数childID，questionID，correct，word0~word3, isLastQuestion=0/1
  



### /wordtest

- 方法：post
- 格式：form
- 参数：
  - childID：整数
  - questionID：题号 整数
  - answer：选择的单词（英文字母形式）
  - time: 做这道题的用时(从page ready 到 submit)
 - 返回：单词测试页面，参数childID，questionID，correct，word0~word3, isLastQuestion=0/1
 
# 当上个url返回的isLastQuestion==1时，接下来请求这个url
### /wordtestresult

- 方法：post
- 格式：form
- 参数：同上
  - childID：
  - questionID：
  - answer：
  - time：
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
  - time: 从进入/survey（或第一次点击一个选项）到提交的时间
### /raventestbegin

- 方法：post
- 格式：form
- 参数： 
   - childID
- 返回：瑞文测试页面，参数childID，questionID，isLastQuestion=0/1
### /raventest

- 方法：post
- 格式：form
- 参数：
  - childID：整数
  - questionID：题号 整数
  - answer：选择的答案（能直接对应一个选项的图片，需事先约定好图片的编号，例如25.jpg为第2题第5个选项的图片，则questionID为2，answer为5）
  - time:
- 返回：瑞文测试页面，参数childID，questionID，isLastQuestion=0/1


# 当上个url返回的isLastQuestion==1时，接下来请求这个url
### /raventestresult

- 方法：post
- 格式：form
- 参数：同上
  - childID：
  - questionID：
  - answer：
  - time:
 - 返回：瑞文测试之后的页面，参数childID

## 记忆测试中，questionID为2k-1,2k的对应长度为k的字符串

### /memorytestbegin

- 方法：post
- 格式：form
- 参数：childID??
- 返回： 工作记忆测试页面，参数questionID

### /memorytest

- 方法：post
- 格式：form
- 参数：
  - childID：整数
  - questionID：题号 整数
  - answer：输入的数字串，限制不超过15
  - time:
- 返回：工作记忆测试页面, 参数childID，questionID
     或，结束页面


### /memorytestresult
目前不使用这个url

