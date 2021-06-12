import React, { Component } from "react";
import { Chart, ArcElement, DoughnutController, Legend, Title, Tooltip } from 'chart.js';

Chart.register(ArcElement, DoughnutController, Legend, Title, Tooltip);

var pieColours = ['rgb(55, 61, 255)', //blue
'rgb(255, 55, 61)', //red
'rgb(7, 211, 4)', //green
'rgb(228, 242, 31)', //yellow
'rgb(31, 242, 221)', //light blue
'rgb(242, 31, 235)', //pink
'rgb(242, 164, 31)'];

/**
 * Pie chart component using Chart.js
 */
class PieChart extends Component {

    constructor(props) {
        super(props);
        this.chartRef = React.createRef();
    }

    /**
     * Load data from react properties
     */
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
              plugins: {
                legend : {
                    display : true,
                    labels: {
                      color: 'white'
                    }
                }
              },
              layout: {
                padding: this.props.padding
              },
              elements: {
                  arc : {
                    backgroundColor: [...pieColours, ...pieColours, ...pieColours],
                    borderWidth: 2,
                    borderColor: 'rgb(0, 0, 0)'
                  }
              }
          }
        });
    }

    /**
     * Re-apply data to chart on update
     */
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