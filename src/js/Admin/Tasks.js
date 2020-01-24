import React, { Component } from "react";
const axios = require('axios');

import showMessage from "../Toast.js"

class Tasks extends Component {

    constructor(props){
        super(props);
        this.state = {
            total_tasks: 0,
            tasks: [],
            schedule_times: []
        }
        this.getTasks();
    }

    getTasks(){
        var self = this;
        axios.get('/api/admin/tasks')
        .then((response) => {
            self.setState({
                total_tasks: response.data.total_tasks,
                tasks: response.data.tasks
            });
        })
        .catch((error) => {
            showMessage(`Error Getting Tasks (${error.response.status})`);
        });
    }

    render () {
        return ( 
            <table className="app-table max-width">
                <thead>
                    <tr>
                        <th>
                           <h1 className="text-no-select full-width center-text ui-text">Running Tasks</h1> 
                        </th>
                    </tr>
                </thead>
                { this.state.tasks.map((entry) => <TaskType url={entry.url} count={entry.count} times={entry.scheduled_times} key={entry.url}/>)}
                <tbody>
                    <tr>
                        <td className="text-no-select full-width center-text ui-text" colSpan='2'>
                            <b>{this.state.total_tasks}</b> Currently Running
                        </td>
                    </tr>
                </tbody>
        </table>);
    }
}

function TaskType(props) {
    return (
        <tbody>
            <tr>
                <td className="text-no-select full-width center-text ui-text" colSpan='2'>
                    {props.url}: {props.count}
                </td>
            </tr>
            {props.times.map((entry) => <tr key={entry}>
                <td colSpan='2' className="text-no-select full-width center-text ui-text">
                    {entry}
                </td>
            </tr>)}
        </tbody>
    );
}

export default Tasks;