"""Independent validator for the Reserved Instance "Needed" figure.

Recomputes, outside Power BI, the same ISF normalization chain used by the semantic
model, so the report's numbers can be cross-checked against an independent
calculation before every purchasing round.

Inputs (CSV):
  vms.csv      : id, vmSize, location            (Azure Resource Graph export)
  isf.csv      : ArmSkuName, InstanceSizeFlexibilityGroup, Ratio
  registry.csv : ResID, Keep, AO, Deleted        (operational registry)
"""
import argparse

import pandas as pd


def build_base_sizes(isf: pd.DataFrame) -> pd.DataFrame:
    """For each ISF group: the smallest VM (MinVMSize) and its ratio."""
    df = isf.dropna(subset=["Ratio"]).copy()
    df["Group"] = df["InstanceSizeFlexibilityGroup"].str.strip()
    df["Arm"] = df["ArmSkuName"].str.strip()
    # deterministic tie-break: alphabetical order among SKUs at the minimum ratio
    base = (df.sort_values(["Group", "Ratio", "Arm"])
              .groupby("Group", as_index=False).first()
              .rename(columns={"Arm": "MinVMSize", "Ratio": "MinRatio"}))
    return base[["Group", "MinVMSize", "MinRatio"]]


def needed(vms, isf, registry) -> pd.DataFrame:
    base = build_base_sizes(isf)
    isf = isf.assign(ArmSkuName=isf["ArmSkuName"].str.strip()).drop_duplicates("ArmSkuName")

    out = vms.merge(isf[["ArmSkuName", "Ratio", "InstanceSizeFlexibilityGroup"]],
                    left_on="vmSize", right_on="ArmSkuName", how="left")
    out = out.merge(base, left_on="InstanceSizeFlexibilityGroup", right_on="Group", how="left")
    out["RatioDivided"] = out["Ratio"] / out["MinRatio"]   # no ISF match -> NaN -> ignored by sum

    # case-insensitive join on the Resource ID (ARM casing is not reliable)
    out["k"] = out["id"].str.lower()
    reg = registry.assign(k=registry["ResID"].str.lower())
    out = out.merge(reg[["k", "Keep", "AO", "Deleted"]], on="k", how="left")

    out["eligible"] = (out["AO"].astype(str).str.upper().eq("TRUE")
                       & out["Deleted"].astype(str).str.upper().ne("YES")
                       & out["Keep"].isin(["Permanent", "AVD"]))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--vms", required=True)
    ap.add_argument("--isf", required=True)
    ap.add_argument("--registry", required=True)
    a = ap.parse_args()
    res = needed(pd.read_csv(a.vms), pd.read_csv(a.isf), pd.read_csv(a.registry))
    summary = (res.groupby(["MinVMSize", "location"])
                  .apply(lambda g: pd.Series({
                      "needed_eligible": g.loc[g.eligible, "RatioDivided"].sum(),
                      "needed_all_fleet": g["RatioDivided"].sum()}), include_groups=False)
                  .reset_index())
    print(summary.to_string(index=False))
    print(f"\nVMs with no ISF match: {res['Ratio'].isna().sum()}")


if __name__ == "__main__":
    main()
