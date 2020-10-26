import itchat,os,math
from PIL import Image

import numpy as np
import matplotlib.pyplot as plt

import jieba
from wordcloud import WordCloud

class Wechat_Photo_Wall(object):

    def __init__(self):
        # 存放所有的个性签名
        self.signature_txt = ''

    def get_wechat(self):
        try:
            # 登录微信,  hotReload=True:持续登录，无需扫码，手机点击登录即可
            # itchat.auto_login(hotReload=True)
            # 扫码登录
            itchat.auto_login()
        except:
            print("请检查网络，再重试")
        # 获取微信好友
        friends = itchat.get_friends(update=True)
        # 创建photo_image文件夹来保存微信头像图片
        if not os.path.exists('photo_image'):
            # 若文件夹不存在，则创建目录
            os.mkdir('photo_image')
        num=0
        for friend in friends:
            # 根据用户名获取对应的微信头像
            img=itchat.get_head_img(userName=friend['UserName'])
            # 图片路径名
            img_name=''.join(['photo_image/img',str(num),'.jpg'])
            # 保存图片
            with open(img_name,'wb') as f:
                f.write(img)
            num+=1

            # 获取生成词云需要的所有好友的个性签名
            signature=friend['Signature'].strip()
            # 剔除个性签名为空以及含span标签的，将所有签名通过空格拼成字符串
            if len(signature)>0 and not '<span class=' in signature:
                self.signature_txt+=signature+' '

        self.merge_image()
        self.merge_love_image()
        self.draw_heart_shape()
        self.get_wordcloud()


    # 拼接，生成照片墙
    def merge_image(self):
        # 获取指定路径下的文件列表
        all_image=os.listdir('photo_image')
        # 设定每个头像的大小
        each_size=int(math.sqrt(float(1024*1024)/len(all_image)))
        # 照片墙的行数
        lines=int(1024/each_size)
        print(lines)
        # 创建Image对象，初始化大小
        image=Image.new('RGBA',(1024,1024))
        x,y=0,0
        for i in range(len(all_image)):
            try:
                img = Image.open(''.join(['photo_image/img', str(i), '.jpg']))
                # 重新设置图像大小
                img = img.resize((each_size, each_size), Image.ANTIALIAS)
                # 根据x,y坐标位置拼接图像
                image.paste(img, (x * each_size, y * each_size))
                # 更新下一张图像位置
                x += 1
            except:
                pass
            finally:
                # 一行一行拼接
                if x == lines:
                    x = 0
                    y += 1

        # 保存生成的照片墙
        # RGBA意思是红色，绿色，蓝色，Alpha的色彩空间，Alpha指透明度。而JPG不支持透明度，所以要么丢弃Alpha,要么保存为.png文件
        image.save('photo_image/photo_wall.png')
        itchat.send_msg('好友头像照片墙', 'filehelper')
        # 发送图像到微信文件传输助手，打开手机微信可查看
        itchat.send_image('photo_image/photo_wall.png','filehelper')

    # 拼接为心形照片墙
    def merge_love_image(self):
        # 获取指定路径下的文件列表
        all_image=os.listdir('photo_image')
        # 设定每个头像的大小
        each_size=int(math.sqrt(float(1024*1024)/len(all_image)))

        # 一行的图像个数,若为偶数个，则+1转换为奇数个，修改每个图像的大小，使最后的心形对称好看
        num=int(1024/each_size)
        if num%2==0:
            num+=1
        each_size=int(1024/num)

        # 照片墙的行数
        lines=int(1024/each_size)
        print(lines)
        # 创建Image对象，初始化大小,其大小不直接设定为（1024*1024），因为照片拼接出的尺寸不是正好等于1024，故用实际拼接的尺寸
        image=Image.new('RGBA',(lines*each_size,lines*each_size))
        x,y=0,0
        for i in range(len(all_image)):
            try:
                # 由于图像坐标从（0，0）开始，而心形函数对应左上角坐标为（-512，512），故此在判断坐标时，稍作转换
                is_heart_part=self.get_heart_shape(-512+x * each_size,512-y * each_size)
                if not is_heart_part:
                    pass
                else:
                    img = Image.open(''.join(['photo_image/img', str(i), '.jpg']))
                    # 重新设置图像大小
                    img = img.resize((each_size, each_size), Image.ANTIALIAS)
                    # 根据x,y坐标位置拼接图像
                    image.paste(img, (x * each_size, y * each_size))
                # 更新下一张图像位置
                x += 1
            except:
                pass
            finally:
                # 一行一行拼接
                if x == lines:
                    x = 0
                    y += 1

        # 保存生成的照片墙
        # RGBA意思是红色，绿色，蓝色，Alpha的色彩空间，Alpha指透明度。而JPG不支持透明度，所以要么丢弃Alpha,要么保存为.png文件
        image.save('photo_image/photo_wall.png')
        itchat.send_msg('心形照片墙', 'filehelper')
        # 发送图像到微信文件传输助手，打开手机微信可查看
        itchat.send_image('photo_image/photo_wall.png','filehelper')

    # 画心形
    @classmethod
    def draw_heart_shape(cls):
        x=np.linspace(-512,512,1024)
        y1=0.618*np.abs(x)-0.7*np.sqrt(262144-x**2)
        y2 = 0.618 * np.abs(x) + 0.7 * np.sqrt(262144 - x ** 2)
        plt.plot(x,y1,color='r')
        plt.plot(x, y2, color='b')
        plt.show()

    # 计算心形，判断图像的坐标是否在心形函数内
    @classmethod
    def get_heart_shape(cls,x,y):
        y1 = 0.618 * np.abs(x) - 0.7 * np.sqrt(262144 - x ** 2)
        y2 = 0.618 * np.abs(x) + 0.7 * np.sqrt(262144 - x ** 2)
        if y<y1 or y>y2:
            return False
        else:
            return True

    # 生成词云
    def get_wordcloud(self):
        try:
            image = np.array(Image.open('./namei.jpeg'))
            # jieba分词
            signature_txt_list = jieba.cut(self.signature_txt, cut_all=False)
            jieba_txt = ' '.join(signature_txt_list)
            # 生成词云
            wordcloud = WordCloud(font_path=r'C:\Windows\Fonts\msyh.ttc',  # 调用系统自带字体(微软雅黑)
                                  background_color='white',  # 背景色
                                  max_words=500,  # 最大显示单词数
                                  max_font_size=60,  # 频率最大单词字体大小
                                  mask=image  # 自定义显示的效果图
                                  ).generate(jieba_txt)
            plt.imshow(wordcloud, interpolation='bilinear')
            plt.axis('off')
            plt.show()
            # 保存为图片
            wordcloud.to_file('./signature_wordcloud.png')
            itchat.send_msg('好友个性签名词云', 'filehelper')
            # tips: 发送的图片名称必须为英文，若为中文，会发送失败
            itchat.send_image('signature_wordcloud.png', 'filehelper')
        except:
            print('词云生成失败，请重试')

if __name__ == '__main__':
    Wechat_Photo_Wall().get_wechat()

