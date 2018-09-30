"""This file contains org parser and analyser
"""
import json
from datetime import datetime, timedelta
import pandas as pd
from orgparse import load


def item2dict(item):
    """
    convert org node to dict
    """
    try:
        result = {
            "name": item.heading,
            "tag": list(item.tags)[0],
            "start_time": item.clock[0].start,
            "end_time": item.clock[0].end,
            "duration": item.clock[0].duration
        }
        return result
    except Exception as e:
        """
        find out which one is wrong
        """
        print(item)
        print(e)


def org2df(root):
    """
    convert org root node to pandas dataframe
    """
    days = root.children
    item_nodes = []
    for day in days:
        item_nodes += day.children
    return pd.DataFrame([item2dict(item) for item in item_nodes])[[
        'name', 'duration', 'start_time', 'end_time', 'tag'
    ]]


def org_path2df(path: str) -> pd.DataFrame:
    """
    convert path of org file to pandas dataframe
    """
    root = load(path)
    df = org2df(root)
    return df


def get_record_df() -> pd.DataFrame:
    """
    get record pandas dataframe from org path
    """
    org_df = get_org_df()
    record_df = org_df2record_df(org_df)
    return record_df


def get_org_df() -> pd.DataFrame:
    """
    get org pandas dataframe from org path
    """
    org_path = "/home/mark/code/org_time_record/2018.org"
    org_df = org_path2df(org_path)
    return org_df


def org_df2record_df(org_df: pd.DataFrame) -> pd.DataFrame:
    """
    convert org dataframe to record df per minute
    """
    result = pd.DataFrame()
    index_list = list(org_df.index)
    for index in index_list:
        record = org_df.iloc[index]
        range_index = pd.date_range(
            start=record.start_time, end=record.end_time, freq='T')
        tmp = pd.DataFrame([{
            'name': record['name'],
            'tag': record['tag']
        } for i in range(len(range_index))],
                           index=range_index)
        result = result.append(tmp)
    return result


def get_this_week(df: pd.DataFrame, now: DateTime):
    """
    get dataframe start_time >= one week ago and end_time <= now
    """
    now = now.replace(hour=23, minute=59, second=59)
    one_week_ago = now - timedelta(weeks=1)
    df = df[(df.index <= now) & (df.index >= one_week_ago)]
    return df


def get_this_day(df: pd.DataFrame, now: DateTime) -> pd.DataFrame:
    """
    get dataframe start_time >= one week ago and end_time <= now
    """
    now = now.replace(hour=23, minute=59, second=59)
    yesterday = now - timedelta(days=1)
    df = df[(df.index <= now) & (df.index >= yesterday)]
    return df


def get_name_time_in_df(df: pd.DataFrame, name: str) -> pd.Series:
    return df[df['name'].apply(lambda x: name in x)]['name'].resample(
        'D').count() / 60


def main():
    record_df = get_record_df()
    # get today's datetime
    now = datetime.now()
    # get this week record
    this_week = get_this_week(record_df, now)
    today = get_this_day(record_df, now)
    print(this_week)
    return record_df


if __name__ == '__main__':
    main()
