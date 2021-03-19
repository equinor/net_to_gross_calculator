# Scripts

The scripts in this directory are not critical to the use of the **Net to Gross Calculator**. However, they have been used during development and might come in handy when investigating your own data.


## `annotate_ppt.py`

Based on https://pbpython.com/creating-powerpoint.html

Can be used to find the necessary indexes and placeholders if you need to set up your own description of a Power Point template similar to [`geong_pptx.toml`](../geong_common/geong_common/assets/templates/geong_pptx.toml) to use together with [`geong_common.reports.powerpoint`](../geong_common/geong_common/reports/powerpoint.py).


## `check_unique.py`

Can be used to confirm that your `unique_id` values are in fact unique. If duplicates are found, information about those duplicates are stored in an Excel sheet.


## `describe_shallow_data.py`

Can be used to get an overview over your shallow data, including composition of building block types and modeling values.
