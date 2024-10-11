import React, { Component } from "react";
const axios = require('axios');

import { Card, Button, CardContent, CardActions, Typography, TextField, Grid } from "@mui/material";

import showMessage from "../Toast.js"

/**
 * Last.fm username setting card
 */
class LastFM extends Component {

    constructor(props){
        super(props);
        this.state = {
            lastfm_username: null,
            isLoading: true
        }
        this.getUserInfo();

        this.handleChange = this.handleChange.bind(this);
        this.handleSubmit = this.handleSubmit.bind(this);
    }

    /**
     * Get user info from API, set current username to state
     */
    getUserInfo(){
        axios.get('/api/user')
        .then((response) => {

            var username = response.data.lastfm_username;

            if(username == null){
                username = '';
            }

            this.setState({
                lastfm_username: username,
                isLoading: false
            })
        })
        .catch((error) => {
            showMessage(`error getting user info (${error.response.status})`);
        });
    }

    /**
     * Handle input box state change
     * @param {*} event Event data
     */
    handleChange(event){
        this.setState({
            'lastfm_username': event.target.value
        });
    }

    /**
     * Handle submit button, post API change request
     * @param {*} event Event data
     */
    handleSubmit(event){

        var username = this.state.lastfm_username;

        if(username == ''){
            username = null
        }

        axios.post('/api/user',{
            lastfm_username: username
        }).then((response) => {
            showMessage('saved');
        }).catch((error) => {
            showMessage(`error saving (${error.response.status})`);
        });

        event.preventDefault();

    }

    render(){
        const table =
            <div style={{maxWidth: '400px', margin: 'auto', marginTop: '20px'}}>
                <Card align="center">
                    <form onSubmit={this.handleSubmit}>
                        <CardContent>
                            <Grid container spacing={3}>

                                {/* TITLE */}
                                <Grid item className="full-width">
                                    <Typography variant="h4" color="textPrimary">Last.fm Username</Typography>
                                </Grid>

                                {/* USERNAME TEXTBOX */}
                                <Grid item className="full-width">
                                    <TextField
                                        label="last.fm Username" 
                                        variant="outlined"
                                        onChange={this.handleChange}
                                        name="current"
                                        value={this.state.lastfm_username} 
                                        className="full-width" />
                                </Grid>
                            </Grid>
                        </CardContent>

                        {/* SUBMIT BUTTON */}
                        <CardActions>
                            <Button color="secondary" type="submit" variant="contained" className="full-width">Save</Button>
                        </CardActions>
                    </form>
                </Card>
            </div>;

        const loadingMessage = <p className="center-text text-no-select">Loading...</p>;

        return this.state.isLoading ? loadingMessage : table;
    }
}

export default LastFM;