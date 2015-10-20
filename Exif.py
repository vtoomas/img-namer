import sys
from tags import TAGS
import struct

class Exif():
    """Class for reading Exif data from JPEG file.  """
    def __init__(self, file_name = ''):
        self._MKRBEGIN = '\xff'
        self._JPEGBEGIN = '\xff\xd8'
        self._JPEGEND = '\xff\xda'
        self.endianness = '<'
        self.file = 0
        self._TIFFBEGIN = 12
        self._IFDBEGIN = 0

        if file_name != '':
            self.open_file(file_name)
            self.verify()

    def read_short(self):
        return struct.unpack(self.endianness + 'H', self.file.read(2))[0]
    def read_long(self):
        return struct.unpack(self.endianness + 'L', self.file.read(4))[0]

    def open_file(self, file_name):
        # print 'Opening file', file_name
        try:
            self.file = open(file_name, 'rb')
        except Exception, e:
            print 'File "' + file_name + '" could not be read. Please try again. '
            sys.exit()
        
    def verify(self):
        if self.file != 0:
            data = self.file.read(2)
            if data == self._JPEGBEGIN:
                pass # print 'JPEG read successfully. '
            else:
                print 'Failed to verify JPEG. Exiting..'
                sys.exit()
            
            self.file.seek(self._TIFFBEGIN)
            data = self.file.read(2)
            if data == '\x49\x49':
                self.endianness = '<'
                # print 'Exif data is little-endian'
            elif data == '\x4d\x4d':
                self.endianness = '>'
                print 'Exif data is big-endian'
            else:
                print 'Problem verifying endianness. '

            assert self.file.read(2) == struct.pack(self.endianness + 'h', 42) # Last check if we got TIFF header read properly

            self._IFDBEGIN = self._TIFFBEGIN + struct.unpack(self.endianness + 'h', self.file.read(2))[0]
            

    def read_all_IFD(self):
        all_IFD_entries = {}
        self.file.seek(self._IFDBEGIN)
        while 1:
            IFD_data = self.read_IFD(self.file.tell())
            all_IFD_entries.update(IFD_data)
            if IFD_data['next_IFD_offset'] != 0:
                self.file.seek(self._TIFFBEGIN + IFD_data['next_IFD_offset'])
                
            else:
                ExifIFDPointer = struct.unpack(self.endianness + 'L', all_IFD_entries['ExifIFDPointer']['data'])[0]
                all_IFD_entries.update(self.read_IFD(self._TIFFBEGIN + ExifIFDPointer))
                break
        return all_IFD_entries
        
    def read_IFD(self, location):
        collection = {}
        formats = { 1:1, 2:1, 3:2, 4:4, 5:8, 6:1, 7:1, 8:2, 9:4, 10:8, 11:4, 12:8 }

        self.file.seek(location)
        ifd_entries = self.read_short()
        # print '[read_IFD] Num of entries is:', ifd_entries
        for i in range(ifd_entries):
            entry = {}
            entry['tag'] = self.read_short()
            entry['tag_name'] = TAGS[entry['tag']]
            entry['data_format'] = self.read_short()
            entry['data_size'] = self.read_long()
            
            datasize = formats[entry['data_format']] * entry['data_size']
            if datasize > 4: # If data bigger then 4 bytes, data contains offset to actual data
                curpos = self.file.tell()
                self.file.seek(self._TIFFBEGIN + self.read_long())
                entry['data'] = self.file.read(datasize - 1) # Ignore the 0-byte for now
                self.file.seek(curpos + 4)
            else:
                entry['data'] = self.file.read(4)

            collection[entry['tag_name']] = entry
        
        next_IFD_offset = self.read_long()
        collection['next_IFD_offset'] = next_IFD_offset
        return collection


def usage():
    print 'Usage: python Exif.py <JPEG file>'

def main():
    if len(sys.argv) != 2:
        usage()
    else:
        exif = Exif(sys.argv[1])
        testread = exif.read_all_IFD()
        print testread
        exif.file = 0 
        

if __name__ == '__main__':
    main()