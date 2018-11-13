# import section
from pysnmp.hlapi import *
from ipaddress import *
from datetime import datetime

# var section

#snmp
community_string = 'public'  
ip_address_host = ''  
port_snmp = 161
OID_SerialNo = '1.3.6.1.2.1.43.5.1.1.17.1 '  # From SNMPv2-MIB hostname/SerialNo
OID_Counter = '1.3.6.1.2.1.43.10.2.1.4.1.1'
filename_of_ip = 'ip.txt' #    Ip 
#log
filename_log = 'OutputLog.'+datetime.strftime(datetime.now(), "%Y%m%d-%H%M%S")+'.txt'  # ��� ��� �����
log_level = 'debug'
#domain='mydomain.ru'

# function section

def snmp_getcmd(community, ip, port, OID):
# type class 'generator' errorIndication, errorStatus, errorIndex, result[3] - ������
# ����� get �������� ��������� ��������� � �������������� �� SNMP � �������� OID
    return (getCmd(SnmpEngine(),
                   CommunityData(community),
                   UdpTransportTarget((ip, port)),
                   ContextData(),
                   ObjectType(ObjectIdentity(OID))))

def snmp_get_next(community, ip, port, OID, file):
# ����� ������������ class generator �� def snmp_get
# ������������ errors, ����� ��� class 'pysnmp.smi.rfc1902.ObjectType' � OID (� name) � ���������  (� val)
# �������� ���� ��������� ��������
    errorIndication, errorStatus, errorIndex, varBinds = next(snmp_getcmd(community, ip, port, OID))

    if errors(errorIndication, errorStatus, errorIndex, ip, file):
        for name, val in varBinds:
            return (val.prettyPrint(), True)
    else:
        file.write(datetime.strftime(datetime.now(),
                                     "%Y.%m.%d %H:%M:%S") + ' : Error snmp_get_next ip = ' + ip + ' OID = ' + OID + '\n')
        return ('Error', False)

def get_from_file(file, filelog):  
#�������� ip ������� �� ����� file, ������ ������ � filelog     
     fd = open(file, 'r')
     list_ip = []
     for line in fd:
         line=line.rstrip('\n')
         if check_ip(line):
            list_ip.append(line)
         else:
            filed.write(datetime.strftime(datetime.now(),
                                              "%Y.%m.%d %H:%M:%S") + ': Error    ip  ' + line)
            print('Error    ip  ' + line)
     fd.close()

     return list_ip

def check_ip(ip): 
#  �������� ip ������ �� ������������. False �������� �� ��������.
    try:
       ip_address(ip)
    except ValueError:
        return False
    else:
        return True

def errors(errorIndication, errorStatus, errorIndex, ip, file):
    #  ��������� ������ � ������ ������ ���������� False � ����� � ���� file
    if errorIndication:
       print(errorIndication, 'ip address ', ip)
       file.write(datetime.strftime(datetime.now(), "%Y.%m.%d %H:%M:%S") + ' : ' + str(
                errorIndication) + ' = ip address = ' + ip + '\n')
       return False
    elif errorStatus:
         print(datetime.strftime(datetime.now(), "%Y.%m.%d %H:%M:%S") + ' : ' + '%s at %s' % (
         errorStatus.prettyPrint(),
         errorIndex and varBinds[int(errorIndex) - 1][0] or '?' ))
         file.write(datetime.strftime(datetime.now(), "%Y.%m.%d %H:%M:%S") + ' : ' + '%s at %s' % (
         errorStatus.prettyPrint(),
         errorIndex and varBinds[int(errorIndex) - 1][0] or '?' + '\n'))
         return False
    else:
         return True

#code section

#��������� ��� ����
filed = open(filename_log,'w')

# ���������� ������� �����
filed.write(datetime.strftime(datetime.now(), "%Y.%m.%d %H:%M:%S") + '\n')

ip_from_file = get_from_file(filename_of_ip, filed)

for ip_address_host in ip_from_file:
    # �������� SerialNo hostname+domainname, ���� ������
    SerialNo, flag_snmp_get = (snmp_get_next(community_string, ip_address_host, port_snmp, OID_SerialNo, filed))
    Counter, flag_snmp_get = (snmp_get_next(community_string, ip_address_host, port_snmp, OID_Counter, filed))
    if flag_snmp_get:
        # �� ������, ���� ������� �� snmp
        if SerialNo == 'No Such Object currently exists at this OID':
             # � community ��������.���� ���������� ����, ����� ������ traceback. ������ �� ����� �� ��������, ��� �������� � community, ������� ������ ���� ����������� hostname, ������� ������ ��� ����������
            print('ERROR community', SerialNo, ' ', ip_address_host)
            filed.write(datetime.strftime(datetime.now(),
                                          "%Y.%m.%d %H:%M:%S") + ' : ' + 'ERROR community SerialNo = ' + SerialNo + '  ip = ' + ip_address_host + '\n')
        else:

            if log_level == 'debug':
                filed.write(datetime.strftime(datetime.now(),
                                              "%Y.%m.%d %H:%M:%S") + ' : ' + '  SerialNo ' + SerialNo + '  Pages printed   ' + Counter + ' type ' + str(
                    type(SerialNo)) + ' len ' + str(len(SerialNo)) + ' ip ' + ip_address_host + '\n')
            if len(SerialNo) < 3:
                SerialNo = 'None_SerialNo'
                if log_level == 'debug' or log_level == 'normal':
                    filed.write(datetime.strftime(datetime.now(),
                                                  "%Y.%m.%d %H:%M:%S") + ' : ' + 'Error SerialNo  3  = ' + SerialNo + '  ip = ' + ip_address_host + '\n')
 
        print('IP: ' + ip_address_host + ' | SerialNo= ' + SerialNo + ' | Pages printed: ' + Counter)

filed.close()