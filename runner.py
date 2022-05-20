import time
import os
import pandas as pd


def job():
    os.system('python cleanenergy.py')
    time.sleep(10)
    os.system('python insideev.py')
    data = pd.read_excel('clean.xlsx', sheet_name="Sheet")
    data1 = pd.read_excel('InsideEv.xlsx', sheet_name="Sheet")
    full_data = pd.concat([data, data1], axis=0)
    full_data.to_excel('posts.xlsx', sheet_name='Sheet', index=False)
    return


if __name__ == '__main__':
    job()
