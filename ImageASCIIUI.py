import random
import time
import warnings
import string
import dialogs
from PIL import Image, ImageFont, ImageDraw, ImageStat, ImageEnhance

import photos,os

def save(sender):
	global text
	global imsize
	im = RenderASCII(text)
	im.save('Place.jpg')
	a=photos.create_image_asset('Place.jpg')
	

def _getfont(fontsize):
	'''Return the ImageFont for the font I'm using'''
	try:
		return ImageFont.truetype("DejaVuSansMono", fontsize*4)
	except IOError:
		import _font_cache
		return ImageFont.truetype(_font_cache.get_font_path('DejaVuSansMono'))
		
		
def visual_weight(char):
	'''Return the (approximate) visual weight for a character'''
	font = _getfont(10)
	# The size of the letter
	width, height = font.getsize(char)
	# Render the letter in question onto an image
	im = Image.new("RGB", (width, height), (255, 255, 255))
	dr = ImageDraw.Draw(im)
	dr.text((0, 0), char, (0, 0, 0), font=font)
	# Mean of image is visual weight
	stat = ImageStat.Stat(im)
	lightness = stat.mean[0]
	# Project the lightness from a scale of 100 to a scale of 255
	lightness = (255 - lightness) / 100.0 * 255
	return lightness
	
	
def gen_charmap(chars=string.printable):
	'''Generate a character map for all input characters, mapping each character
	to its visual weight.'''
	# Use the translate method with only the second `deletechars` param.
	chars = chars.replace("\n", "").replace("\r", "").replace("\t", "")
	charmap = {}
	for c in chars:
		weight = visual_weight(c)
		if weight not in charmap:
			charmap[weight] = ''
		charmap[weight] += c
	return charmap
	
	
def resize(im, base=200):
	# Resize so the smaller image dimension is always 200
	if im.size[0] > im.size[1]:
		x = im.size[1]
		y = im.size[0]
		a = False
	else:
		x = im.size[0]
		y = im.size[1]
		a = True
		
	percent = (base/float(x))
	size = int((float(y)*float(percent)))
	if a:
		im = im.resize((base, int(size*0.5)), Image.ANTIALIAS)
	else:
		im = im.resize((size, int(base*0.5)), Image.ANTIALIAS)
	return im
	
	
def image2ASCII(im, scale=75, showimage=False, charmap=gen_charmap()):
	del charmap[122.82499999999997]
	thresholds = list(charmap.keys())
	grayscale = list(charmap.values())
	
	if showimage:
		im.show()
	# Make sure an image is selected
	if im is None:
		raise ValueError("No Image Selected")
	# Make sure the output size is not too big
	if scale > 500:
		warnings.warn("Image cannot be more than 500 characters wide")
		scale = 500
		
	# Resize the image and convert to grayscale
	im = resize(im, scale).convert("L")
	# Optimize the image by increasing contrast.
	enhancer = ImageEnhance.Contrast(im)
	im = enhancer.enhance(1.5)
	
	# Begin with an empty string that will be added on to
	output = ''
	
	# Create the ASCII string by assigning a character
	# of appropriate weight to each pixel
	for y in range(im.size[1]):
		for x in range(im.size[0]):
			luminosity = 255-im.getpixel((x, y))
			# Closest match for luminosity
			closestLum = min(thresholds, key=lambda x: abs(x-luminosity))
			row = thresholds.index(closestLum)
			possiblechars = grayscale[row]
			output += possiblechars[random.randint(0, len(possiblechars)-1)]
		output += '\n'
		
	# return  the final string
	return output
	
	
def RenderASCII(textl, fontsize=200, bgcolor='#EDEDED'):
	'''Create an image of ASCII text'''
	linelist = textl.split('\n')
	fon = _getfont(fontsize)
	width, height = fon.getsize(linelist[1])
	
	image = Image.new("RGB", (width, height*len(linelist)), bgcolor)
	draw = ImageDraw.Draw(image)
	
	for x in range(len(linelist)):
		line = linelist[x]
		draw.text((0, x*height), line, (0, 0, 0), font=fon)
	return image
# 7:80,5:95,4:130,3:195



resolution = 'high'

import console,time

import photos,os,ui
r = dialogs.alert('Image', '', 'Camera', 'Photo Library')

rolling = True

if r ==1:
	x=photos.capture_image()
	x.save('placeholder.jpg')
	
elif r==2:
	x=photos.Asset.get_image(photos.pick_asset(photos.get_assets()))
	x.save('placeholder.jpg')

im =Image.open('placeholder.jpg')
global imsize
if im.height > im.width:
	vals={'low':[6.3,95],'med':[4.75,130],'high':[3,205]}
	v=ui.load_view('uiImageAscii')
	sa=ui.ButtonItem()
	sa.action = save
	sa.title = 'Save'
	v.right_button_items = [sa]
	
	print('Loading in portrait...')
else:
	v = ui.load_view('uiImageAsciiLan')
	vals={'low':[5,110],'med':[4,145],'high':[3,300],'screen':[4,200]}
	print('Loading in landscape...')

font, imsize = vals[resolution]
global text

console.set_font('Menlo',font)
text=image2ASCII(im,imsize,showimage=False)

label = v['label1']
label.font = ('Menlo',font)
v.present()
out = ''
count = 0
if resolution == 'high' or resolution == 'screen':
	speed = 50
else:
	speed=25
if rolling:
	
		
	try:
		while 1:
			if count > len(text) - 1:
				break
				
			out += text[count:count + speed]
			count += speed
			label.text = out
		
	except:
		while 1:
			if count > len(text) - 1:
				break
			out += text[count]
			count +=1
			label.text=out
		

else:
	label.text = text
import clipboard
clipboard.set(text)
console.set_font('Menlo',11)
os.remove('placeholder.jpg')
