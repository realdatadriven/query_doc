# Query Doc Package

A small package that allows you to break your query in manageable chunks (normally fields), allowing you to focus on building each variable / field independently, with notes / documentation and at the end cam be compiled to a single gigantic query string that otherwise would be impossible to manage or maintain


```python
from query_doc import QueryDoc
```

# Instantiate


```python
qd = QueryDoc({})
```

# ADD FIELDS

## FIELD A


```python
_field = qd.field()
_field.name = 'FieldA'
_field.desc = 'FieldA description'
_select = f"""SELECT "TABLE_A"."FILED_A" AS "{_field.name}"\n"""
_field.select = _select
_field.from_ = f"""FROM "TABLE_A"\n"""
_where = f"""WHERE "TABLE_A"."COND_FIELD_A" IS NOT NULL 
    AND "TABLE_A"."DATE_FIELD" = '{{YYYY-MM-DD}}'\n"""
_field.where = _where
qd.add_field(_field)
```

## FIELD B


```python
_field = qd.field()
_field.name = 'FieldB'
_field.desc = 'FieldB description'
_select = f"""    , "TABLE_B"."FILED_B" AS "{_field.name}"\n"""
_join = f"""LEFT OUTER JOIN (
    SELECT *
    FROM "TABLE_B"
) AS "TABLE_B" ON (
    "TABLE_B"."FK_FROM_A" = "TABLE_A"."KEY_FIELD"
    AND "TABLE_B"."DATE_FIELD" = "TABLE_A"."DATE_FIELD"
)\n"""
_field.select = _select
_field.join = _join
qd.add_field(_field)
```

## CONCAT FIELD A & B


```python
_field = qd.field()
_field.name = 'FieldA+FieldB'
_field.desc = 'FieldA Concat FieldB description'
_select = f"""    , (COALESCE(@FieldA, '') || COALESCE(@FieldB, '')) AS "{_field.name}"\n"""
_field.select = _select
qd.add_field(_field)
```

# GET QUERY PARTS DICT


```python
query_parts = qd.get_query_parts()
print(query_parts)
```
```py

    {'FieldA': {'name': 'FieldA', 'desc': 'FieldA description', 'select': 'SELECT "TABLE_A"."FILED_A" AS "FieldA"\n', 'from_': 'FROM "TABLE_A"\n', 'join': None, 'where': 'WHERE "TABLE_A"."COND_FIELD_A" IS NOT NULL \n    AND "TABLE_A"."DATE_FIELD" = \'{YYYY-MM-DD}\'\n', 'group_by': None, 'order_by': None, 'having': None, 'window': None, 'extras': None, 'active': True}, 'FieldB': {'name': 'FieldB', 'desc': 'FieldB description', 'select': '    , "TABLE_B"."FILED_B" AS "FieldB"\n', 'from_': None, 'join': 'LEFT OUTER JOIN (\n    SELECT *\n    FROM "TABLE_B"\n) AS "TABLE_B" ON (\n    "TABLE_B"."FK_FROM_A" = "TABLE_A"."KEY_FIELD"\n    AND "TABLE_B"."DATE_FIELD" = "TABLE_A"."DATE_FIELD"\n)\n', 'where': None, 'group_by': None, 'order_by': None, 'having': None, 'window': None, 'extras': None, 'active': True}, 'FieldA+FieldB': {'name': 'FieldA+FieldB', 'desc': 'FieldA Concat FieldB description', 'select': '    , (@FieldA || @FieldB) AS "FieldA+FieldB"\n', 'from_': None, 'join': None, 'where': None, 'group_by': None, 'order_by': None, 'having': None, 'window': None, 'extras': None, 'active': True}}
```

# GET QUERY STRING (SQL)


```python
sql = qd.get_query_sql(None)
print(sql)
```

    {'name': None, 'desc': None, 'select': 'SELECT "TABLE_A"."FILED_A" AS "FieldA"\n    , "TABLE_B"."FILED_B" AS "FieldB"\n    , (("TABLE_A"."FILED_A") || ( "TABLE_B"."FILED_B")) AS "FieldA+FieldB"\n', 'from_': 'FROM "TABLE_A"\n', 'join': 'LEFT OUTER JOIN (\n    SELECT *\n    FROM "TABLE_B"\n) AS "TABLE_B" ON (\n    "TABLE_B"."FK_FROM_A" = "TABLE_A"."KEY_FIELD"\n    AND "TABLE_B"."DATE_FIELD" = "TABLE_A"."DATE_FIELD"\n)\n', 'where': 'WHERE "TABLE_A"."COND_FIELD_A" IS NOT NULL \n    AND "TABLE_A"."DATE_FIELD" = \'{YYYY-MM-DD}\'\n', 'group_by': '', 'order_by': '', 'having': '', 'window': '', 'extras': None, 'active': True}
    SELECT "TABLE_A"."FILED_A" AS "FieldA"
        , "TABLE_B"."FILED_B" AS "FieldB"
        , (("TABLE_A"."FILED_A") || ( "TABLE_B"."FILED_B")) AS "FieldA+FieldB"
    FROM "TABLE_A"
    LEFT OUTER JOIN (
        SELECT *
        FROM "TABLE_B"
    ) AS "TABLE_B" ON (
        "TABLE_B"."FK_FROM_A" = "TABLE_A"."KEY_FIELD"
        AND "TABLE_B"."DATE_FIELD" = "TABLE_A"."DATE_FIELD"
    )
    WHERE "TABLE_A"."COND_FIELD_A" IS NOT NULL 
        AND "TABLE_A"."DATE_FIELD" = '{YYYY-MM-DD}'
    


# SET DATE


```python
import datetime
dates = [datetime.date(2023, 1, 31)]
sql = qd.set_date(sql, dates)
print(sql)
```
```sql
    SELECT "TABLE_A"."FILED_A" AS "FieldA"
        , "TABLE_B"."FILED_B" AS "FieldB"
        , (("TABLE_A"."FILED_A") || ( "TABLE_B"."FILED_B")) AS "FieldA+FieldB"
    FROM "TABLE_A"
    LEFT OUTER JOIN (
        SELECT *
        FROM "TABLE_B"
    ) AS "TABLE_B" ON (
        "TABLE_B"."FK_FROM_A" = "TABLE_A"."KEY_FIELD"
        AND "TABLE_B"."DATE_FIELD" = "TABLE_A"."DATE_FIELD"
    )
    WHERE "TABLE_A"."COND_FIELD_A" IS NOT NULL 
        AND "TABLE_A"."DATE_FIELD" IN ('2023-01-31')
```   
    


```python

```
