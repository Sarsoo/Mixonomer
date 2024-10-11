import React, { Component } from "react";
const axios = require('axios');

import { Card, CardContent, Typography, Grid } from '@mui/material';

import showMessage from "../Toast.js"

/**
 * Running tasks card component
 */
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

    /**
     * Get tasks from API
     */
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
            <div style={{maxWidth: '1000px', margin: 'auto', marginTop: '20px'}}>

                {/* GRID OF TASK CARDS */}
                <Grid container spacing={4}>
                    { this.state.tasks.map((entry) => <TaskType url={entry.url} count={entry.count} times={entry.scheduled_times} key={entry.url}/>)}
                </Grid>
            </div>
        );
    }
}

/**
 * Grid of task cards
 * @param {*} props 
 * @returns Card compnent wrapped in grid cell
 */
function TaskType(props) {
    return (
        <Grid item xs={12} sm={6} md={4}>
            <Card align="center">
                <CardContent>
                    <Typography variant="body2" color="textSecondary">{props.url}: {props.count}</Typography>
                    {props.times.map((entry) => <Typography variant="body2" color="textSecondary">{entry}</Typography>)}
                </CardContent>
            </Card>
        </Grid>
    );
}

export default Tasks;