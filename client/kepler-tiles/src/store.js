/*
 * Copyright (c) 2018 vladzaitsev@gmail.com
 */

import { applyMiddleware, combineReducers, compose, createStore } from 'redux';
import keplerGlReducer from 'kepler.gl/reducers';
import appReducer from './app-reducer';
import { taskMiddleware } from 'react-palm/tasks';
import window from 'global/window';

import debounce from 'lodash.debounce';
import { createAction } from 'redux-actions';
import {
    tilerPreprocessorADD_DATA_TO_MAP,
    tilerPreprocessorDebouncedOpacity,
    tilerPreprocessorLAYER_CONFIG_CHANGE,
    tilerPreprocessorREMOVE_DATASET, tilerPreprocessorREMOVE_LAYER
} from './tilerPreproccessor';

const customizedKeplerGlReducer = keplerGlReducer
    .initialState({
        uiState: {
            // hide side panel to disallower user customize the map
            readOnly: false,

            // customize which map control button to show
            mapControls: {
                visibleLayers: {
                    show: true
                },
                mapLegend: {
                    show: true,
                    active: true
                },
                toggle3d: {
                    show: false
                },
                splitMap: {
                    show: false
                }
            },
            // "mapStyle": {
            //     "bottomMapStyle": {
            //         "sources": {
            //             "aaa": {
            //                 "type": "raster",
            //                 "tiles": [
            //                     "http://tiles.rdnt.io/tiles/{z}/{x}/{y}@2x?url=https%3A%2F%2Fs3-us-west-2.amazonaws.com%2Fplanet-disaster-data%2Fhurricane-harvey%2FSkySat_Freeport_s03_20170831T162740Z3.tif"
            //                 ],
            //                 "tileSize": 256
            //             }
            //         },
            //         "layers": [
            //             {
            //                 "id": "bbb",
            //                 "type": "raster",
            //                 "source": "aaa",
            //                 "layout": {
            //                     "visibility": "visible"
            //                 },
            //                 "paint": {
            //                     "raster-opacity": 1
            //                 }
            //             }
            //         ]
            //     },
            // }

        }
    })
    // handle additional actions
    .plugin({
        HIDE_AND_SHOW_SIDE_PANEL: (state, action) => ({
            ...state,
            uiState: {
                ...state.uiState,
                readOnly: !state.uiState.readOnly
            }
        }),

    })
;


const reducers = combineReducers({
    keplerGl: customizedKeplerGlReducer,
    app: appReducer
});



const composedReducer = (state, action) => {
    //TODO add debounce to opacity

    if (['DEBOUNCED_OPACITY'].includes(action.type)) {
        tilerPreprocessorDebouncedOpacity(state, action);
    }
    if (['@@kepler.gl/LAYER_CONFIG_CHANGE'].includes(action.type) &&
        action.payload.newConfig && action.payload.newConfig.hasOwnProperty('isVisible')) {
        tilerPreprocessorLAYER_CONFIG_CHANGE(state, action);
    }
    if (['@@kepler.gl/LAYER_VIS_CONFIG_CHANGE'].includes(action.type)
        && action.payload.newVisConfig && action.payload.newVisConfig.hasOwnProperty('opacity')) {
        const { config: { dataId, columns: { geojson } } } = action.payload.oldLayer;
        //make payload layer-like
        dispatchDebouncedOpacity({
            config: {
                dataId,
                columns: { geojson },

            }, newVisConfig: { opacity: action.payload.newVisConfig.opacity }
        });

    }
    if (['@@kepler.gl/REMOVE_DATASET'].includes(action.type)) {
        tilerPreprocessorREMOVE_DATASET(state, action);
    }
    if (['@@kepler.gl/REMOVE_LAYER'].includes(action.type)) {
        tilerPreprocessorREMOVE_LAYER(state, action);

    }
// -------------- add tiles -----------------------------
    if (['@@kepler.gl/ADD_DATA_TO_MAP'].includes(action.type)) {
        // console.log(action.payload);
        tilerPreprocessorADD_DATA_TO_MAP(state, action);
    }
    return reducers(state, action);
};

const middlewares = [taskMiddleware];
const enhancers = [applyMiddleware(...middlewares)];

const initialState = {};

// add redux devtools
const composeEnhancers = window.__REDUX_DEVTOOLS_EXTENSION_COMPOSE__ || compose;

const store = createStore(
    composedReducer,
    initialState,
    composeEnhancers(...enhancers)
);

const debouncedOpacityAction = createAction('DEBOUNCED_OPACITY');
const dispatchDebouncedOpacity = debounce((payload) => {
    store.dispatch(debouncedOpacityAction(payload));
}, 300, {
    'leading': false,
    'trailing': true
});

export default store;
