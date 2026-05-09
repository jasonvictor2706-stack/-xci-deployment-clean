from services.ml_service import SOIL_DF, CLIMATE_DF
from fastapi import HTTPException


def _fuzzy_match(df, region: str):
    """Case-insensitive substring match on Region column."""
    key = region.strip().lower()
    # Exact match first
    exact = df[df["_region_key"] == key]
    if not exact.empty:
        return exact.iloc[0]
    # Partial match
    partial = df[df["_region_key"].str.contains(key, na=False)]
    if not partial.empty:
        return partial.iloc[0]
    # Try matching the other way (csv region contains input)
    for _, row in df.iterrows():
        if key in row["_region_key"] or row["_region_key"] in key:
            return row
    return None


def _fuzzy_match_climate(df, region: str, season: str):
    """Match on Region AND Season columns."""
    key = region.strip().lower()
    season_key = season.strip().lower()
    
    # First filter by season
    # Using df["Season"] as the climate dataset has a 'Season' column
    season_df = df[df["Season"].str.strip().str.lower() == season_key]
    
    if season_df.empty:
        return None
        
    # Then fuzzy match region within that season subset
    return _fuzzy_match(season_df, region)


def get_region_features(region: str, season: str) -> dict:
    """
    Returns merged feature dict for a given Indian state/UT and Season.
    """
    soil_row = _fuzzy_match(SOIL_DF, region)
    climate_row = _fuzzy_match_climate(CLIMATE_DF, region, season)

    if soil_row is None:
        raise HTTPException(
            status_code=404,
            detail=f"Region '{region}' not found in soil database. "
                   f"Please check the region name.",
        )
    if climate_row is None:
        raise HTTPException(
            status_code=404,
            detail=f"Season '{season}' for Region '{region}' not found in climate database. "
                   f"Please check the selection.",
        )

    return {
        "N": float(soil_row["Avg_N"]),
        "P": float(soil_row["Avg_P"]),
        "K": float(soil_row["Avg_K"]),
        "ph": float(soil_row["Avg_pH"]),
        "temperature": float(climate_row["Temperature"]),
        "humidity": float(climate_row["Humidity"]),
        "rainfall": float(climate_row["Rainfall"]),
        "soil_type": str(soil_row["Soil_Type"]),
        "region_matched": str(soil_row.get("State", soil_row.get("Region"))),
    }
