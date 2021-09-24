import React, { Component } from 'react';
export const getClassesPieChart = (api_data) => {
  let pie_data_classes = {
    labels: [
      'Used Classes Count',
      'Unused Classes Count',
    ],
    datasets: [{
      data: [api_data.used_classes_count, api_data.total_classes_count - api_data.used_classes_count],
      backgroundColor: [
        '#36A2EB',
        '#FF6384',
      ],
      hoverBackgroundColor: [
        '#36A2EB',
        '#FF6384',
      ]
    }]
  };
  return pie_data_classes;
};

export const getMethodsPieChart = (api_data) => {
  let pie_data_methods = {
    labels: [
      'Used Method Count',
      'Unused Method Count',
    ],
    datasets: [{
      data: [api_data.used_methods_count, api_data.total_methods_count - api_data.used_methods_count],
      backgroundColor: [
        '#36A2EB',
        '#FF6384',
      ],
      hoverBackgroundColor: [
        '#36A2EB',
        '#FF6384',
      ]
    }]
  };
  return pie_data_methods;
};

export const barChartOptions =  {
    scales: {
        xAxes: [{
            ticks: {
                beginAtZero:true
            }
        }]
    }
}

export const getUsedUnusedPlotData = (libNames, totalCounts, usedCounts) => {
  return {
          labels: libNames,
          datasets: [{
            label: 'Total Classes',
            data: totalCounts,
            backgroundColor: 'rgba(255,99,132,0.2)',
            borderColor: 'rgba(255,99,132,1)',
            borderWidth: 1,
            hoverBackgroundColor: 'rgba(255,99,132,0.4)',
            hoverBorderColor: 'rgba(255,99,132,1)',
          },
          {
            label: 'Used Classes',
            data: usedCounts,
            backgroundColor: '#71B37C',
            borderColor: '#71B37C',
            hoverBackgroundColor: '#71B37C',
            hoverBorderColor: '#71B37C',
          }
          ]
        }
}

export const processLibraryDataForCharts = (libraries) => {
    let lib_names = [];
    let used_counts = [];
    let total_counts = [];
    let library_classes_obj = {}
    let library_methods = []
    for (let i = 0; i < libraries.length; i++) {
      let libname = libraries[i].library_name;
      lib_names.push(libname);
      total_counts.push(libraries[i].total_classes_count);
      used_counts.push(libraries[i].used_classes_count);
      let lib_classes = libraries[i].classes;
      library_classes_obj[libname] = {
        classes: lib_classes,
      }

      for (let j = 0; j < lib_classes.length; j++) {
        let lib_class = lib_classes[j]
        lib_class.total_methods_verbose.forEach(function (m) {
          library_methods.push({
            value: m,
            label: m
          })
        })
      }
    }

    return { lib_names, used_counts, total_counts, library_classes_obj, library_methods } 
}

export const getDebloatStatisticsTable = (info) => {
    return (
    <table style={{ width: '100%' }}>
        <tr>
          <th></th>
          <th style={{textAlign: 'left'}}>Before</th>
          <th style={{textAlign: 'left'}}>After</th>
          <th style={{textAlign: 'left'}}>% Reduction</th>
        </tr>
        <tr>
          <td>App Size</td>
          <td>{info["app_size_before"]} Bytes</td>
          <td>{info["app_size_after"]} Bytes</td>
          <td>{info["app_size_reduction"]}%</td>
        </tr>
        <tr>
          <td>Lib Size</td>
          <td>{info["libs_size_before"]} Bytes</td>
          <td>{info["libs_size_after"]} Bytes</td>
          <td>{info["libs_size_reduction"]}%</td>
        </tr>
        <tr>
          <td>Num of App Methods</td>
          <td>{info["app_num_methods_before"]}</td>
          <td>{info["app_num_methods_after"]}</td>
          <td>{info["app_num_methods_reduction"]}%</td>
        </tr>
        <tr>
          <td>Num of Lib Methods</td>
          <td>{info["libs_num_methods_before"]}</td>
          <td>{info["libs_num_methods_after"]}</td>
          <td>{info["libs_num_methods_reduction"]}%</td>
        </tr>
  </table>
  )
}