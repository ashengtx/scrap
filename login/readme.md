# now

现在可以通过半手动的方式拿到cookie

有两种方式可以爬

一，通过selenium点击获取html
二，拿到cookie后用requests获取

第二种方法分析起来比较难，也怕被封ip，先试试第一种

## 通过selenium点击获取html

遇到问题：browser.page_source拿不到最新的窗口，还停留在原来的窗口。

解决方案，切换到最新窗口试试。
https://blog.csdn.net/gz_testing/article/details/71251901

