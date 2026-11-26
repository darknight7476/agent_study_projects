# 问题、错误和解决方案

问题1

现象：在测试并发Task.Group和as_completed时，整体速度比gather慢几秒

原因：使用同步循环去获取result过程中存在并发串行化问题，即在循环中获取结果

