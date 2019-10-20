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
                  display : false
              },
              elements: {
                  arc : {
                    backgroundColor: ['rgb(55, 61, 255)', 'rgb(255, 55, 61)'],
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