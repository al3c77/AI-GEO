/*
 * Copyright (c) 2018 vladzaitsev@gmail.com
 */

import * as Immutable from 'immutable';
import { MAPID } from './app';

/**
 *  executes callback for mapbox layer that have tiles injected
 *
 *  params to invoke function :
 *  const oldLayer = state.keplerGl[MAPID].visState.layers[idx];
 *  console.log(oldLayer);
 *  const { config: { dataId, columns: { geojson } } } = oldLayer;
 *
 *  callback called with arguments (layerIdx, lid) where `layerIdx` is index in layers List and  `lid` is _sourceId_ of tiles layer
 *
 * @param keplerState
 * @param oldLayerConfig
 * @param callback
 * @returns {null}
 */
const processMapLyaer = (keplerState, { config: { dataId, columns: { geojson } } }, callback) => {
    if (geojson) {
        try {
            const dataset = keplerState.visState.datasets[dataId];
            if (dataset.fields[geojson.fieldIdx].type !== 'geojson' || dataset.fields[geojson.fieldIdx].name !== geojson.value) {
                console.error(`layer field dont have corresponding data field ${geojson.value} in ${dataset.label}`);
                return null
            }
            const lid = composeTileLayerId(dataId, geojson.value);
            let immutable_bottom = keplerState.mapStyle.bottomMapStyle;
            let new_kepler_layers = immutable_bottom.get('layers');
            let layerIdx = new_kepler_layers.findIndex(l => l.has('source') && l.get('source') === lid);
            if (layerIdx !== -1) {
                callback(layerIdx, lid);
            }
        } catch (e) {
            console.error('Exception while processing layer', e)
        }
    } else {
        console.warn('bad geojson')
    }
};


const composeTileLayerId = (dsid, cog_field_name) => `${dsid}_${cog_field_name}_cogurl`;

export const tilerPreprocessorLAYER_CONFIG_CHANGE = (state, action) => {
    let keplerState = state.keplerGl[MAPID];
    if (!keplerState.mapStyle.bottomMapStyle) {
        return null;
    }

    let imutable_bottom = keplerState.mapStyle.bottomMapStyle;
    const newVisibility = action.payload.newConfig.isVisible ? 'visible' : 'hidden';
    processMapLyaer(keplerState, action.payload.oldLayer, (layerIdx) => {
        imutable_bottom = imutable_bottom.setIn(['layers', layerIdx, 'layout', 'visibility'], newVisibility);
    });
    if (keplerState.mapStyle.bottomMapStyle !== imutable_bottom) {
        keplerState.mapStyle.bottomMapStyle = imutable_bottom;
    }
    return null

};
export const tilerPreprocessorDebouncedOpacity = (state, action) => {
    let keplerState = state.keplerGl[MAPID];
    if (!keplerState.mapStyle.bottomMapStyle) {
        return null;
    }

    const { newVisConfig: { opacity } } = action.payload;
    let immutable_bottom = keplerState.mapStyle.bottomMapStyle;
    processMapLyaer(keplerState, action.payload, (layerIdx) => {
        immutable_bottom = immutable_bottom.setIn(['layers', layerIdx, 'paint', 'raster-opacity'], opacity);
    });
    if (keplerState.mapStyle.bottomMapStyle !== immutable_bottom) {
        keplerState.mapStyle.bottomMapStyle = immutable_bottom;
    }
    return null

};
export const tilerPreprocessorREMOVE_LAYER = (state, action) => {
    let keplerState = state.keplerGl[MAPID];
    if (!keplerState.mapStyle.bottomMapStyle) {
        return null;
    }
    const oldLayer = keplerState.visState.layers[action.payload.idx];
    const { config: { dataId, columns: { geojson } } } = oldLayer;
    let immutable_bottom = keplerState.mapStyle.bottomMapStyle;
    processMapLyaer(keplerState, oldLayer, (layerIdx, lid) => {
        immutable_bottom = immutable_bottom
            .update('layers', layers => layers.filterNot(layer => layer.has('source') && layer.get('source') === lid))
            .update('sources', sources => sources.filterNot((val, key) => key === lid))
        ;
    });
    if (keplerState.mapStyle.bottomMapStyle !== immutable_bottom) {
        keplerState.mapStyle.bottomMapStyle = immutable_bottom;
    }
    return null;
};


export const tilerPreprocessorREMOVE_DATASET = (state, action) => {
    let keplerState = state.keplerGl[MAPID];
    if (!keplerState.mapStyle.bottomMapStyle) {
        return null;
    }
    const reg = new RegExp(`${action.payload.key}.+_cogurl`);
    keplerState.mapStyle.bottomMapStyle = keplerState.mapStyle.bottomMapStyle
        .update('layers', layers => layers.filterNot(layer => reg.test(layer.get('source'))))
        .update('sources', sources => sources.filterNot((val, key) => reg.test(key)))
    ;
    return customizedKeplerGlReducer(state.keplerGl, action);
};
export const tilerPreprocessorADD_DATA_TO_MAP = (state, action) => {
    if (!action.payload.datasets || !action.payload.datasets.length) {
        return null;
    }
    if (!state.keplerGl[MAPID].mapStyle.bottomMapStyle) {
        console.error("Dataset loading while mapStyle is not ready");
        return null;
    }
    let keplerState = state.keplerGl[MAPID];
    let imutable_bottom = keplerState.mapStyle.bottomMapStyle;

    action.payload.datasets.forEach(dataset => {
        const geojsons = [];
        // console.log(dataset);
        dataset.data.fields.filter(f => f.type === 'geojson').forEach(geom => {

                dataset.data.rows.forEach(r => {
                    try {
                        //in .csv row has string, in .geojson it has object
                        const geo = typeof r[geom.tableFieldIndex - 1] === 'string'
                            ? JSON.parse(r[geom.tableFieldIndex - 1])
                            : r[geom.tableFieldIndex - 1];
                        if (geo.hasOwnProperty('properties') && geo.properties.hasOwnProperty('COGURL')) {
                            geojsons.push({ fname: geom.name, url: geo.properties.COGURL });
                            // console.log(geo.properties.COGURL);
                        }
                    } catch (e) {
                        console.error("Bad geojson", r[geom.tableFieldIndex - 1])
                    }
                });
            }
        );
        if (geojsons.length) {
            const dsid = dataset.info.id;


            geojsons.forEach((cog, i) => {
                const lid = composeTileLayerId(dsid, cog.fname);
                if (imutable_bottom.hasIn(['sources', lid])) {
                    // COG layer already exists, next geojson
                    return;
                }
                const urls = typeof cog.url === "string" ? [cog.url] : cog.url;
                const newSource = Immutable.fromJS({
                    type: 'raster',
                    tiles: [
                        ...urls
                        // 'http://tiles.rdnt.io/tiles/{z}/{x}/{y}@2x?url=https%3A%2F%2Foin-hotosm.s3.amazonaws.com/56f9b5a963ebf4bc00074e70/0/56f9c2d42b67227a79b4faec.tif',                                // ...urls
                    ],
                    tileSize: 256
                });
                // console.log(newSource);
                const newLayer = Immutable.fromJS({
                    'id': `${lid}_layer`,
                    'type': 'raster',
                    'source': lid,
                    'layout': {
                        'visibility': 'visible'
                    },
                    paint: {
                        'raster-opacity': 0.8,
                    }
                });
                imutable_bottom = imutable_bottom
                    .update('layers', layers => layers.push(newLayer))
                    .update('sources', sources => sources.set(lid, newSource));
            });

        }
    });
    if (keplerState.mapStyle.bottomMapStyle !== imutable_bottom) {
        keplerState.mapStyle.bottomMapStyle = imutable_bottom;

    }

    return null;
};