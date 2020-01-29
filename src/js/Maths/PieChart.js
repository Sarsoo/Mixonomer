import React, { Component } from "react";
var Chart = require('chart.js');

class PieChart extends Component {

    constructor(props) {
        super(props);
        this.chartRef = React.createRef();
    }

    componentDidMount() {
        this.chart = new Chart(this.chartRef.current, {
          type: 'doughnut',
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
                  display : true,
                  labels: {
                    fontColor: 'white'
                  }
              },
              elements: {
                  arc : {
                    backgroundColor: ['rgb(55, 61, 255)', //blue
                      'rgb(255, 55, 61)', //red
                      'rgb(7, 211, 4)', //green
                      'rgb(228, 242, 31)', //yellow
                      'rgb(31, 242, 221)', //light blue
                      'rgb(242, 31, 235)', //pink
                      'rgb(242, 164, 31)', //orange
                      'rgb(55, 61, 255)', //blue
                      'rgb(255, 55, 61)', //red
                      'rgb(7, 211, 4)', //green
                      'rgb(228, 242, 31)', //yellow
                      'rgb(31, 242, 221)', //light blue
                      'rgb(242, 31, 235)', //pink
                      'rgb(242, 164, 31)', //orange
                      'rgb(55, 61, 255)', //blue
                      'rgb(255, 55, 61)', //red
                      'rgb(7, 211, 4)', //green
                      'rgb(228, 242, 31)', //yellow
                      'rgb(31, 242, 221)', //light blue
                      'rgb(242, 31, 235)', //pink
                      'rgb(242, 164, 31)' //orange
                    ],
                    borderWidth: 2,
                    borderColor: 'rgb(0, 0, 0)'
                  }
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

export default PieChart;