import React, { Component } from "react";
const axios = require('axios');

import showMessage from "../Toast.js"
import { Card, Button, ButtonGroup, CardContent, CardActions, Typography } from "@mui/material";

/**
 * Admin functions card component
 */
class Functions extends Component {

    constructor(props){
        super(props);

        this.runAllUsers = this.runAllUsers.bind(this);
        this.runStats = this.runStats.bind(this);
    }

    /**
     * Make run all playlists request of API
     * @param {*} event Event data
     */
    runAllUsers(event){
        axios.get('/api/playlist/run/users')
        .then((response) => {
            showMessage('Users Run');
        })
        .catch((error) => {
            showMessage(`Error Running All Users (${error.response.status})`);
        });
    }

    /**
     * Make run stats request of API
     * @param {*} event Event data
     */
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

                        {/* TITLE */}
                        <Typography variant="h4" color="textPrimary">Admin Functions</Typography>
                    </CardContent>
                    <CardActions>
                        <ButtonGroup variant="contained" color="secondary" className="full-width">

                            {/* RUN ALL PLAYLISTS BUTTON */}
                            <Button className="full-width button" onClick={this.runAllUsers}>Run All Users</Button>
                            
                            {/* RUN STATS BUTTON */}
                            <Button className="full-width button" onClick={this.runStats}>Run Stats</Button>
                        </ButtonGroup>
                    </CardActions>
                </Card>
            </div>
        );
    }
}

export default Functions;