# -*- coding: utf-8 -*-
# @Author: cai bao
# @Email: lucaibao@houselai.com
# @Time: 2022/5/17
import random
import re
import xlwt
import datetime


class Tool(object):
    @staticmethod
    def random_str(length=32):
        """
        生成32位随机字符串
        :return :32位随机字符串
        """
        chars = 'abcdefghijklmnopqrstuvwxyz0123456789'
        rand = random.Random()
        return "".join([chars[rand.randint(0, len(chars) - 1)] for i in range(length)])

    @staticmethod
    def verify_phone(phone):
        """
        验证手机号格式是否正确
        """
        return re.match("^1[345789][0-9]{9}$", phone)

    @staticmethod
    def excel(header="", title=None, data=None):
        workbook = xlwt.Workbook(encoding='utf-8')
        worksheet = workbook.add_sheet("Sheet1")

        style = xlwt.XFStyle()
        style2 = xlwt.XFStyle()
        style3 = xlwt.XFStyle()

        # 设置header背景颜色
        pattern = xlwt.Pattern()
        # 设置背景颜色的模式
        pattern.pattern = xlwt.Pattern.SOLID_PATTERN
        # 背景颜色
        pattern.pattern_fore_colour = 5
        style.pattern = pattern

        # 设置title背景颜色
        pattern2 = xlwt.Pattern()
        # 设置背景颜色的模式
        pattern2.pattern = xlwt.Pattern.SOLID_PATTERN
        # 背景颜色
        pattern2.pattern_fore_colour = 50
        style2.pattern = pattern2

        # 设置字体
        font = xlwt.Font()
        # 字体类型
        font.name = "Arial"
        # 字体加粗
        font.bold = True
        # 下划线
        # font.underline = True
        # 斜体字
        # font.italic = True
        # 设置字体大小，11为字号，20为衡量单位
        font.height = 20 * 20
        style.font = font

        al = xlwt.Alignment()
        # horz属性代表水平对齐方式 0x01左对齐,0x02居中,0x03右对齐
        al.horz = 0x02
        # vert属性代表垂直对齐方式 0x00上对齐,0x01居中,0x02底对齐
        al.vert = 0x01
        # 设置自动换行
        al.wrap = 1
        style.alignment = al
        style2.alignment = al
        style3.alignment = al

        # 设置行高，20为基准数
        worksheet.row(0).height_mismatch = True
        worksheet.row(0).height = 20 * 30
        worksheet.row(1).height = 20 * 40

        # 设置列宽,256为基准数
        worksheet.col(0).width = 256 * 15
        worksheet.col(1).width = 256 * 15
        worksheet.col(2).width = 256 * 15
        worksheet.col(3).width = 256 * 35
        worksheet.col(4).width = 256 * 35
        worksheet.col(5).width = 256 * 25
        worksheet.col(6).width = 256 * 20
        worksheet.col(7).width = 256 * 20

        worksheet.write_merge(0, 0, 0, len(title) - 1, header, style)
        for i in range(len(title)):
            worksheet.write(1, i, title[i], style2)

        for i in range(len(data)):
            for j in range(len(data[i])):
                if isinstance(data[i][j], datetime.datetime):
                    worksheet.write(i + 2, j, data[i][j].strftime("%Y-%m-%d %H:%M:%S"), style3)
                else:
                    worksheet.write(i + 2, j, data[i][j], style3)

        return workbook
