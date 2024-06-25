import VectorSource from "ol/source/Vector";
import {GeoJSON} from "ol/format";
import VectorLayer from "ol/layer/Vector";
import {getStyles} from "./layerStyles.ts";

export const generateVectorLayer = (featuresFunction: (params: any) => any[], params = null) => {
    const features = {
        type: 'FeatureCollection',
        crs: {
            type: 'lines',
            properties: {
                name: 'EPSG:3857',
            },
        },
        features: featuresFunction(params),
    }
    const vectorSource = new VectorSource({
        features: new GeoJSON().readFeatures(features),
    });

    const vectorLayer = new VectorLayer({
        source: vectorSource,
        style: (feature) => getStyles(feature)
    })
    vectorLayer.setZIndex(3);

    return vectorLayer
}