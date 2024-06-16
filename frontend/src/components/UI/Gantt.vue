<template>
  <div class="scroll-gantt">
    <g-gantt-chart
        :chart-start="date(vessels[0].start_date)"
        :chart-end="getEndDate"
        precision="day"
        :no-overlap="true"
        width="100%"
        bar-start="start_date"
        bar-end="end_date"
    >
      <g-gantt-row v-for="(path, idx) in rowBarList" :bars="path.bars" :key="idx" :label="path.label"/>
    </g-gantt-chart>
  </div>
</template>

<script setup lang="ts">
import {computed, onMounted, Ref, ref} from "vue"
import {GanttBarObject, GGanttChart, GGanttRow} from "@infectoone/vue-ganttastic";
import {useIceTransportStore} from "../../store";
import {IPath, IWaybill, tTypeWay} from "../../types.ts";
import {storeToRefs} from "pinia";
import {DateTime} from "luxon";
import {getDate} from "../../utils/getDate.ts";

const {vessels, paths} = storeToRefs(useIceTransportStore())

interface IRowBar {
  label: string
  bars: GanttBarObject[]
}

const rowBarList: Ref<IRowBar[]> = ref([])

onMounted(() => {
  rowBarList.value = paths.value.map(path => {
    return {
      label: vessels.value?.find(vessel => vessel.id === path.vessel_id)?.name || '',
      bars: path.waybill.map((way, idx) => {
        const {start_date, end_date} = getDates(way, path, idx)

        return {
          start_date,
          end_date,
          ganttBarConfig: {
            id: `${path.vessel_id}_${way.point}_${way.event}`,
            style: {
              background: getBackground(way.event),
            }
          }
        }
      })
    }
  })
})

const getEndDate = computed(() => {
  const maxDate = paths.value
      .reduce((acc, date) => {
        return acc && new Date(acc) > new Date(date.end_date || date.start_date) ? acc : date.end_date || date.start_date
      }, '')

  const endDate = `${date.value(maxDate, "yyyy-MM-dd")} 23:59`
  const startDate = date.value(vessels.value[0].start_date)

  return startDate !== endDate ? endDate : date.value(DateTime.fromISO(vessels.value[0].start_date).plus({hours: 1}))
})

const date = computed(() => {
  return ((date: string, format: string) => {
    return getDate(date, format || 'yyyy-MM-dd HH:mm')
  })
})

const getDates = (way: IWaybill, path: IPath, idx: number) => {
  const start_date = date.value(way.dt)

  let end_date

  if (path.success && way.event === tTypeWay.FIN) {
    end_date = date.value(way.dt)
  } else if (way.event === tTypeWay.STUCK) {
    end_date = date.value(DateTime.fromISO(way.dt).plus({hours: 1}))
  } else {
    end_date = date.value(DateTime.fromISO(path.waybill[idx + 1].dt))
  }

  return {
    start_date,
    end_date
  }
}

const getBackground = (event: tTypeWay) => {
  if (event === tTypeWay.MOVE || event === tTypeWay.FIN) return 'green'
  if (event === tTypeWay.STUCK) return 'red'
  if (event === tTypeWay.FORMATION) return 'blue'
  return 'gray'
}
</script>

<style lang="scss" scoped>
//.scroll-gantt {
//  display: flex !important;
//  flex-wrap: nowrap !important;
//  overflow: auto;
//  overflow-y: hidden;
//}
</style>