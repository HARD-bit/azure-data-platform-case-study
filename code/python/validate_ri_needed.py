"""Validatore indipendente del fabbisogno di Reserved Instance ("Needed").

Ricalcola fuori da Power BI la stessa catena di normalizzazione ISF del modello
semantico, cosi' i numeri del report possono essere confrontati con un calcolo
indipendente prima di ogni round di acquisto.

Input (CSV):
  vms.csv  : id, vmSize, location            (export Azure Resource Graph)
  isf.csv  : ArmSkuName, InstanceSizeFlexibilityGroup, Ratio
  registry.csv : ResID, Keep, AO, Deleted     (registro operativo)
"""
import argparse
import pandas as pd


def build_base_sizes(isf: pd.DataFrame) -> pd.DataFrame:
    """Per ogni gruppo ISF: VM piu' piccola (MinVMSize) e il suo ratio."""
    df = isf.dropna(subset=["Ratio"]).copy()
    df["Group"] = df["InstanceSizeFlexibilityGroup"].str.strip()
    df["Arm"] = df["ArmSkuName"].str.strip()
    # tie-break deterministico: ordine alfabetico tra le SKU al ratio minimo
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
    out["RatioDivided"] = out["Ratio"] / out["MinRatio"]   # SKU senza match -> NaN -> ignorata dalla somma

    # join case-insensitive sul Resource ID (il casing in ARM non e' affidabile)
    out["k"] = out["id"].str.lower()
    reg = registry.assign(k=registry["ResID"].str.lower())
    out = out.merge(reg[["k", "Keep", "AO", "Deleted"]], on="k", how="left")

    eligible = (out["AO"].astype(str).str.upper().eq("TRUE")
                & out["Deleted"].astype(str).str.upper().ne("YES")
                & out["Keep"].isin(["Permanent", "AVD"]))
    out["eligible"] = eligible
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
    print(f"\nVM senza match ISF: {res['Ratio'].isna().sum()}")


if __name__ == "__main__":
    main()
