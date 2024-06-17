<template>
  <div class="scroll-gantt">
    <g-gantt-chart
        :chart-start="startDate"
        :chart-end="endDate"
        precision="day"
        width="100%"
        bar-start="start_date"
        bar-end="end_date"
    >
      <div v-if="rowBarListVessels.length" class="section">Суда</div>
      <g-gantt-row v-for="(path, idx) in rowBarListVessels" :bars="path.bars" :key="idx" :label="path.label"/>

      <div v-if="rowBarListIcebreakers.length" class="section">Ледоколы</div>
      <g-gantt-row v-for="(path, idx) in rowBarListIcebreakers" :bars="path.bars" :key="idx" :label="path.label"/>
    </g-gantt-chart>
  </div>
</template>

<script setup lang="ts">
import {computed, onMounted, Ref, ref} from "vue"
import {GanttBarObject, GGanttChart, GGanttRow} from "@infectoone/vue-ganttastic";
import {useIceTransportStore} from "../../store";
import {IIcebreaker, IPath, IVessel, IWaybill, tTypeWay, typeTransport} from "../../types.ts";
import {storeToRefs} from "pinia";
import {DateTime} from "luxon";
import {getDate} from "../../utils/getDate.ts";

const {vessels, pathsVessels, icebreakers, pathsIcebreakers} = storeToRefs(useIceTransportStore())

interface IRowBar {
  label: string
  bars: GanttBarObject[]
}

const rowBarListVessels: Ref<IRowBar[]> = ref([])
const rowBarListIcebreakers: Ref<IRowBar[]> = ref([])
const startDate = ref()
const endDate = ref()

onMounted(() => {
  // @ts-ignore
  rowBarListVessels.value = createRows(pathsVessels.value, vessels.value, 'vessel_id', typeTransport.VESSELS)
  // @ts-ignore
  rowBarListIcebreakers.value = createRows(pathsIcebreakers.value, icebreakers.value, 'icebreaker_id', typeTransport.ICEBREAKERS)

  startDate.value = getStartDate()
  endDate.value = getEndDate()
})

const getStartDate = () => {
  const minDate = [...pathsVessels.value, ...pathsIcebreakers.value]
      .reduce((acc, date) => {
        return acc && new Date(acc) < new Date(date.start_date) ? acc : date.start_date
      }, '')

  return date.value(minDate)
}

const getEndDate = () => {
  const maxDate = [...pathsVessels.value, ...pathsIcebreakers.value]
      .reduce((acc, date) => {
        // @ts-ignore
        return acc && new Date(acc) > new Date(date.end_date || date.start_date) ? acc : date.end_date || date.start_date
      }, '')

  return `${date.value(maxDate, "yyyy-MM-dd")} 23:59`
}

const date = computed(() => {
  return ((date: string, format: string = 'yyyy-MM-dd HH:mm') => {
    return getDate(date, format)
  })
})

const createRows = (paths: IPath[], listTransport: IVessel[] | IIcebreaker[], keyIdx: string, type: typeTransport) => {
  return paths.map(path => {
    return {
      // @ts-ignore
      label: listTransport?.find(transport => transport.id === path[keyIdx])?.name || '',
      bars: path.waybill?.map((way, idx) => {
        const {start_date, end_date} = getDates(way, path, idx)

        return {
          start_date,
          end_date,
          ganttBarConfig: {
            // @ts-ignore
            id: `${path[keyIdx]}_${way.point}_${way.event}`,
            style: {
              background: getBackground(way.event, type),
            }
          }
        }
      })
    }
  })
}

const getDates = (way: IWaybill, path: IPath, idx: number) => {
  const start_date = date.value(way.dt)

  let end_date

  if (way.event === tTypeWay.FIN) {
    end_date = date.value(way.dt)
  } else if (way.event === tTypeWay.STUCK) {
    // @ts-ignore
    end_date = date.value(DateTime.fromISO(way.dt).plus({hours: 1}))
  } else if (path.waybill[idx + 1]) {
    // @ts-ignore
    end_date = date.value(DateTime.fromISO(path.waybill[idx + 1].dt))
  } else {
    end_date = date.value(DateTime.fromISO(way.dt))
  }

  return {
    start_date,
    end_date
  }
}

const getBackground = (event: tTypeWay, type: typeTransport) => {
  if ((event === tTypeWay.MOVE || event === tTypeWay.FIN) && type === typeTransport.VESSELS) return 'green'
  if (event === tTypeWay.STUCK) return 'red'
  if (event === tTypeWay.FORMATION) return 'blue'
  if (type === typeTransport.ICEBREAKERS && event !== tTypeWay.WAIT) return 'deepskyblue'
  return 'gray'
}
</script>

<style lang="scss" scoped>
.scroll-gantt {
  display: grid !important;
  flex-wrap: nowrap !important;
  overflow: auto;
  min-width: 100%;
  max-height: 500px;

  .section {
    padding-bottom: 10px;
    padding-top: 10px;
    font-weight: bold;
  }
}
</style>