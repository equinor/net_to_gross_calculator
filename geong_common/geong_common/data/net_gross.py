"""Calculate Net:Gross estimates"""


def calculate_shallow_net_gross(model, composition):
    """Calculate a net gross estimate based on the given shallow composition"""
    net_gross = model.assign(
        bb_pct=lambda df: df.apply(
            lambda row: composition.get(row.building_block_type, 0)
            if composition.get(f"{row.building_block_type} Quality")
            == row.descriptive_reservoir_quality
            else 0,
            axis="columns",
        ),
    )

    return net_gross.loc[:, ["net_gross", "bb_pct"]].prod(axis="columns").sum()
