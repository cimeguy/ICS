# ICS
a course about information security protection of the industrial control system
<!-- TOC -->

- [ICS](#ics)
  - [Update Info](#update-info)
  - [Details](#details)
    - [modbus protocol](#modbus-protocol)

<!-- /TOC -->
## Update Info
- 2019.03.09 python模拟modbus协议通信过程，参考ethernet protocol

## Details
### modbus protocol
仿真设计ModBus通信数据（具体报文格式参考第二次课PPT第32页）
- （1）主设备访问从设备固定寄存器的状态 （该设备返回报文给主设备）
- （2）主设备读取该从设备该寄存器的值（该设备返回报文给主设备）
- （3）主设备修改该从设备该寄存器的值（该设备返回报文给主设备）

   