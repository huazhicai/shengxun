# -*- coding: utf-8 -*- 
''' 
Created on 2012-12-17
@author: walfred 
@module: XLRDPkg.write_append 
@description: 
'''
import os
from xlutils.copy import copy
import xlrd as ExcelRead


def write_append(file_name):
    values = ["Ann", "woman", 22, "UK", u"我靠"]

    r_xls = ExcelRead.open_workbook(file_name)
    r_sheet = r_xls.sheet_by_index(0)
    rows = r_sheet.nrows  # 取源文件行
    w_xls = copy(r_xls)
    sheet_write = w_xls.get_sheet(0)
    print(rows, r_sheet, sheet_write)
    for i in range(0, len(values)):
        sheet_write.write(rows, i, values[i])

    w_xls.save(file_name + '.out' + os.path.splitext(file_name)[-1])


if __name__ == "__main__":
    write_append("./test.xls")
