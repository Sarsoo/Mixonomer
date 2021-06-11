import React, { Component } from "react";
import { Chart, BarElement, BarController, LinearScale, CategoryScale, Legend, Title, Tooltip } from 'chart.js';

Chart.register(BarElement, BarController, LinearScale, CategoryScale, Legend, Title, Tooltip);

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
                        size: 20
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