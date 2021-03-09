"""Create a PowerPoint report"""

# Standard library imports
import functools
import io

# Third party imports
import pptx
import pyplugs
from pptx.chart.data import ChartData
from pptx.enum import chart as pptx_charts
from pyconfs import Configuration

# Geo:N:G imports
from geong_common import files

# Call plugin functions within powerpoint module
*_, PLUGIN = __name__.split(".")
call = functools.partial(pyplugs.call, __package__, PLUGIN)
content_types = functools.partial(pyplugs.funcs, __package__, PLUGIN)


@pyplugs.register
def generate_powerpoint(template_url, cfg, data, output_path):
    """Generate PowerPoint report from data based on cfg. Store to output_path"""
    template = files.get_url_or_asset(template_url, local_assets="geong_common.assets")
    template_cfg = Configuration.from_str(template.read_text(), format="toml")
    template_ppt = (template.parent / template_cfg.replace("template")).read_bytes()

    prs = pptx.Presentation(io.BytesIO(template_ppt))
    add_slides(prs, template_cfg, cfg, data)
    prs.save(output_path)


def add_slides(prs, template, cfg, data):
    """Generate slides and insert them into the prs PowerPoint document"""
    for slide_cfg in cfg.slide:
        if "nested" in slide_cfg:
            for single_data in data[slide_cfg.nested["data"]]:
                add_slides(prs, template, cfg[slide_cfg.nested.cfg], single_data)
            continue

        layout_name = template.layouts.get(slide_cfg.layout, slide_cfg.layout)
        layout = prs.slide_layouts.get_by_name(layout_name)
        slide = prs.slides.add_slide(layout)

        # Add title
        if "title" in slide_cfg:
            slide.shapes.title.text = slide_cfg.title.format(**data)

        # Add content
        ph_cfg = template.placeholders[slide_cfg.layout]
        for placeholder, info in slide_cfg.section_items:
            if placeholder not in ph_cfg:
                raise ValueError(
                    f"Unknown placeholder {placeholder!r}. "
                    f"Choose between {', '.join(ph_cfg.entry_keys)}"
                )

            func = f"add_{info.type}"
            if func not in content_types():
                types = [ct[4:] for ct in content_types() if ct.startswith("add_")]
                raise ValueError(
                    f"Unknown type {info.type!r}. Choose between {', '.join(types)}"
                )

            content = info.content
            if isinstance(content, str) and content.startswith("ref:"):
                content = cfg.content[info.type][info.content[4:]]

            call(
                func=func,
                placeholder=slide.placeholders[ph_cfg[placeholder]],
                content=content,
                data=data,
            )


@pyplugs.register
def add_text(placeholder, content, data):
    """Add text to placeholder"""
    placeholder.text = content.format(**data)


@pyplugs.register
def add_picture(placeholder, content, data):
    """Add picture to placeholder, content should be path to image file"""
    placeholder.insert_picture(content.format(**data))


@pyplugs.register
def add_chart(placeholder, content, data):
    """Add chart to placeholder

    TODO: Figure out what would be a useful general way of specifying content
    """
    chart = ChartData()
    chart.categories = content.categories
    chart.add_series("Series 1", content.series_1)
    chart.add_series("Series 2", content.series_2)
    placeholder.insert_chart(
        getattr(pptx_charts.XL_CHART_TYPE, content.type.upper()), chart
    )


@pyplugs.register
def add_table(placeholder, content, data):
    """Add table to placeholder

    TODO: Figure out what would be a useful general way of specifying content
    """
    table = placeholder.insert_table(rows=content.rows, cols=len(content.cols)).table

    for idx, col_name in enumerate(content.cols):
        table.cell(0, idx).text = col_name
