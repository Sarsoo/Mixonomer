import React, { Component } from "react";
const axios = require('axios');

import showMessage from "../Toast.js"
import { Card, Button, ButtonGroup, CardContent, CardActions, Typography } from "@material-ui/core";

class Functions extends Component {

    constructor(props){
        super(props);

        this.runAllUsers = this.runAllUsers.bind(this);
        this.runStats = this.runStats.bind(this);
    }

    runAllUsers(event){
        axios.get('/api/playlist/run/users')
        .then((response) => {
            showMessage('Users Run');
        })
        .catch((error) => {
            showMessage(`Error Running All Users (${error.response.status})`);
        });
    }

    runStats(event){
        axios.get('/api/spotfm/playlist/refresh/users')
        .then((response) => {
            showMessage('Stats Run');
        })
        .catch((error) => {
            showMessage(`Error Running All Users (${error.response.status})`);
        });
    }

    render () {
        return ( 
            <div style={{maxWidth: '1000px', margin: 'auto', marginTop: '20px'}}>
                <Card align="center">
                    <CardContent>
                        <Typography variant="h4" color="textPrimary">Admin Functions</Typography>
                    </CardContent>
                    <CardActions>
                        <ButtonGroup variant="contained" color="primary" className="full-width">
                            <Button className="full-width button" onClick={this.runAllUsers}>Run All Users</Button>
                            <Button className="full-width button" onClick={this.runStats}>Run Stats</Button>
                        </ButtonGroup>
                    </CardActions>
                </Card>
            </div>
        );
    }
}

export default Functions;