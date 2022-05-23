# -*- coding: utf-8 -*-
# @Author: cai bao
# @Email: lucaibao@houselai.com
# @Time: 2022/5/17
import random
import re
import string


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
    def verify_name(name):
        """
        校验用户真实姓名(纯中文或者纯英文)
        """
        if name.isalpha():  # 如果字符串至少有一个字符并且所有字符都是字母或文字则返回 True，否则返回 False。
            for i in name:
                print(i)
                if not '\u4e00' <= i <= '\u9fa5':
                    print("11111111")
                    return False
                elif i not in string.ascii_lowercase+string.ascii_uppercase:
                    print("22222222222")
                    return False
            return True
        else:
            return False


if __name__ == "__main__":
    s = "卢才把"
    res = Tool.verify_name(name=s)
    print(res)