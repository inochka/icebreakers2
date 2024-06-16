import {Circle, Fill, Icon, Stroke, Style} from "ol/style";
import {FeatureLike} from "ol/Feature";
import {tTypeWay, typeTransport} from "../types.ts";
import endPoint from "../assets/icons/anchor-icon-svgrepo-com.png";
import icebreakerIcon from "../assets/icons/ship-2-svgrepo-com.png";

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
    const {event, point, transport} = feature.getProperties()
    const type = feature.getGeometry()?.getType()

    if (type === 'Point' && transport === typeTransport.ICEBREAKERS && event === tTypeWay.MOVE) {
        return new Style({
            image: new Icon({
                height: 20,
                width: 20,
                src: icebreakerIcon,
            }),
        })
    }

    if (type === 'Point' && event === tTypeWay.STUCK) {
        return stylePoint('red')
    }

    if ((type === 'Point' && event === tTypeWay.MOVE) || (type === 'Point' && point === 'start')) {
        return stylePoint('blue')
    }

    if ((type === 'Point' && event === tTypeWay.FIN) || (type === 'Point' && point === 'end')) {
        return new Style({
            image: new Icon({
                height: 20,
                width: 20,
                src: endPoint,
            }),
        })
    }

    if (type === 'Point' && (event === tTypeWay.WAIT || event === tTypeWay.FORMATION)) {
        return stylePoint('gray')
    }

    if (event === tTypeWay.FORMATION) {
        return new Style({
            stroke: new Stroke({
                color: 'blue',
                width: 2,
            })
        })
    }

    if ((event === tTypeWay.MOVE || event === tTypeWay.FIN) && transport === typeTransport.ICEBREAKERS) {
        return new Style({
            stroke: new Stroke({
                color: 'deepskyblue',
                width: 2,
            })
        })
    }

    if (event === tTypeWay.MOVE || event === tTypeWay.FIN) {
        return new Style({
            stroke: new Stroke({
                color: 'green',
                width: 2,
            })
        })
    }

    return styleLine('gray')
}
