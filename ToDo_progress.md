# ToDo Progress

Date: 2025-08-28

## Implemented

- Satellite map display toggle (single vs all) with selector; default AVISO.
- Added coastline overlay using contour over data mask; default bbox set to [[-99, -81], [18, 30]].
- Converted satellite SST from Kelvin to Celsius; updated hover and labels.
- Colorbar titles updated to include parameter names and units for all maps.
- NeSPReSO T and S map sizes matched to satellite maps.
- Added 'Add Points' toggle and ensured draw line tool is available on all maps; added undo/clear for profiles/transects.
- Instruction overlays for Profiles and Transects, auto-swap to Undo/Clear when active.

## UI Additions

- Controls in sidebar: Show all maps switch, Field selector, Add Points toggle.
- New instruction containers above transect and profile plots.

## Figure Behavior

- Default geographic extent: lon [-99, -81], lat [18, 30].
- SST shown in °C; salinity in PSU; AVISO in meters.

## Notes

- Coastlines are derived from data mask (NaNs over land). If a dedicated coastline dataset is desired, can integrate Cartopy-generated shapelines rasterized into contours.

## Next

- Optional: Persist user-selected display mode and field via `dcc.Store`.


