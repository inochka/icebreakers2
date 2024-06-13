<template>
  <g-gantt-chart
      :chart-start="startDate(vessels[0].start_date)"
      :chart-end="`${date(paths.at(-1).end_date)} 23:59`"
      precision="day"
      bar-start="start_date"
      bar-end="end_date"
  >
    <g-gantt-row v-for="(path, idx) in rowBarList" :bars="path.bars" :key="idx" :label="path.label" />
  </g-gantt-chart>
</template>

<script setup lang="ts">
import {computed, onMounted, Ref, ref} from "vue"
import {GanttBarObject, GGanttChart, GGanttRow} from "@infectoone/vue-ganttastic";
import {useVesselsStore} from "../../store";
import {DateTime} from "luxon";
import {tTypeWay} from "../../types.ts";

const {vessels, paths} = useVesselsStore()

interface IRowBar {
  label: string
  bars: GanttBarObject[]
}

const rowBarList: Ref<IRowBar[]> = ref([])

onMounted(() => {
  rowBarList.value = paths.map(path => {
    return {
      label: vessels?.find(vessel => vessel.id === path.id)?.name || '',
      bars: path.waybill.map((way) => {
        return {
          start_date: `${date.value(way.time)} 00:00`,
          end_date: `${date.value(way.time)} 23:59`,
          ganttBarConfig: {
            id: `${path.id}_${way.point}_${way.event}`,
            style: {
              background: getBackground(way.event, path.success),
            }
          }
        }
      })
    }
  })
})

const date = computed(() => {
  return ((date: string) => {
   return DateTime.fromFormat(date, 'dd.MM.yyyy').toFormat('yyyy-MM-dd')
  })
})

const startDate = computed(() => {
  return ((date: string) => {
    return date.replace('T', ' ').slice(0, date.length - 3)
  })
})

const getBackground = (event: tTypeWay, success: boolean) => {
  if (event === tTypeWay.WAIT || event === tTypeWay.FIN) return success ? 'green' : 'red'
  if (event === tTypeWay.FORMATION) return 'blue'
  return 'gray'
}
</script>
