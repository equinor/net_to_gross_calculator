"""Calculate Net:Gross estimates"""


def calculate_deep_net_gross_model(model, composition):
    """Calculate a net gross estimate based on the given deep composition"""
    net_gross = model.assign(
        bb_pct=lambda df: df.apply(
            lambda row: composition["building_block_type"][row.building_block_type],
            axis="columns",
        ),
        cls_ratio=1.0,
    )

    for building_block_type in ("Channel Fill", "Lobe"):
        for filter_class, weights in composition.get(building_block_type, {}).items():
            ignores = [v for k, v in weights.items() if k.startswith("Ignore ")]
            if ignores and ignores[0]:
                idx = net_gross.query(
                    "building_block_type == @building_block_type"
                ).index
                num_values = len(
                    [v for v in net_gross.loc[idx, filter_class].unique() if v]
                )
                net_gross.loc[idx, "cls_ratio"] /= num_values
            else:
                for value in (
                    net_gross.query("building_block_type == @building_block_type")
                    .loc[:, filter_class]
                    .unique()
                ):
                    idx = net_gross.query(
                        "building_block_type == @building_block_type and "
                        f"{filter_class} == @value"
                    ).index
                    net_gross.loc[idx, "cls_ratio"] *= weights.get(value, 0) / 100

    return net_gross.assign(
        result=lambda df: df.loc[:, ["net_gross", "bb_pct", "cls_ratio"]].prod(
            axis="columns"
        )
    )


def calculate_deep_net_gross(model, composition):
    """Calculate one net gross number"""
    return (
        calculate_deep_net_gross_model(model=model, composition=composition)
        .loc[:, "result"]
        .sum()
    )


def calculate_shallow_net_gross_model(model, composition):
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

    return net_gross.assign(
        result=lambda df: df.loc[:, ["net_gross", "bb_pct"]].prod(axis="columns")
    )


def calculate_shallow_net_gross(model, composition):
    """Calculate one net gross number"""
    return (
        calculate_shallow_net_gross_model(model=model, composition=composition)
        .loc[:, "result"]
        .sum()
    )
