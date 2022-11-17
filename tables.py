import time
from typing import Sequence
from handlers import get_config, get_users_handler
from types_def import *
import gspread
import constants


__all__ = ['get_dds_list', 'get_payment_types']


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


def _update_dds_list():
    dds_info = _scan_table_values('dds', DDSInfo._fields)
    res_info = tuple(DDSInfo(dds, dds_info['type'][i], dds_info['pl'][i])
                     for i, dds in enumerate(dds_info['dds']) if dds)

    conf = get_config()
    conf.save_data('dds_types', res_info)


def _update_users_access():
    u_info = _scan_table_values('logins', ['username', 'userid', None, 'access'])
    users = [UserInfo(user, u_info['userid'][i], u_info['access'])
             for i, user in enumerate(u_info['username']) if user]
    get_users_handler().update_users_list(users)


def _update_payment_types():
    p_info = _scan_table_values('payment_types', ['value'])
    types = tuple(PaymentTypeInfo(v) for v in p_info['value'])
    get_config().save_data('payment_types', types)


def _update_spreadsheets():
    _update_dds_list()
    _update_users_access()
    _update_payment_types()


def _autoupdate():
    cf = get_config()
    if ((lu := cf.get_saved_data('last_spreadsheet_update')) is None
            or time.time() - lu > constants.EXCEL_UPDATE_INTERVAL):
        _update_spreadsheets()
        cf.save_data('last_spreadsheet_update', time.time())


def get_dds_list() -> tuple[DDSInfo]:
    _autoupdate()
    return get_config().get_saved_data('dds_types')


def get_payment_types() -> tuple[PaymentTypeInfo]:
    _autoupdate()
    return get_config().get_saved_data('payment_types')
