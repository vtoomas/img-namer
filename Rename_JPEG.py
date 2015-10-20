from Exif import *
import sys, os, argparse, shutil

class Rename_JPEG(object):
    """docstring for Rename_JPEG"""
    def __init__(self, srcfile):
        self.srcfile = srcfile
        exif = Exif(srcfile)
        exif_data = exif.read_all_IFD() 
        self.dateStr = exif_data['DateTimeOriginal']['data'].split(' ')[0]
        self.timeStr = exif_data['DateTimeOriginal']['data'].split(' ')[1]
        self.model = exif_data['Model']['data']
        
    def _pattern_to_string(self, pattern):
        dd = self.dateStr[8:10]
        MM = self.dateStr[5:7]
        yy = self.dateStr[2:4]
        yyyy = self.dateStr[0:4]
        hh = self.timeStr[0:2]
        mm = self.timeStr[3:5]
        ss = self.timeStr[6:8]
        return pattern.replace('MODEL', self.model).replace('yyyy', yyyy).replace('dd', dd).replace('MM', MM).replace('yy', yy).replace('hh', hh).replace('mm', mm).replace('ss', ss)

    def calc_name(self, pattern):
        ext = '.jpeg'
        srcdir = os.path.dirname(os.path.abspath(self.srcfile))
        filelist = os.listdir(srcdir)
        new_name = self._pattern_to_string(pattern)
        
        def checkname(name, ext, fl, i):
            if not name + ext in fl:
                return name + ext
            elif not name + '-' + str(i).zfill(3) + ext in fl:
                return name + '-' + str(i).zfill(3) + ext
            else:
                return checkname(name, ext, fl, i + 1)

        new_name = os.path.join(srcdir, checkname(new_name, ext, filelist, 1)) 
        # print 'srcfile:', self.srcfile
        # print 'new_name:',new_name 
        return new_name

    def rename_as(self, pattern):
        os.rename(self.srcfile, self.calc_name(pattern))


def new_name(filepath, pattern):
    ren = Rename_JPEG(filepath)
    return ren.calc_name(pattern)

def rename_file(filepath, pattern):
    ren = Rename_JPEG(filepath)
    ren.rename_as(pattern)

def explore_dir(dirpath):
    included_extenstions = ['jpg','JPG','JPEG','jpeg' ] 
    file_names = [os.path.join(dirpath, fn) for fn in os.listdir(dirpath) if any([fn.endswith(ext) for ext in included_extenstions])]
    return file_names
            
def main():

    parser = argparse.ArgumentParser(description='Renames JPEG files based on Exif data from camera. ')
    parser.add_argument('dest_path', type=str, help='Specify a path to directory or file to process.')
    parser.add_argument('pattern', type=str, nargs='?', default='yyyy-MM-dd-hhmmss.MODEL', \
        help='A pattern of naming the file(s). Valid example of pattern (also default): yyyy-MM-dd-hhmmss.MODEL')
    parser.add_argument('-e', '--explore', type=str, help='Returns a list of JPEG files in directory. ')
    args = parser.parse_args()
    
    if os.path.isdir(args.dest_path):
        fs = explore_dir(args.dest_path)
        for f in fs:
            rename_file(f, args.pattern)
    else:
        rename_file(args.dest_path, args.pattern)
    

if __name__ == '__main__':
    main()