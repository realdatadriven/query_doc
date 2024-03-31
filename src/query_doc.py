"""A small package that allows you to break your query in manageable chunks (normally fields),
allowing you to focus on building each variable / field independently,
with notes / documentation and at the end cam be compiled to a single gigantic query string
that otherwise would be impossible to manage or maintain"""
import os
import re
from dataclasses import dataclass, asdict
from typing import Optional
import copy

@dataclass
class Field:
    """Query field or variable"""
    name: str = None
    desc: Optional[str] = None
    select: str = None
    from_: Optional[str] = None
    join: Optional[str] = None
    where: Optional[str] = None
    group_by: Optional[str] = None
    order_by: Optional[str] = None
    having: Optional[str] = None
    window: Optional[str] = None
    extras: Optional[dict] = None
    active: bool = True
    def get_dict(self) -> dict:
        '''returns the field in the dict format'''
        return {k: v for k, v in asdict(self).items()}

class QueryDoc():
    """A small package that allows you to break your query in manageable chunks (normally fields),
    allowing you to focus on building each variable / field independently,
    with notes / documentation and at the end cam be compiled to a single gigantic query string
    that otherwise would be impossible to manage or maintain"""
    def __init__(self, query_parts: dict):
        self.query_parts = query_parts if query_parts else {}
    def field(self, args: Optional[dict] = None) -> Field:
        """Query field or variable"""
        _field = Field()
        if args:
            _field = Field(**args)
        return _field
    def add_field(self, _field: Field):
        '''Add field to the main query parts dict'''
        if not _field.name:
            print('Field.name is required')
        elif not _field.select:
            print('Field.select is required')
        else:
            self.query_parts[_field.name] = _field.get_dict()
        return self
    def remove_fields(self, name: str):
        '''Remove field to the main query parts dict'''
        try:
            del self.query_parts[name]
        except KeyError as _err:
            print(str(_err))
        return self
    def get_query_parts(self) -> dict:
        '''return the query parts object'''
        return dict(self.query_parts)
    def get_query_sql(self, _parts: Optional[dict]) -> str:
        '''generate the query string form the parts'''
        if not _parts:
            _parts = copy.deepcopy(dict(self.query_parts))
        elif not isinstance(_parts, dict):
            _parts = copy.deepcopy(dict(self.query_parts))
        elif len(_parts) == 0:
            _parts = copy.deepcopy(dict(self.query_parts))
        _query = Field().get_dict()
        _pieces = Field().get_dict().keys()
        for field in _parts:
            patt = re.compile(r'@\w+', re.IGNORECASE) # PATTERN TO FIND REFERENCED FIELDS (@FIELDS)
            _select = copy.deepcopy(_parts[field].get('select'))
            _join   = copy.deepcopy(_parts[field].get('join'))
            _where  = copy.deepcopy(_parts[field].get('where'))
            _group  = copy.deepcopy(_parts[field].get('group_by'))
            _order  = copy.deepcopy(_parts[field].get('order_by'))
            _window = copy.deepcopy(_parts[field].get('window'))
            _having = copy.deepcopy(_parts[field].get('having'))
            _str = f'{_select}{_join}{_where}{_group}{_window}{_order}{_having}'
            _ref_fields = re.findall(patt, _str)
            _sql_pieces_list = [
                'select',
                'join',
                'where',
                'group_by',
                'order_by',
                'window',
                'having'
            ]
            for _ref_field in _ref_fields:
                _ref_field = _ref_field.replace('@', '')
                if  not _parts.get(_ref_field):
                    continue
                _ref_field_sql = copy.deepcopy(_parts[_ref_field].get('select'))
                patts = [
                    re.compile(r'\n'),
                    re.compile(r'\t'),
                    re.compile(r'\s\s+'),
                    re.compile(r'^\W?\,')
                ]
                for patt in patts:
                    _ref_field_sql = re.sub(patt, ' ', _ref_field_sql)
                patt = re.compile(r'^,?\W{0,}?.{0,}?\(\W{0,}.{0,}SELECT.+', re.IGNORECASE)
                if len(re.findall(patt, _ref_field_sql)) == 0:
                    patt = re.compile(r'^(\W+)?SELECT\s?', re.IGNORECASE)
                    _ref_field_sql = re.sub(patt, ' ', _ref_field_sql)
                patt = re.compile(r'\s+(AS)?\s+[\"]?' + _ref_field + r'[\"]?\W', re.IGNORECASE)
                _ref_field_sql = re.sub(patt, ' ', _ref_field_sql)
                patt = re.compile(r'@\b' + _ref_field + r'\b', re.IGNORECASE)
                for _piece in _pieces:
                    if _piece not in _sql_pieces_list:
                        continue
                    if not _parts[field].get(_piece):
                        continue
                    _piece_sql = copy.deepcopy(_parts[field].get(_piece))
                    _piece_sql = re.sub(patt, f"({_ref_field_sql})", _piece_sql)
                    _parts[field][_piece] = copy.deepcopy(_piece_sql)
            for _piece in _pieces:
                _sql_pieces_list.append('from_')
                if _piece not in _sql_pieces_list:
                    continue
                if not _query.get(_piece):
                    _query[_piece] = ''
                if not _parts[field].get(_piece) or not _parts[field].get('active'):
                    continue
                _query[_piece] += _parts[field].get(_piece)
        return f"""{
            _query['select']}{
            _query['from_']}{
            _query['join']}{
            _query['where']}{
            _query['group_by']}{
            _query['window']}{
            _query['order_by']}{
            _query['having']
        }"""
    def set_date(self, sql: str, dates: list) -> str:
        '''puts de date in the placeholder "FIELD_NAME" = '{YYYY-MM-DD}' '''
        patt = re.compile(
            r"([\"]?\w+[\"]?\.[\"]?\w+[\"]?\s{0,}=\s{0,}'\{.*?\}'|[\"]?\w+[\"]?\s{0,}=\s{0,}'\{.*?\}')",
            re.IGNORECASE
        )
        matchs = re.findall(patt, sql)
        if not matchs:
            patt = re.compile(r"[\"]?\w+[\"]?\s{0,}=\s{0,}'\{.*?\}'", re.IGNORECASE)
            matchs = re.findall(patt, sql)
        elif len(matchs) == 0:
            patt = re.compile(r"[\"]?\w+[\"]?\s{0,}=\s{0,}'\{.*?\}'", re.IGNORECASE)
            matchs = re.findall(patt, sql)
        if len(matchs) > 0:
            patt2 = re.compile(r"'\{.*?\}'", re.IGNORECASE)
            for _m in matchs:
                frmt = re.findall(patt2, _m)
                if len(frmt) > 0:
                    dt_format_final = frmt[0].replace('YYYY','%Y') #FULL YEAR
                    dt_format_final = dt_format_final.replace('YY','%y') #YY YEAR
                    dt_format_final = dt_format_final.replace('MM','%m') #MONTH YEAR
                    dt_format_final = dt_format_final.replace('DD','%d') #DAY YEAR
                    dt_format_final = dt_format_final.replace('{','').replace('}','')
                    if isinstance(dates, list):
                        dts = ','.join([
                            f'{dt.strftime(dt_format_final)}' for dt in copy.deepcopy(dates)
                        ])
                        procc = re.sub(patt2, f'({dts})', _m)
                        patt3 = re.compile(r"\s?=\s?", re.IGNORECASE)
                        procc = re.sub(patt3, ' IN ', procc)
                    else:
                        procc = re.sub(patt2, dates.strftime(dt_format_final), _m)
                    patt =  re.compile(r'(' + _m + ')', re.IGNORECASE)
                    sql = re.sub(patt, procc, sql)
        patt = re.compile(r"'?\{.*?\}'?", re.IGNORECASE)
        matchs = re.findall(patt, sql)
        patt_dts = re.compile(
            r'YYYY.?MM.?DD|AAAA.?MM.?DD|YY.?MM.?DD|AA.?MM.?DD|YYYY.?MM|AAAA.?MM|YY.?MM|AA.?MM|MM.?DD',
            re.IGNORECASE
        )
        if len(matchs) > 0:
            for _m in matchs:
                frmt = _m
                if len(re.findall(patt_dts, frmt)) == 0:
                    continue
                dt_format_final = frmt.replace('YYYY','%Y') #FULL YEAR
                dt_format_final = dt_format_final.replace('YY','%y') #YY YEAR
                dt_format_final = dt_format_final.replace('YY','%y') #YY YEAR
                dt_format_final = dt_format_final.replace('AAAA','%Y') #FULL YEAR
                dt_format_final = dt_format_final.replace('AA','%y') #YY YEAR
                dt_format_final = dt_format_final.replace('MM','%m') #MONTH YEAR
                dt_format_final = dt_format_final.replace('DD','%d') #DAY YEAR
                dt_format_final = dt_format_final.replace('{','').replace('}','')
                if isinstance(dates, list):
                    procc = re.sub(patt, dates[0].strftime(dt_format_final), _m)
                else:
                    procc = re.sub(patt, dates.strftime(dt_format_final), _m)
                try:
                    patt =  re.compile(r'(' + _m + ')', re.IGNORECASE)
                    sql = re.sub(patt, procc, sql)
                except Exception as _err:
                    pass
        matchs = re.findall(patt_dts, sql)
        if len(matchs) > 0:
            for _m in matchs:
                frmt = _m
                dt_format_final = frmt.replace('YYYY','%Y') #FULL YEAR
                dt_format_final = dt_format_final.replace('YY','%y') #YY YEAR
                dt_format_final = dt_format_final.replace('YY','%y') #YY YEAR
                dt_format_final = dt_format_final.replace('AAAA','%Y') #FULL YEAR
                dt_format_final = dt_format_final.replace('AA','%y') #YY YEAR
                dt_format_final = dt_format_final.replace('MM','%m') #MONTH YEAR
                dt_format_final = dt_format_final.replace('DD','%d') #DAY YEAR
                if isinstance(dates, list):
                    procc = re.sub(patt, dates[0].strftime(dt_format_final), _m)
                else:
                    procc = re.sub(patt, dates.strftime(dt_format_final), _m)
                patt =  re.compile(r'(' + _m + ')', re.IGNORECASE)
                sql = re.sub(patt, procc, sql)
        return sql
    def set_str_env(self, _str: str) -> str:
        '''Set / replace environmental variable @ENV.NAME to real value in os.environ'''
        _patt = re.compile(r'@ENV\.\w+', re.I)
        _matchs = re.findall(_patt, _str)
        if len(_matchs) > 0:
            for _env in _matchs:
                _environ = re.sub(r'@ENV\.', '', str(_env))
                try:
                    _str = re.sub(_env, os.environ.get(_environ), _str)
                except Exception as _err:# pylint: disable=broad-exception-caught
                    pass
        return _str
