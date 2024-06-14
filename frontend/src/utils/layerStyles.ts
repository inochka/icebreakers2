import {Circle, Fill, Icon, Stroke, Style} from "ol/style";
import {FeatureLike} from "ol/Feature";
import {tTypeWay} from "../types.ts";
import endPoint from "../assets/icons/anchor-icon-svgrepo-com.png";

const stylePoint = (color: string) => {
    return new Style({
        fill: new Fill({
            color: color
        }),
        stroke: new Stroke({
            width: 3,
            color: color
        }),
        image: new Circle({
            fill: new Fill({
                color: color
            }),
            stroke: new Stroke({
                width: 5,
                color: color
            }),
            radius: 5
        }),
    })
}

const styleLine = (color: string) => {
    return new Style({
        stroke: new Stroke({
            color: color,
            width: 2,
        })
    })
}

export const getStyles = (feature: FeatureLike) => {
    const {event, success} = feature.getProperties()
    const type = feature.getGeometry()?.getType()

    if (type === 'Point' && event === tTypeWay.MOVE) {
        return stylePoint('blue')
    }

    if (type === 'Point' && event === tTypeWay.FIN) {
        return new Style({
            image: new Icon({
                height: 20,
                width: 20,
                src: endPoint,
            }),
        })
    }

    if (type === 'Point' && event === tTypeWay.WAIT) {
        return stylePoint('gray')
    }

    if (event === tTypeWay.MOVE || event === tTypeWay.FIN) {
        return new Style({
            stroke: new Stroke({
                color: success ? 'green' : 'red',
                width: 2,
            })
        })
    }

    if (event === tTypeWay.FORMATION) {
        return styleLine('blue')
    }

    return styleLine('gray')
}
