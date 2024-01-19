import echarts from "echarts/lib/export";

const pieColorMap = {
  'AC': {color: '#19be6b'},
  'WA': {color: '#ed3f14'},
  'TLE': {color: '#ff9300'},
  'MLE': {color: '#f7de00'},
  'RE': {color: '#ff6104'},
  'CE': {color: '#80848f'},
  'PAC': {color: '#2d8cf0'}
}

function getItemColor (obj) {
  return pieColorMap[obj.name].color
}

const pie = {
  legend: {
    left: 'center',
    top: '10',
    orient: 'horizontal',
    data: ['AC', 'WA']
  },
  series: [
    {
      name: 'Summary',
      type: 'pie',
      radius: '80%',
      center: ['50%', '55%'],
      itemStyle: {
        normal: {color: getItemColor}
      },
      data: [
        {value: 0, name: 'WA'},
        {value: 0, name: 'AC'}
      ],
      label: {
        normal: {
          position: 'inner',
          show: true,
          formatter: '{b}: {c}\n {d}%',
          textStyle: {
            fontWeight: 'bold'
          }
        }
      }
    }
  ]
}


const largePie = {
  legend: {
    left: 'center',
    top:
      '10',
    orient:
      'horizontal',
    itemGap:
      20,
    data:
      ['AC', 'RE', 'WA', 'TLE', 'PAC', 'MLE']
  },
  series: [
    {
      name: 'Detail',
      type: 'pie',
      radius: ['45%', '70%'],
      center: ['50%', '55%'],
      itemStyle: {
        normal: {color: getItemColor}
      },
      data: [
        {value: 0, name: 'RE'},
        {value: 0, name: 'WA'},
        {value: 0, name: 'TLE'},
        {value: 0, name: 'AC'},
        {value: 0, name: 'MLE'},
        {value: 0, name: 'PAC'}
      ],
      label: {
        normal: {
          formatter: '{b}: {c}\n {d}%'
        }
      },
      labelLine: {
        normal: {}
      }
    },
    {
      name: 'Summary',
      type: 'pie',
      radius: '30%',
      center: ['50%', '55%'],
      itemStyle: {
        normal: {color: getItemColor}
      },
      data: [
        {value: '0', name: 'WA'},
        {value: 0, name: 'AC', selected: true}
      ],
      label: {
        normal: {
          position: 'inner',
          formatter: '{b}: {c}\n {d}%'
        }
      }
    }
  ]
}

const radarGraph = {
    color: ['#FF917C'],
    legend: {},
    tooltip: {
      trigger: 'axis'
    },
    radar: {
      indicator: [
        { text: '자료구조', max: 30000, color: '#000000', },
        { text: '구현', max: 65000, color: '#000000', },
        { text: '수학', max: 16000, color: '#000000', },
        { text: '탐색', max: 38000, color: '#000000', },
        { text: '정렬', max: 52000, color: '#000000', },
      ],
      center: ['50%', '50%'],
      axisName:{
        fontWeight: 'bold'
      },
      splitArea: {
        areaStyle: {
          color: ['rgba(255,255,255,0)', 'rgba(255,255,255,0)', 'rgba(255,255,255,0)', 'rgba(255,255,255,0)'],
        }
      },
      splitNumber: 4,
    },
    series: [
      {
        name: 'ACM Score',
        type: 'radar',
        emphasis:{
          areaStyle:{
            color: '#FF917C',
            shadowColor: '#FF917C'
          },
        },
        data: [
          {
            value: [20000, 3000, 4200, 35000, 50000, 18000],
            tooltip: {
              trigger: 'item',
              backgroundColor: 'rgba(255,145,124,0.22)',
              textStyle: {
                color: '#1C1C1C',
                fontWeight: 'bold'
              }

            },
          },
        ],
      }
    ]
}

export { pie, largePie, radarGraph }
