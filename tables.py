from typing import Sequence
from config import get_config
from collections import namedtuple
import gspread
import constants


__all__ = ['DDSInfo', 'update_dds_list']


DDSInfo = namedtuple('DDSInfo', 'dds type pl payment')


_gservice = gspread.service_account(filename=str(constants.AUTH_KEY))
_spreadsheets: dict[str, gspread.Spreadsheet] = \
    {n: _gservice.open_by_url(url) for n, url in get_config().get_spreadsheets_list()}


def _scan_table_values(tag: str, headers: Sequence[str]):
    info = get_config().get_spreadsheet_tag_info(tag)
    sheet = _spreadsheets[info['spreadsheet']].worksheet(info['worksheet'])
    start = info['start']
    length = len(sheet.col_values(start[1])[start[0] - 1:])
    v_range = [i for i in sheet.range(start[0], start[1], start[0] + length - 1, start[1] + len(headers) - 1)]
    return {r_name: [c.value for c in v_range[i::len(headers)]]
            for i, r_name in enumerate(headers) if r_name is not None}


def update_dds_list():
    dds_info = _scan_table_values('dds', DDSInfo._fields)
    res_info = tuple(DDSInfo(dds, dds_info['type'][i], dds_info['pl'][i], dds_info['payment'][i])
                     for i, dds in enumerate(dds_info['dds']) if dds)

    conf = get_config()
    conf.save_data('dds_types', res_info)