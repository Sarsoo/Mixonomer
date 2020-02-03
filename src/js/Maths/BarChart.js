import React, { Component } from "react";
var Chart = require('chart.js');

class BarChart extends Component {

    constructor(props) {
        super(props);
        this.chartRef = React.createRef();
    }

    componentDidMount() {
        this.chart = new Chart(this.chartRef.current, {
          type: 'bar',
          data: {
            labels: this.props.data.map(d => d.label),
            datasets: [{
              label: this.props.title,
              data: this.props.data.map(d => d.value),
              backgroundColor: this.props.color
            }]
          },
          options: {
              legend : {
                  display : false
              },
              elements: {
                  rectangle : {
                    backgroundColor: 'rgb(255, 255, 255)'
                  }
              },
              scales: {
                yAxes: [{
                  ticks: {
                      fontColor: "#d8d8d8",
                      fontSize: 16,
                      stepSize: 1,
                      beginAtZero: true
                  }
              }],
              xAxes: [{
                  ticks: {
                      fontColor: "#d8d8d8",
                      fontSize: 16,
                      stepSize: 1
                  }
              }]
              }
          }
        });
    }

    componentDidUpdate() {
      this.chart.data.labels = this.props.data.map(d => d.label);
      this.chart.data.datasets[0].data = this.props.data.map(d => d.value);
      this.chart.update();
    }
    
    render() {
        return (
            <canvas ref={this.chartRef} />
        );
    }    
}

export default BarChart;