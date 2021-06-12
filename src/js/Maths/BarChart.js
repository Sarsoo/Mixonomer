import React, { Component } from "react";
import { Chart, BarElement, BarController, LinearScale, CategoryScale, Legend, Title, Tooltip } from 'chart.js';

Chart.register(BarElement, BarController, LinearScale, CategoryScale, Legend, Title, Tooltip);

/**
 * Bar chart component using Chart.js
 */
class BarChart extends Component {

    constructor(props) {
        super(props);
        this.chartRef = React.createRef();
    }

    /**
     * Load data from react properties
     */
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
              indexAxis: this.props.indexAxis, // vertical or horizontal bars
              plugins: {
                legend : {
                    display : true,
                    labels: {
                      color: 'white'
                    }
                }
              },
              elements: {
                  bar : {
                    backgroundColor: 'rgb(255, 255, 255)',
                    borderWidth: 2,
                    borderColor: 'rgb(0, 0, 0)'
                  }
              },
              scales: {
                y: {
                  ticks: {
                      color: "#d8d8d8",
                      font: {
                        size: 16
                      }
                  }
                },
                x: {
                  ticks: {
                      color: "#d8d8d8",
                      font: {
                        size: 16
                      }
                  }
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

export default BarChart;