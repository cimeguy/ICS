import os,sys,random
import matplotlib.pyplot as plt
import threading,time

'''
2019.03 模拟实现modbus通信
寄存器类、设备类（主从设备）、modbus协议消息类

'''
register_addr = '0x0010'
deltat = 0.1
starttime=time.time()
def octtohex(data):
    #实现带或者不带0o的十进制转化为十六进制，不带0x
    if '0o' in data:
        sdata = str(hex(int(data[2:])))[2:]
    else:
        sdata = str(hex(int(data)))[2:]
    return sdata

def hextooct(data):
     #实现带或者不带0x的十进制转化为十六进制，不带0o
    if '0x' in data:
        sdata = int(data[2:],16)
    else:
        sdata = int(data[:],16)
    return sdata
    

class register(object):
    def __init__(self,name,param,state,addr):
        self.__name = name
        self.__param = param#十六进制
        self.__state = state
        self.__addr =addr
        self.__realspeed=float(int(hextooct(param)))#十进制,这一步是为了防止丢失精度  float
        # self.octparam = hextooct(self.__param)
    def readrealspeed(self):
        return self.__realspeed

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

    def alterparam(self,param):#param是十六进制
        if(self.__state == 'on'):
            self.__param = '0'*(4-len(param))+ param
            return True
        else:
            print('ERROR---寄存器状态为off,不能修改！') 
            return False  

    def alterrealspeed(self,real):#param是十六进制
        if(self.__state == 'on'):
            self.__realspeed =float(real)
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
            r1 = register('speed','01f4','off','0x0010')#从设备 ：创造一个速度寄存器，初始值是500
            self.registers.append(r1)
            self.u=0
            
    def send(self,message):
        return message.print()
            
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

                elif message.operate == '06':#修改数值  message.data是十六进制
                    #PID过程
                    yi_1=r.readrealspeed()#十六进制转换
                  
                    speed =deltat/(10+deltat)*self.u+10/(10+deltat)*yi_1#执行器接收u产生速度
                  
                    hexspeed = octtohex(str(int(speed)))
                    hexspeed = '0'*(4-len(hexspeed))+hexspeed
                    r.alterparam(hexspeed)
                    r.alterrealspeed(speed)
                    message.data= str(speed)#构建message时数据是十进制字符
                    # print(message.data)
                    # print(message.data)
                    time.sleep(0.1)
                    response_message = Modbus_message(message.receiver,message.sender,message.register_addr,message.operate,message.data)
                    return response_message.print()
                    
                else:
                    pass
                # print(message.data)
               
                response_message = Modbus_message(message.receiver,message.sender,message.register_addr,message.operate,message.data)

                if needonflag:
                    r.alterstate('on')
                    print('寄存器改变状态，打开-----')
                
            return response_message.print()
                # return  None
        print('ERROR--没有此寄存器!-------')   
         


class Modbus_message(object):
    '''Modbus protocol'''
    'RTU方式 字符为十六进制'
    def __init__(self,sender,receiver,register_addr,operate,data):#data为十进制字符串
        self.sender = sender
        self.receiver = receiver
        self.register_addr=register_addr
        self.operate = operate
        self.realdata=data#十进制
        # 
        self.data =data#十六进制
        if data != '':
            # print(data)
            if '.' in data:

               sdata = str(hex(int(float(data))))[2:]
            else:
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
        crcresult = '0'*(4-len(crcresult))+crcresult
        return crcresult

    def print(self):
        if self.attr=='send':
            if self.operate=='01':
                state = '主设备查询状态'
            elif self.operate =='03':
                state = '主设备读取数值'
            else:
                state = '主设备修改数值'
        else:
            if self.operate=='01':
                state = '从设备响应状态'
            elif self.operate =='03':
                state = '从设备响应读取'
            else:
                state = '从设备响应修改'

        nowtime=round((time.time()-starttime),1)
        messagedata=self.modbus_part1()+self.modbus_part2()+self.modbus_part3()+self.modbus_part4()
        print(str(nowtime)+'s:  ['+state+']   '+messagedata)
        with open('输出报文.txt', 'a') as f:#输出到文件
            f.write('\n'+str(nowtime)+'s:  ['+state+']  '+messagedata)
        return self.realdata


if __name__ == "__main__":
    #将所有报文输出到文件
    with open('输出报文.txt', 'w') as f:
        f.write('通信报文,所有数值均为十六进制\n')

     #创建一个主设备PLC，一个从设备运动执行器,从设备带有一个speed寄存器
    PLC =device('master','0x00')#地址0x00  PLC
    MotionActuator =device('slave','0x01')#地址0x01  运动执行器
    register_addr = '0x0010'#寄存器地址
    print('初始化主、从设备完成---操作速度寄存器地址'+register_addr)

    ###读取固定寄存器'speed'状态
    message1 = Modbus_message(PLC,MotionActuator,register_addr,'01','')
    print('PLC访问MotionActuator的寄存器获取状态---')
    PLC.send(message1)
    print('从设备MotionActuator响应---')
    MotionActuator.response(message1)

    ###读取固定寄存器'speed'的值
    message2 = Modbus_message(PLC,MotionActuator,register_addr,'03','')
    print('主设备PLC查询MotionActuator的寄存器数值---')
    PLC.send(message2)
    print('从设备MotionActuator响应---')
    firstdata=MotionActuator.response(message2)#获得最开始的速度
     ###修改固定寄存器'speed'的值为1000(输入为十进制),这里传输的u值走普通电缆,目标值不放入报文中
    message3 = Modbus_message(PLC,MotionActuator,register_addr,'06',data='')
    print('主设备PLC修改MotionActuator的寄存器数值---')
    PLC.send(message3)
    '''
        更改，之前直接通过modbus传输目标值，这次改为直接通过普通电线传输u值，然后执行器再处理数据，并反馈速度数据，PLC计算u值
        
        由于在计算中速度的值达到小数点后13位，如果选择单精度浮点数（4字节）来表示速度报文信息，也会造成精度损失（只能到小数点后6位）
        从而导致计算出现误差，选择双精度浮点数（8字节16个十六进制数）的话报文信息太过冗杂，所以最后还是选择使用整型数据
        （2个字节）代表报文中的速度信息，但为了计算精度，同时还会传输一个真实的速度浮点数用于PLC和执行器各自的计算
    '''

    T = 4000#每0.1s采样 400s采样4000次
    deltat = 0.1#每0.1s采样 
    rPLC= 1000.#目标值1000
    y=[0]*(T+1)#从index==1开始 所以list大小为T+1
    
    y[1]=float(firstdata)#第一次的数据  500
    kp =1.7
    print('从设备MotionActuator每0.1s报告---')
    for i in range(2,T+1):   #控制过程
        MotionActuator.u = (rPLC-y[i-1])*kp#u值直接传输
        responsedata=MotionActuator.response(message3)#执行器作出计算和响应  并返回十进制的数值
        y[i]=float(responsedata)#PLC从中获取真实速度，如果直接从十六进制报文获取速度将会导致精度丢失
                                #精度丢失的情况下数据将极不准确
        #储存速度值    
        
    #画图
    x = [a/10 for a in range(1,T+1)]
    y = y[1:]
    plt.plot(x,y)
    plt.show()
   




    
