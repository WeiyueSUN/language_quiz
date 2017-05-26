# language_quiz

This is a SRT project in Tsinghua University, supervised by Prof. M. Zhang



***router table***

### /

- 方法:：get



### /info

- 方法：get



### /begin

- 方法：post
- 格式：form
- 参数：
  - sex: 'f'/'m'
  - age:0.5/1/1.5/…...
  - edu1~edu7:'0'/'1'



### /wordtest

- 方法：post
- 格式：form
- 参数：
  - childID：整数
  - questionID：题号 整数
  - answer：选择的单词（英文字母形式）