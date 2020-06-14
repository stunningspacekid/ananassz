#!/usr/bin/env python
# coding: utf-8

# In[76]:


from os.path import getsize
from binascii import b2a_hex, a2b_hex
from random import choice

# Constants
###########################################
START_BUFFER = b'EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE'
END_BUFFER = b'FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF'
TAB = b'\t'
###########################################

class Common:
    ''' 
    Provides common functions for steg classes. 
    Primary function is to convert files into workable binary and provide cryptographic support.
    '''

    def __init__(self, file_path):
        self.carrier_file = file_path

        if file_path != None:
            self.file_type = (file_path.split('.')[-1]).upper()
    
    def text_to_binary(self, file_path, max_size):
        '''
        Reads a payload file and converts it to binary with the appropriate buffers.
        :param file_path: The path of the payload file.
        :param max_size: Used to determine how much extra random data should be appended to the end of the message.
        '''
        "print(type(file_path))
        if type ( file_path )  == 'str':
            text = file_path
            
        else:
            try:
                text_file = open(file_path, 'rb').read()
                hidden_file = file_path.split('.')[-1]
            except Exception as e:
                raise Exception('[!] Failed to open target file: {}'.format(str(e)))
            try:
                text = text_file.read()
                text += TAB

        # add buffers and file format
        text += START_BUFFER + TAB
        text += str.encode(hidden_file) + TAB
        text += END_BUFFER
        text_file.close()

        # convert to hex string
        hex_text = b2a_hex(text).decode('ascii')
        # convert hex to binary and fill the rest of the bitstream with random hex
        b = ''
                
        for ch in hex_text:
                tmp = bin(ord(ch))[2:]
                if len(tmp) < 7:
                    for _ in range(0,(7-len(tmp))):
                        tmp = '0' + tmp
                b += tmp
        for _ in range(0,(max_size - len(b)),7):
            b += str(bin(ord(choice('abcdef')))[2:])
        return b
        
        except Exception as e:
            raise Exception('[!] Text to binary conversion failed! {}'.format(str(e)))

            
    def set_bit(self, old_byte, new_bit):
        '''
        Takes a byte and alters the least significant bit.
        :param old_byte: The original Byte.
        :param new_bit: New bit value.
        '''
        b = list(bin(old_byte))
        b[-1] = new_bit
        return int(''.join(b),2)

    def reconstitute_from_binary(self, raw_bits):
        try:
            # break long string into array for bytes
            b = [raw_bits[i:i+7] for i in range(0, len(raw_bits), 7)]
            # convert to string
            c = ''
            for i in b:
                c += chr(int(i,2))
            # if the string length is not even, add a digit
            if len(c) % 2 != 0:
                c += 'A'
                
            # convert back to ascii
            as_ascii = a2b_hex(c[:-10].encode('ascii'))
            # check to see if the buffer is intact still
            buffer_idx = as_ascii.find(START_BUFFER)
            buffer_idx2 = as_ascii.find(END_BUFFER)
        except Exception as e:
            raise Exception(str(e))

        if buffer_idx != -1:
            fc = as_ascii[:buffer_idx]
        else:
            raise Exception('[!] Failed to find message buffer...')

        if buffer_idx2 != -1:
            payload_file_type = '.' + as_ascii[buffer_idx+49:buffer_idx2-1].decode('ascii')
        else:
            raise Exception('[!] Unknown file type in extracted message')

        if (buffer_idx != -1) and (buffer_idx2 != -1):
            try:
                to_save = open('hidden_file' + payload_file_type, 'wb')
                to_save.write(fc)
                to_save.close()
                print('[+] Successfully extracted message: {}{}'.format('hiddenFile', payload_file_type))
            except Exception as e:
                raise Exception('[!] Failed to write extracted file: {}'.format(str(e)))
            finally:
                to_save.close()
                return 'hidden_file' + payload_file_type
    
    def get_payload_size(self, file_path):
        '''
        Returns the size of the potential payload.
        '''
        return getsize(file_path)*8


# In[77]:



from PIL import Image as img

class IMG:
    '''
    Class for hiding binary data within select lossless image formats.
    Supported image formats: PNG, TIFF, BMP 
    :param payload_path: The path of the payload (message) that should be hidden.
    :param image_path: The path of the carrier image in which to hide the payload.
    '''
    def __init__(self, payload_path=None, image_path=None):
        self.payload_to_hide = payload_path
        self.carrier_image = image_path
        self.file_type = None
        self.fg = None
        self.image_type = None
        self.max_image_size = 0
        self.image_mode = None
        self.payload = None
        self.common = Common(self.payload_to_hide)
        self.supported = ['PNG','TIFF','TIF','BMP','ICO']

        assert self.carrier_image is not None

        # Get the file type from payload path
        self.file_type = self.payload_to_hide.split('.')[-1] if self.payload_to_hide else None
        # Analyze image attributes
        self.analyze_image()

    def analyze_image(self):
        '''
        Opens the carrier image file and gathers details.
        '''
        try:
            # Open the image file using PIL
            self.fg = img.open(self.carrier_image)
            # Get the carrier image name and type from the path
            self.image_type = self.carrier_image.split('.')[-1]
            # Get the total number of pixels that can be manipulated
            self.max_image_size = self.fg.size[1] * self.fg.size[0]
            # Gets the image mode, hopefully this is L, RGB, or RGBA
            self.image_mode = ''.join(self.fg.getbands())
        except Exception as err:
            raise Exception('Error analyzing image: {} - {}'.format(self.carrier_image, str(err)))

    def assign_output_file_type(self):
        '''
        Determines the correct file format.
        '''
        image_type = self.image_type.lower()
        if image_type in ['jpg', 'jpeg']:
            return 'jpeg'
        elif image_type in ['tif', 'tiff']:
            return 'TIFF'
        elif image_type == 'png':
            return 'png'
        elif image_type == 'bmp':
            return 'bmp'
            

    def _use_correct_function_hide(self):
        '''
        Depending on image mode will use the different hiding methods.
        '''
        if self.image_mode == 'L':
            self.L_replace_bits(self.payload_to_hide)
        elif self.image_mode in ['RGB', 'BGR']:
            self.RGB_replace_bits(self.payload_to_hide)
        elif self.image_mode == 'RGBA':
            self.RGBA_replace_bits(self.payload_to_hide)
        elif self.image_mode == '1':
            print("[!] Cannot hide content using an image with a mode of '1'")
        else:
            print("[!] Error determining image mode")

    def _use_correct_function_extract(self):
        '''
        depending on IMG format will use the different Extraction methods
        '''
        if self.image_mode == 'L':
            return self.L_extract_message(self.fg)
        elif self.image_mode in ['RGB', 'BGR']:
            return self.RGB_extract_message(self.fg)
        elif self.image_mode == 'RGBA':
            return self.RGBA_extract_message(self.fg)
        elif self.image_mode == '1':
            print("[!] Cannot extract content using an image with a mode of '1'")
            return '.'
        else:
            print("[!] Error determining image mode")

    def RGB_replace_bits(self, payload):
        '''
        Replace the least-significant bit for RGB images.
        :param payload: This is the path of the payload file.
        '''
        # 3 bytes per pixel should be greater than 2* the binary message length
        if self.max_image_size*3 <= 2*self.common.get_payload_size(payload):
            raise Exception('[!] Attempting to hide a message that is too large for the carrier')

        # generate bitstream 
        bitstream = iter(self.common.text_to_binary(payload, self.max_image_size * 3))

        # create a new empty image the same size and mode as the original
        newIm = img.new("RGB", (self.fg.size[0], self.fg.size[1]), "white") 
        try:
            for row in range(self.fg.size[1]):
                for col in range(self.fg.size[0]):
                    # get the value for each byte of each pixel in the original image
                    fgr,fgg,fgb = self.fg.getpixel((col,row))

                    # get the new lsb value from the bitstream
                    rb = next(bitstream)
                    # modify the original byte with our new lsb
                    fgr = self.common.set_bit(fgr, rb)

                    gb = next(bitstream)
                    fgg = self.common.set_bit(fgg, gb)

                    bb = next(bitstream)
                    fgb = self.common.set_bit(fgb, bb)
                    # add pixel with modified values to new image
                    newIm.putpixel((col, row),(fgr, fgg, fgb))
            output_file_type = self.assign_output_file_type()
            newIm.save(str('new.' + output_file_type), output_file_type)
            print('[+] {} created'.format('new.' + output_file_type))
        except Exception as e:
            raise Exception('Failed to write new file: {}'.format(str(e)))


    # extract hidden message from RGB image
    def RGB_extract_message(self, fg):
        '''
        Extracts and reconstructs payloads concealed in RGB images.
        :param fg: This is the PngImageFile of the carrier image.
        '''
        hidden = ''
        try:
            # iterate through each pixel and pull the lsb from each color per pixel
            for row in range(fg.size[1]):
                for col in range(fg.size[0]):
                    fgr,fgg,fgb = fg.getpixel((col,row))
                    
                    hidden += bin(fgr)[-1]
                    hidden += bin(fgg)[-1]
                    hidden += bin(fgb)[-1]
            try:
                returned_file = self.common.reconstitute_from_binary(hidden)
                return returned_file
            except Exception as e:
                raise Exception('Inner failed to extract message: {}'.format(str(e)))
        except Exception as e:
            raise Exception('Outer failed to extract message: {}'.format(str(e)))

    #LSB steg for Black and white images
    def L_replace_bits(self, payload):
        '''
        Replace the least-significant bit for L images.
        :param payload: This is the path of the payload file.
        '''
        if self.max_image_size <= 2*self.common.get_payload_size(payload):
            raise Exception('[!] Attempting to hide a message that is too large for the carrier')

        # generate bitstream 
        bitstream = iter(self.common.text_to_binary(payload, self.max_image_size * 3))

        newIm = img.new("L", (self.fg.size[0], self.fg.size[1]), "white") 
        try:
            for row in range(self.fg.size[1]):
                for col in range(self.fg.size[0]):
                    fgL = self.fg.getpixel((col,row))

                    nextbit = next(bitstream)
                    fgL = self.common.set_bit(fgL, nextbit)

                    # add pixel to new image
                    newIm.putpixel((col,row),(fgL))
            output_file_type = self.assign_output_file_type()
            newIm.save(str('new.' + output_file_type), output_file_type)
            print('[+] {} created'.format('new.' + output_file_type))
        except Exception as e:
            raise Exception('Failed to write new file: {}'.format(str(e)))

    # extract hidden message from L image
    def L_extract_message(self, fg):
        '''
        Extracts and reconstructs payloads concealed in L images.
        :param fg: This is the PngImageFile of the carrier image.
        '''
        hidden = ''
        try:
            # iterate through each pixel and pull the lsb from each color per pixel
            for row in range(fg.size[1]):
                for col in range(fg.size[0]):
                    fgL = fg.getpixel((col,row))
                    
                    hidden += bin(fgL)[-1]
            try:
                returned_file = self.common.reconstitute_from_binary(hidden)
                return returned_file
            except Exception as e:
                raise Exception('Inner failed to extract message: {}'.format(str(e)))
        except Exception as e:
            raise Exception('Outer failed to extract message: {}'.format(str(e)))

    # replace lest-significant bit for RGBA images
    def RGBA_replace_bits(self, payload):
        '''
        Replace the least-significant bit for RGBA images.
        :param payload: This is the path of the payload file.
        '''
        if self.max_image_size*3 <= 2*self.common.get_payload_size(payload):
            raise Exception('[!] Attempting to hide a message that is too large for the carrier')

        # generate bitstream 
        bitstream = iter(self.common.text_to_binary(payload, self.max_image_size * 3))

        newIm = img.new("RGBA", (self.fg.size[0], self.fg.size[1]), "white") 
        try:
            for row in range(self.fg.size[1]):
                for col in range(self.fg.size[0]):
                    fgr, fgg, fgb, fga = self.fg.getpixel((col, row))

                    redbit = next(bitstream)
                    fgr = self.common.set_bit(fgr, redbit)

                    greenbit = next(bitstream)
                    fgg = self.common.set_bit(fgg, greenbit)

                    bluebit = next(bitstream)
                    fgb = self.common.set_bit(fgb, bluebit)
                    # add pixel to new image
                    newIm.putpixel((col, row),(fgr, fgg, fgb, fga))
            # if our passed in location exists, try saving there
            output_file_type = self.assign_output_file_type()
            newIm.save(str('new.' + output_file_type), output_file_type)
            print('[+] {} created'.format('new.' + output_file_type))
        except Exception as e:
            raise Exception('[!] Failed to write new file: {}'.format(str(e)))

    # extract hidden message from RGBA image
    def RGBA_extract_message(self, fg):
        '''
        Extracts and reconstructs payloads concealed in RGBA images.
        :param fg: This is the PngImageFile of the carrier image.
        '''
        hidden = ''
        try:
            # iterate through each pixel and pull the lsb from each color per pixel
            for row in range(fg.size[1]):
                for col in range(fg.size[0]):
                    fgr, fgg, fgb, fga = fg.getpixel((col, row))
                    
                    hidden += bin(fgr)[-1]
                    hidden += bin(fgg)[-1]
                    hidden += bin(fgb)[-1]
            try:
                returned_file = self.common.reconstitute_from_binary(hidden)
                return returned_file
            except Exception as e:
                raise Exception('Inner failed to extract message: {}'.format(str(e)))
        except Exception as e:
            raise Exception('Outer failed to extract message: {}'.format(str(e)))
    
    def hide(self):
        '''
        Hides a payload within a carrier image. Defaults to outputting the new image into the 
        current directory with the name `new.<file_type>`.
        '''
        self._use_correct_function_hide()

    def extract(self):
        '''
        Extracts a payload from a carrier image if possible. Defaults to output the payload into the
        current directory with the name `hidden_file.<file_type>`.
        '''
        self._use_correct_function_extract()


# In[78]:


import base64
from PIL import Image

def encode_txt(string, image = 'help.png'):
    
    string = base64.b64encode(bytes(string, 'utf-8'))
    with open(image, "wb") as fh:
        fh.write(base64.decodebytes(string))
       
    return fh

def decode_txt(image):
    with open(image, "rb") as image:
        b64string = base64.b64encode(image.read())
        
        b64string = b64string.decode('ascii')
        message_bytes = base64.b64decode(b64string)
        message = message_bytes.decode('ascii')

    return message


# In[79]:


#tests


# In[80]:


message = 'soma roma in the dooooooooma!!!!!!!!11!'
message = encode_txt(message)
message
oj = IMG('help.png', 'God.jpg')
oj.hide()


# In[4]:


import anvil.server
anvil.server.connect('5LSBOEJLV4COQJ5K266QJ4T6-LGPIPMYGEZILEW3O')


# In[6]:


import anvil.media

@anvil.server.callable
def fill_cont(file):
    with anvil.media.TempFile(file) as filename:
        img = load_img(filename)


# In[ ]:




