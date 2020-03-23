# ICS
a course about information security protection of the industrial control system
<!-- TOC -->

- [ICS](#ics)
  - [Update Info](#update-info)
  - [Details](#details)
    - [modbus protocol](#modbus-protocol)
    - [PLC](#plc)
    - [PLC vulnerability analysis](#plc-vulnerability-analysis)

<!-- /TOC -->
## Update Info
- 2019.03.09 python模拟modbus协议通信过程，参考ethernet protocol
- 2019.03.23 更新PLC和PLC漏洞分析
## Details
### modbus protocol
仿真设计ModBus通信数据（具体报文格式参考第二次课PPT第32页）
- （1）主设备访问从设备固定寄存器的状态 （该设备返回报文给主设备）
- （2）主设备读取该从设备该寄存器的值（该设备返回报文给主设备）
- （3）主设备修改该从设备该寄存器的值（该设备返回报文给主设备）
参考第二节PPT
### PLC

![enter description here](http://img.elfship.cn/img/1584947172237.png)
说明：
1. PLC询问执行器速度
2. PLC给的数据是u，u是电压值，执行器的驱动器根据u来调整速度（u可以认为是走到modbus线，也可以认为是走的电缆），整个方框里是PLC
3. r不是发给执行器的
4.如果u走modbus线那么PLC每次都要发u，如果走普通电缆，则认为PLC设定目标速度后（这一步应该没有modbus通信),设备就开始不断报告（设备收到u再转换为速度）
参考matlab语言：（注意这里写错了，应该是4000）
![matlab](http://img.elfship.cn/img/1584947213374.png)
参考第三节PPT
### PLC vulnerability analysis
分析垃圾邮件发送者对PLC的威胁和PLC的漏洞
参考第六节PPT