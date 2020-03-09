import os,sys,random
'''
2019.03 模拟实现modbus通信
寄存器类、设备类（主从设备）、modbus协议消息类

'''
class register(object):
    def __init__(self,name,param,state,addr):
        self.__name = name
        self.__param = param
        self.__state = state
        self.__addr =addr

    def readname(self):
        return self.__name

    def readparam(self):
        return self.__param

    def readstate(self):
        return self.__state
    def readaddr(self):
        return self.__addr

    def alterstate(self,state):
       self.__state = state

    def alterparam(self,param):
        if(self.__state == 'on'):
            self.__param = param 
            return True
        else:
            print('ERROR---寄存器状态为off,不能修改！') 
            return False  

class device(object):
    def __init__(self,attr,address):
        self.attr=attr
        self.address = address
        self.registers = []#寄存器列表
        if(attr=='slave'):
            r1 = register('speed','AA22','off','0x0010')#从设备 ：创造一个速度寄存器
            self.registers.append(r1)
            
    def send(self,message):
        message.print()
            
    def response(self,message):
        # if(attr=='slave'):
        needonflag=False
        for r in self.registers:#查找寄存器
            if r.readaddr() == message.register_addr:
                
                if message.operate =='01':#读取r的状态
                    if(r.readstate()=='on'):
                        message.data='FFFF'
                    else:##off响应修改状态
                        message.data = '0000'
                        needonflag = True

                elif message.operate =='03':#读取数值
                    data= r.readparam()
                    tmp =int(str(data),16)
                    # print(tmp)
                    message.data = str(tmp)

                elif message.operate == '06':#修改数值
                    if r.alterparam(message.data) == False:#修改失败   
                        return None 
                    tmp =int(message.data,16)
                    # print(tmp)
                    message.data = str(tmp)
                else:
                    pass
                # print(message.data)
               
                response_message = Modbus_message(message.receiver,message.sender,message.register_addr,message.operate,message.data)
                response_message.print()
                if needonflag:
                    r.alterstate('on')
                    print('寄存器改变状态，打开-----')

                return  None
        print('ERROR--没有此寄存器!-------')   


class Modbus_message(object):
    '''Modbus protocol'''
    'RTU方式 字符为十六进制'
    def __init__(self,sender,receiver,register_addr,operate,data):
        self.sender = sender
        self.receiver = receiver
        self.register_addr=register_addr
        self.operate = operate
        # 
        self.data =data
        if data != '':
            # print(data)
           
            sdata = str(hex(int(data)))[2:]
            self.data = '0'*(4-len(sdata))+sdata
            # print(self.data)

        if self.sender.attr=='master':
            self.attr='send'
        else:
            self.attr='responce'

 
    def modbus_part1(self): #地址
        if(self.attr=='send'):
            device_addr =self.receiver.address[2:]
        else:
            device_addr = self.sender.address[2:]
        # print(self.attr)
        if len(device_addr)<= 2:
            part1 = '0'*(2-len(device_addr))+device_addr
        else:
            part1 =device_addr[0:2]
        # print(part1)
        return part1
    
    def modbus_part2(self):#功能码
        part2=self.operate
        return part2

    def modbus_part3(self):#数据
        if self.attr =='send':##主设备报文
            if self.operate=='01' or self.operate=='03':
                part3 = self.register_addr[2:]+'0001'
            else:
              
                part3 =self.register_addr[2:]+self.data
        else:#从设备报文
            if self.operate=='01' or self.operate=='03':
                part3 = '0002'+(4-len(self.data))*'0'+self.data    
            else:
                part3 = self.register_addr[2:]+self.data
            #  part3 = '0'*(4-len(self.data))+self.data
        return part3


    def modbus_part4(self):#CRC
        prepart=self.modbus_part1()+self.modbus_part2()+self.modbus_part3()
        # print(self.modbus_part3())
        

        data = bytearray.fromhex(prepart)
        crc = 0xFFFF
        for pos in data:
            crc ^= pos
            for i in range(8):
                if ((crc & 1) != 0):#
                    crc >>= 1
                    crc ^= 0xA001
                else:
                    crc >>= 1

        crcresult= hex(((crc & 0xff) << 8) + (crc >> 8))
        # print(crcresult)
        crcresult = crcresult[2:]
        return crcresult

    def print(self):

        print(self.modbus_part1()+self.modbus_part2()+self.modbus_part3()+self.modbus_part4())



if __name__ == "__main__":

    '''  
    说明：当寄存器状态为off时，返回数值为0000,状态为on时返回FFFF 
    报文格式为16进制字符

    查询状态格式：[地址][01][第一个R的高地址][第一个R低地址][数量高字节][数量低字节][CRC]  
                 [地址][01][字节数量]                     [数据高字节][数据低字节][CRC]

    查询数值格式：[地址][03][第一个R的高地址][第一个R低地址][数量高字节][数量低字节][CRC]
    响应  格式为：[地址][03][字节数量]                     [数据高字节][数据低字节][CRC]

    修改数值格式：[地址][06][第一个R地址高8位] [低8位]      [数据高8位][低8位]     [CRC] 
    响应  格式为：[地址][06][第一个R地址高8位] [低8位]      [数据高8位][低8位]     [CRC] 

    '''

    #创建一个主设备一个从设备,从设备带有一个speed寄存器
    master =device('master','0x00')#地址0x00
    slave1 =device('slave','0x01')#地址0x01
    register_addr = '0x0010'
    print('初始化主、从设备完成---操作寄存器地址'+register_addr)

    ###读取固定寄存器'speed'状态
    message1 = Modbus_message(master,slave1,register_addr,'01','')
    print('主设备master访问slave1的寄存器获取状态---')
    master.send(message1)
    print('从设备slave1响应---')
    slave1.response(message1)
    ###读取固定寄存器'speed'的值
    message2 = Modbus_message(master,slave1,register_addr,'03','')
    print('主设备master查询slave1的寄存器数值---')
    slave1.send(message2)
    print('从设备slave1响应---')
    slave1.response(message2)
     ###修改固定寄存器'speed'的值为500(输入为十进制)
    message3 = Modbus_message(master,slave1,register_addr,'06',data='500')
    print('主设备master修改slave1的寄存器数值---')
    slave1.send(message3)
    print('从设备slave1响应---')
    slave1.response(message3)
   




    