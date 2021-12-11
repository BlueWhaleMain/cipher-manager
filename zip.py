# -*- coding: gb2312 -*-
# Copyright by BlueWhale. All Rights Reserved.
"""
zipѹ��
"""
import getopt
import os
import sys
import time
import zipfile


def get_zip_file(input_path, result):
    """
    ��Ŀ¼����������ȱ���
    :param input_path:
    :param result:
    :return:
    """
    try:
        for file in os.listdir(input_path):
            if os.path.isdir(input_path + '/' + file):
                result.append(input_path + '/' + file)
                # ������Ŀ¼
                get_zip_file(input_path + '/' + file, result)
            else:
                result.append(input_path + '/' + file)
    except NotADirectoryError as ex:
        print(ex.filename, ex.strerror)
        sys.exit(2)


def zip_file_path(input_path, output_path, output_name, compress_level=None):
    """
    ѹ���ļ�
    :param compress_level: ѹ���ȼ�
    :param input_path: ѹ�����ļ���·��
    :param output_path: ��ѹ���������·��
    :param output_name: ѹ��������
    :return:
    """
    f = zipfile.ZipFile(output_path + '/' + output_name, 'w', zipfile.ZIP_DEFLATED, compresslevel=compress_level)
    file_list = []
    get_zip_file(input_path, file_list)
    before_size = 0
    file_count = len(file_list)
    file_index = 0
    while file_index < file_count:
        file = file_list[file_index]
        before_size += os.path.getsize(file)
        arc_name = file[len(input_path):]
        # ����ļ���������·��
        f.write(file, arc_name)
        sys.stdout.write(str(int((file_index / file_count) * 100)) + "%\r")
        sys.stdout.flush()
        file_index += 1
    f.close()
    after_size = os.path.getsize(output_path + '/' + output_name)
    if before_size != 0:
        print("Դ�ļ��ܴ�С��", before_size, "ѹ�����С��", after_size, "ѹ���ʣ�", after_size / before_size * 100, "%")
    else:
        print("�ļ��ܴ�СΪ0")
    return len(file_list)


def main(argv):
    """

    :param argv:
    """
    err_msg = 'zip.py -i <input_path> -o <output_path> -n <output_name> [-l <compress_level>]'
    input_path = ''
    output_path = ''
    output_name = ''
    compress_level = None
    try:
        opts, args = getopt.getopt(argv, "hi:o:n:l:",
                                   ["input_path=", "output_path=", "output_name=", "compress_level="])
        if len(argv) < 6:
            print(err_msg)
            sys.exit(2)
    except getopt.GetoptError as e:
        print(e.msg)
        sys.exit(2)
    before = time.time()
    for opt, arg in opts:
        if opt == '-h':
            print(err_msg)
            sys.exit()
        elif opt in ("-i", "--input_path"):
            if arg == "":
                print("Ŀ��·������Ϊ�գ�")
                sys.exit(2)
            input_path = arg
        elif opt in ("-o", "--output_path"):
            if arg == "":
                print("���·������Ϊ�գ�")
                sys.exit(2)
            output_path = arg
        elif opt in ("-n", "--output_name"):
            if arg == "":
                print("����ļ�������Ϊ�գ�")
                sys.exit(2)
            output_name = arg
        elif opt in ("-l", "--compress_level"):
            if not arg == "":
                try:
                    compress_level = int(arg)
                except ValueError:
                    compress_level = arg
    r = zip_file_path(input_path, output_path, output_name, compress_level)
    print("���ѹ��������", r, "����Ŀ", "\r\n����ļ���", output_path + '/' + output_name, "��ʱ��", time_escape(time.time() - before))


def time_escape(t: float = 0, iteration: bool = False) -> str:
    """
    ����ʱ�䣨�룩תΪ�ַ���
    :param t:ʱ�䳤��
    :param iteration:�Ƿ�Ϊ����
    :return:�ַ���
    """
    if t < 1:
        if t > 0:
            return f"{int(t * 1000)}����"
        elif t == 0:
            if iteration is True:
                return "0��"
            else:
                return "��ǰ"
        else:
            return f"��ȥʱ�䣺{time_escape(-t)}"
    elif t < 60:
        return f"{int(t)}��"
    elif t < 3600:
        return f"{int(t / 60)}��{time_escape(t % 60, True)}"
    elif t < 86400:
        return f"{int(t / 3600)}ʱ{time_escape(t % 3600, True)}"
    else:
        return f"{int(t / 86400)}��{time_escape(t % 86400, True)}"


if __name__ == "__main__":
    main(sys.argv[1:])
