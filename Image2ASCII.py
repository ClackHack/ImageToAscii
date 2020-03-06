'''Works well with high contrast'''
import random
import time
import warnings
import string

from PIL import Image, ImageFont, ImageDraw, ImageStat, ImageEnhance


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
	
	
def RenderASCII(text, fontsize=200, bgcolor='#EDEDED'):
	'''Create an image of ASCII text'''
	linelist = text.split('\n')
	font = _getfont(fontsize)
	width, height = font.getsize(linelist[1])
	
	image = Image.new("RGB", (width, height*len(linelist)), bgcolor)
	draw = ImageDraw.Draw(image)
	
	for x in range(len(linelist)):
		line = linelist[x]
		draw.text((0, x*height), line, (0, 0, 0), font=font)
	return image
# 7:80,5:95,4:130,3:195

vals={'low':[5,95],'med':[4,130],'high':[3,195]}

resolution = 'high'
font, imsize = vals[resolution]
import console,time
console.set_font('Menlo',font)
import photos,os
x=photos.capture_image()
x.save('placeholder.jpg')
im =Image.open('placeholder.jpg')
text=image2ASCII(im,imsize,showimage=False)
for i in text:
	print(i,end='')
	time.sleep(0.00001)
	

console.set_font('Menlo',11)
os.remove('placeholder.jpg')
