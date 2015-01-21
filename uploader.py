#!/usr/bin/env python
# - coding: utf-8
import os, sys, time, yaml, datetime, traceback
import wasanbon
from wasanbon.core.rtc import rtcprofile
from jinja2 import Environment, FileSystemLoader
from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import GetPosts, NewPost
from wordpress_xmlrpc.methods.users import GetUserInfo
from wordpress_xmlrpc.methods import posts, taxonomies, media
from wordpress_xmlrpc.compat import xmlrpc_client

from PIL import Image, ImageDraw, ImageFont


setting_filename = 'setting.txt'
#test_name = 'MapperViewer'
#test_name = None
test_name = "SFMLJoystick"

def is_test():
    return test_name != None

def is_upload():
    #return False
    return True


def create_image(rtcprof):

    len_svc_intf = 0
    for s in rtcprof.serviceports:
        len_svc_intf = len_svc_intf + len(s.serviceInterfaces)
    num_rightside_port = len(rtcprof.outports) + len(rtcprof.serviceports) + len_svc_intf
    num_leftside_port = len(rtcprof.inports)
    if num_rightside_port > num_leftside_port:
        num_port = num_rightside_port
    else:
        num_port = num_leftside_port
        pass

    top_margin = 20
    bottom_margin = 40
    top_bottom_margin = 20
    port_height = 20
    port_margin = 20
    num_margin = num_port -1
    if num_margin < 0: num_margin = 0
    img_height = num_port * port_height + num_margin * port_margin + top_bottom_margin *2 + top_margin + bottom_margin
    img_width  = 800

    fill_color = (20, 20, 255, 255)
    outline_color = (15, 15, 30, 255)
    text_color = (15, 15, 30, 255)
    line_color = (15, 15, 30, 255)

    text_font = ImageFont.truetype("/Library/Fonts/Courier New.ttf", 14)
    title_font = ImageFont.truetype("/Library/Fonts/Courier New.ttf", 20)
    im = Image.new('RGBA', (img_width, img_height), (228, 212, 162, 0))
    draw = ImageDraw.Draw(im)
    
    rtc_height = num_port * port_height + num_margin * port_margin + top_bottom_margin *2
    rtc_width  = 100

    rtc_topleft = ( (img_width - rtc_width) / 2, top_margin)
    rtc_rightbottom = (rtc_topleft[0] + rtc_width, top_margin + rtc_height)
    draw.rectangle((rtc_topleft, rtc_rightbottom), fill=fill_color, outline=outline_color)

    text = rtcprof.name
    width, height = draw.textsize(text, font=title_font)
    text_offset = (img_width/2 - width/2, top_margin + rtc_height + height/2)
    draw.text(text_offset, text, font=title_font, fill=text_color)
    
    outport_polygon = ((-port_height/2, -port_height/2), (+port_height/2, -port_height/2),
                       (port_height/2+port_height/2, 0), (port_height/2, port_height/2),
                       (-port_height/2, port_height/2), (-port_height/2, -port_height/2))
        
    for i, p in enumerate(rtcprof.outports):
        offset = (img_width/2 + rtc_width/2, top_margin + top_bottom_margin + (port_height+port_margin)*i + port_height/2)
        port_polygon = []
        for point in outport_polygon:
            port_polygon.append((point[0] + offset[0], point[1] + offset[1]))
        draw.polygon(port_polygon, fill=fill_color, outline=outline_color)
        
        text = p.name + '(' + p.type + ')'
        text_pos = (offset[0] + port_height/2, offset[1] - port_height*1.5)
        draw.text(text_pos, text, fill=text_color, font=text_font)


    svcport_polygon = ((-port_height/2, -port_height/2), (+port_height/2+port_height/2, -port_height/2),
                       (+port_height/2+port_height/2, port_height/2),
                       (-port_height/2, port_height/2), (-port_height/2, -port_height/2))
        
    len_svc = 0
    i = len(rtcprof.outports) - 1
    for j, s in enumerate(rtcprof.serviceports):
        i = i + 1
        offset = (img_width/2 + rtc_width/2, top_margin + top_bottom_margin + (port_height+port_margin)*i + port_height/2)

        for k, f in enumerate(s.serviceInterfaces):
            i = i + 1
            start = (offset[0] + port_height/2, offset[1])
            intf_offset = (img_width/2 + rtc_width/2 + port_height/2 * 5, top_margin + top_bottom_margin + (port_height+port_margin)*i + port_height/2)
            pivot0 = (start[0] + port_height/2 *2, start[1])
            pivot1 = (pivot0[0], intf_offset[1])
            draw.line((start, pivot0), fill=outline_color)
            draw.line((pivot0, pivot1), fill=outline_color)
            draw.line((pivot1, intf_offset), fill=outline_color)

            bbox = ((intf_offset[0], intf_offset[1]-port_height/2),
                    (intf_offset[0] + port_height, intf_offset[1]+port_height/2))

            if f.direction == 'Provided':
                draw.ellipse(bbox, outline=outline_color)
            else:
                draw.arc(bbox, 90, 270, fill=outline_color)

            text = f.type
            text_pos = (intf_offset[0] + port_height/2, intf_offset[1] - port_height*1.5)
            draw.text(text_pos, text, fill=text_color, font=text_font)
        
            
        len_svc = len_svc + len(s.serviceInterfaces)


        port_polygon = []
        for point in svcport_polygon:
            port_polygon.append((point[0] + offset[0], point[1] + offset[1]))
        draw.polygon(port_polygon, fill=fill_color, outline=outline_color)


        text = s.name
        text_pos = (offset[0] + port_height/2, offset[1] - port_height*1.5)
        draw.text(text_pos, text, fill=text_color, font=text_font)



    inport_polygon = ((-port_height/2-port_height/2, -port_height/2), (+port_height/2, -port_height/2),
                      (+port_height/2, +port_height/2),
                       (-port_height/2-port_height/2, port_height/2),
                      (-port_height/2-port_height/2+port_height/2, 0),
                      (-port_height/2-port_height/2, -port_height/2))
        
    for i, p in enumerate(rtcprof.inports):
        offset = (img_width/2 - rtc_width/2, top_margin + top_bottom_margin + (port_height+port_margin)*i + port_height/2)
        port_polygon = []
        for point in inport_polygon:
            port_polygon.append((point[0] + offset[0], point[1] + offset[1]))
        draw.polygon(port_polygon, fill=fill_color, outline=outline_color)

        text = p.name + '(' + p.type + ')'
        width, height = draw.textsize(text, font=text_font)
        text_pos = (offset[0] - port_height/2 - width, offset[1] - port_height*1.5)
        draw.text(text_pos, text, fill=text_color, font=text_font)
    
    return im

env = Environment(loader=FileSystemLoader('./', encoding='utf8'))
tpl = env.get_template('page_template.html')

all_posts = []    

def is_content_updated(rtcprof, content):
    title = '[RTC] ' + rtcprof.name
    editFlag = False
    post = None
    for p in all_posts:
        if p.title == title:
            editFlag = True
            post = p
            break

    if not post:
        return True
    if post.content == content:
        return False
    return True
        
def upload_image(wp, rtcprof, img_file):
    sys.stdout.write(' - Uploading Image %s\n' % rtcprof.name)
    data = {
        'name': os.path.basename(img_file),
        'type': 'image/jpeg',  # mimetype
        }
    
    with open(img_file, 'rb') as img:
        data['bits'] = xmlrpc_client.Binary(img.read())

    response = wp.call(media.UploadFile(data))
    # response == {
    #       'id': 6,
    #       'file': 'picture.jpg'
    #       'url': 'http://www.example.com/wp-content/uploads/2012/04/16/picture.jpg',
    #       'type': 'image/jpeg',
    # }
    return response

def upload_text(wp, rtcprof, html, img_info = None):
    sys.stdout.write(' - Uploading %s\n' % rtcprof.name)
    title = '[RTC] ' + rtcprof.name
    editFlag = False
    post = None

    if not is_upload():
        open(title + ".html", "w").write(html)
        return

    for p in all_posts:
        if p.title == title:
            editFlag = True
            post = p
            break
    if not editFlag:
        post = WordPressPost()
        post.title = '[RTC] ' + rtcprof.name
        post.content = html
        post.terms_names = {
            'post_tag': [rtcprof.name, 'RTC'],
            'category': ['RTComponents']
            }
        post.slug = rtcprof.name
        n = datetime.datetime.now()
        post.date = datetime.datetime(n.year, n.month, n.day, n.hour-9, n.minute, n.second)
        post.post_status = 'publish'
        post.thumbnail = img_info['id']
        post.id = wp.call(NewPost(post))
        return 
    else:
        #post = WordPressPost()
        post.title = '[RTC] ' + rtcprof.name
        post.content = html
        post.terms_names = {
            'post_tag': [rtcprof.name, 'RTC'],
            'category': ['RTComponents']
            }
        post.slug = rtcprof.name
        n = datetime.datetime.now()
        post.date = datetime.datetime(n.year, n.month, n.day, n.hour-9, n.minute, n.second)
        post.post_status = 'publish'
        post.thumbnail = img_info['id']
        wp.call(posts.EditPost(post.id, post))



def test():
    prof_path = os.path.join(wasanbon.rtm_temp(), 'rtcprofile')
    #file = 'NAO_python'
    file = 'NAO_test'
    xml_file = os.path.join(prof_path, file + '.xml')
    yaml_file = os.path.join(prof_path, file + '.yaml')
    
    try:
        rtcprof = rtcprofile.RTCProfile(xml_file)
        info = yaml.load(open(yaml_file, 'r'))
        
            #html = tpl.render({'rtc': rtcprof, 'info':info})
            #text = html.split('<!--more-->')
            #content = '<!--:en-->'+text[0]+'<!--:--><!--:ja-->'+text[0]+'<!--:-->' + \
            #'<!--more-->' + '<!--:en-->'+text[1]+'<!--:--><!--:ja-->'+text[1]+'<!--:-->'
            
            #upload_text(wp, rtcprof, content)
            # Debug
        im = create_image(rtcprof)
        im.show()
        im.save(file + '.jpg')
        return
    except:
        traceback.print_exc()


def main():

    if setting_filename in os.listdir(os.getcwd()):
        setting = yaml.load(open(setting_filename, 'r'))
        user = setting['user']
        passwd = setting['passwd']
        url = setting['url']
    else:
        print 'User:', 
        user = raw_input()
        print 'Pass:',
        passwd = raw_input()
        print 'URL :',
        url = raw_input()
        if url.endswith('/'):
            url = url[0:-1]

    wp = Client(url + '/xmlrpc.php', user, passwd)
    global all_posts
    offset = 0
    increment = 20
    sys.stdout.write(' - Loading All Posts...\n')
    while True:
        my_posts = wp.call(posts.GetPosts({'number': increment, 'offset': offset}))
        if len(my_posts) == 0:
                break  # no more posts returned
        all_posts = all_posts + my_posts
        offset = offset + increment
    sys.stdout.write(' - OK.\n')

    prof_path = os.path.join(wasanbon.rtm_temp(), 'rtcprofile')
    for file in [f[0:-4] for f in os.listdir(prof_path) if f.endswith('.xml')]:
        if is_test():
            if not file == test_name:
                continue
        sys.stdout.write(' - Checking RTC.%s\n' % file)
        xml_file = os.path.join(prof_path, file + '.xml')
        yaml_file = os.path.join(prof_path, file + '.yaml')
        img_file = os.path.join(prof_path, file + '.jpg')
        try:
            rtcprof = rtcprofile.RTCProfile(xml_file)
            info = yaml.load(open(yaml_file, 'r'))
            html = tpl.render({'rtc': rtcprof, 'info':info})
            text = html.split('<!--more-->')
            content = '<!--:en-->'+text[0]+'<!--:--><!--:ja-->'+text[0]+'<!--:-->' + \
            '<!--more-->' + '<!--:en-->'+text[1]+'<!--:--><!--:ja-->'+text[1]+'<!--:-->'

            if is_content_updated(rtcprof, content) or is_test():
                im = create_image(rtcprof)
                if os.path.isfile(img_file):
                    os.rename(img_file, img_file + wasanbon.timestampstr())
                im.save(img_file)
                
                response = upload_image(wp, rtcprof, img_file)
            
                upload_text(wp, rtcprof, content, response)

        except:
            traceback.print_exc()
        
    return



if __name__ == '__main__':
    main()
    #test()
