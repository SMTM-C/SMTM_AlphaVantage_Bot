async def canvas(ctx, text=None):
    #print('\n'.join(dir(ctx)))
    #print('\n'.join(dir(ctx.author)))

    # --- create empty image ---

    #IMAGE_WIDTH = 600
    #IMAGE_HEIGHT = 300

    # create empty image 600x300 
    #image = Image.new('RGB', (IMAGE_WIDTH, IMAGE_HEIGHT)) # RGB, RGBA (with alpha), L (grayscale), 1 (black & white)

    # --- load image from local file ---

    # or load existing image
    #image = Image.open('/home/furas/Obrazy/images/lenna.png')

    # --- load image from url ---

    import urllib.request    

    url = 'https://upload.wikimedia.org/wikipedia/en/7/7d/Lenna_%28test_image%29.png?download'

    response = urllib.request.urlopen(url)
    image = Image.open(response)  # it doesn't need `io.Bytes` because it `response` has method `read()`
    print('size:', image.size)

    #IMAGE_WIDTH, IMAGE_HEIGHT = image.size
    IMAGE_WIDTH = image.size[0] 

    # --- draw on image ---

    # create object for drawing
    draw = ImageDraw.Draw(image)

    # draw red rectangle with green outline from point (50,50) to point (550,250) #(600-50, 300-50)
    draw.rectangle([50, 50, IMAGE_WIDTH-50, IMAGE_HEIGHT-50], fill=(255,0,0, 128), outline=(0,255,0))

    # draw text in center
    text = f'Hello {ctx.author.name}'

    font = ImageFont.truetype('Arial.ttf', 30)

    text_width, text_height = draw.textsize(text, font=font)
    x = (IMAGE_WIDTH - text_width)//2
    y = (IMAGE_HEIGHT - text_height)//2

    draw.text( (x, y), text, fill=(0,0,255), font=font)

    # --- avatar ---

    #print('avatar:', ctx.author.avatar_url)
    #print('avatar:', ctx.author.avatar_url_as(format='jpg'))
    #print('avatar:', ctx.author.avatar_url_as(format='png'))

    AVATAR_SIZE = 128

    # get URL to avatar
    # sometimes `size=` doesn't gives me image in expected size so later I use `resize()`
    avatar_asset = ctx.author.avatar_url_as(format='jpg', size=AVATAR_SIZE)

    # read JPG from server to buffer (file-like object)
    buffer_avatar = io.BytesIO()
    await avatar_asset.save(buffer_avatar)
    buffer_avatar.seek(0)

    # read JPG from buffer to Image 
    avatar_image = Image.open(buffer_avatar)

    # resize it 
    avatar_image = avatar_image.resize((AVATAR_SIZE, AVATAR_SIZE)) # 

    x = 50 + 5
    y = (IMAGE_HEIGHT-AVATAR_SIZE)//2  # center vertically
    image.paste(avatar_image, (x, y))

    # --- sending image ---

    # create buffer
    buffer_output = io.BytesIO()

    # save PNG in buffer
    image.save(buffer_output, format='PNG')    

    # move to beginning of buffer so `send()` it will read from beginning
    buffer_output.seek(0) 

    # send image
    await ctx.send(file=File(buffer_output, 'myimage.png'))