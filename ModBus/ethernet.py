class ethernet_message(object):
    'ethernet protocol'
    def __init__(self,source_address,destination_address,data):
        self.source_address = source_address
        self.destination_address = destination_address
        self.data = data
    
    def encode(self,s):
        for c in s:
            str_s = ''.join([bin(ord(c)).replace('0b','')])#ascii to bin

        return str_s
    # def encode(s):
    #      for c in s:
    #         return ''.join([bin(ord(c)).replace('0b','')])

    def ethernet_part1(self):
        #preamble unit 同步码
        str_1 = '10101010'
        str_2 = '10101011'
        part1 = hex(int(str_1,2))*7+hex(int(str_2,2))#bin2hex
        return part1
    
    def ethernet_part2(self):
        #six bytes
        mac_source = self.encode(self.source_address)
        if len(mac_source)<= 48:
            part2 = '0'*(48-len(mac_source))+mac_source
        else:
            part2 = mac_source[0:48]
        return part2

    def ethernet_part3(self):
        destination_address = self.encode(self.destination_address)
        if len(destination_address)<=48:
            part3='0'*(48-len(destination_address))+destination_address
        else:
            part3 = destination_address[0:48]
        return part3
    
    def ethernet_part4(self):
        part4 = (16-len(bin(self.data))+2)*'0'+bin(self.data)[2:]
        return part4

    def ethernet_part5(self):
        part5 = '10101010'*2 +'00000011' #LLC
        return part5
    
    def ethernet_part6 (self):
        part6 = bin(self.data)[2:]
        return part6

    def ethernet_part7(self):
        part7 = '00000000'*4
        return part7
