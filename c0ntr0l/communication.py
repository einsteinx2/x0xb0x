import string
from packet import Packet
from binascii import a2b_hex
from binascii import b2a_hex
from DataFidelity import crc8
from Globals import *
from pattern import Pattern

import time




#
# Messages from the c0ntr0l software to the x0xb0x.
#
PING_MSG = '\x01'
WRITE_PATTERN_MSG = '\x10'
READ_PATTERN_MSG = '\x11'
LOAD_PATTERN_MSG = '\x04'
SET_BANK_MSG = '\x05'
GET_BANK_MSG = '\x06'
SET_PATTERN_MSG = '\x07'
GET_PATTERN_MSG = '\x08'
TOGGLE_SEQUENCER_MSG = '\x09'
GET_SEQUENCER_STATE_MSG = '\x0B'
SET_SYNC_MSG = '\x0C'
GET_SYNC_MSG = '\x0D'
SET_TEMPO_MSG = '\x0E'
CTRL_GET_TEMPO_MSG = '\x0F'

#
# Messages from the x0xb0x to the c0ntr0l software.
#
X0X_PING_MSG = '\x01'
X0X_STATUS_MSG = '\x80'
X0X_PATT_MSG = '\x19'

class DataLink:
    def __init__ (self, serialPort):
        self.s = serialPort

#----------------------- Basic Packet Sending Primitives --------------------

    def sendBasicPacket(self, packetType, content='') :
        try:
            header = packetType
            header += chr((len(content) >> 8) & 0xFF)
            header += chr(len(content) & 0xFF)
            
            packetToSend = header + content + crc8(header + content)
            print 'Sending Packet: ' + b2a_hex(packetToSend)
            self.s.write(packetToSend)
        except Exception, e:
            print 'Exception occured in sendBasicPacket(): ' + str(e)
            raise CommException('Error occured in sendBasicPacket()')

    def getBasicPacket(self) :
        try:
            self.s.setTimeout(DEFAULT_TIMEOUT)

            packet = Packet([])
            character = self.s.read()
            while character :
                packet.addBytes(character)
                if packet.isComplete :
                    break
                character = self.s.read()
            return packet
        except Exception, e:
            print 'Exception occured in getBasicPacket(): ' + str(e)
            raise CommException('Error occured in getBasicPacket()')

#----------------- Specific Packet Types ---------------------------------
    def sendPingMessage(self):
        self.s.flushInput()
        self.sendBasicPacket(PING_MSG)

        packet = self.getBasicPacket()
        if packet.isCorrect:
            packet.printMe()
        else:
            packet.printMe()
            print 'Bad packet!'

    def sendReadPatternMessage(self, bank, loc):
        self.s.flushInput()
        self.sendBasicPacket(READ_PATTERN_MSG, content = chr(bank) + chr(loc))

        packet = self.getBasicPacket()
        if packet.isCorrect:
            packet.printMe() 
        else:
            packet.printMe()
            print 'Bad packet!'


        if packet.isCorrect and packet.messageType() == X0X_PATT_MSG:
            pat = Pattern(packet.content())
            return pat
        else:
            print 'Error: Received a bad pattern.'
            raise BadPacketException('Received a bad pattern.')
        

    def sendWritePatternMessage(self, pattern, bank, loc):
        #
        # Convert pattern to binary
        #
        self.s.flushInput()
        self.sendBasicPacket(WRITE_PATTERN_MSG, content = chr(bank) + chr(loc) + pattern.toByteString())

        packet = self.getBasicPacket()
        if packet.isCorrect:
            packet.printMe()
        else:
            packet.printMe()
            print 'Bad Packet!'

    #
    # Sequencer run/stop control
    #
    def sendLoadPatternMessage(self, bank, loc) :
        self.sendBasicPacket(LOAD_PATTERN_MSG, content=[dec2hex(bank), dec2hex(loc)])
        packet = self.getBasicPacket()
        print packet

    def sendSetBankMessage(self, bank) :
        self.sendBasicPacket(SET_BANK_MSG, content = [dec2hex(bank)])
        packet = self.getBasicPacket()
        print packet

    def sendGetBankMessage(self) :
        self.sendBasicPacket(GET_BANK_MSG)
        packet = self.getBasicPacket()
        print packet

    def sendSetLocationMessage(self, loc) :
        self.sendBasicPacket(SET_LOCATION_MSG, content = [dec2hex(loc)])
        packet = self.getBasicPacket()
        print packet

    def sendGetLocationMessage(self) :
        self.sendBasicPacket(GET_LOCATION_MSG)
        packet = self.getBasicPacket()
        print packet

    def sendToggleSequencerMessage(self) :
        self.sendBasicPacket(TOGGLE_SEQUENCER_MSG)
        packet = self.getBasicPacket()
        print packet

    def sendGetSequencerStatePacket(self) :
        self.sendBasicPacket(GET_SEQUENCER_STATE_MSG)
        packet = self.getBasicPacket()
        print packet

    #
    # Sync and tempo messages
    #
    def sendSetSyncPacket(self, source) :
        self.sendBasicPacket(SET_SYNC, content = [dec2hex(source)])
        packet = self.getBasicPacket()
        print packet

    def sendGetSyncPacket(self) :
        self.sendBasicPacket(GET_SYNC)
        packet = self.getBasicPacket()
        print packet

    def sendSetTempoPacket(self, tempo) :
        self.sendBasicPacket(SET_TEMPO, content = [dec2hex(tempo)])
        packet = self.getBasicPacket()
        print packet

    def sendGetTempoPacket(self) :
        self.sendBasicPacket(GET_TEMPO)
        packet = self.getBasicPacket()
        print packet


        
def dec2hex(dec) :
    hexstring = (hex(dec).upper().split('X'))[1]

    #
    # If necessary, pad the hexstring with a zero so that
    # there are an even number of characters in the string.
    #
    if len(hexstring) % 2 != 0:
        hexstring = '0' + hexstring

    return hexstring
    
class CommException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class BadPacketException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
