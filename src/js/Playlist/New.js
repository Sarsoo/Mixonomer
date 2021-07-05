import React, { Component } from "react";
const axios = require('axios');

import { Card, Button, FormControl, TextField, InputLabel, Select, CardActions, CardContent, Typography, Grid } from '@material-ui/core';

import showMessage from "../Toast.js"

/**
 * New playlist card
 */
class NewPlaylist extends Component {

    constructor(props) {
        super(props);
        this.state = {
            name: '',
            type: 'default',
            description: ''
        }
        this.handleInputChange = this.handleInputChange.bind(this);
        this.handleSubmit = this.handleSubmit.bind(this);
    }

    /** Set initial state of playlist type description */
    componentDidMount(){
        this.setDescription('default');
    }

    /**
     * Set playlist type description
     * @param {*} value Playlist type string to match
     */
    setDescription(value){
        switch(value){
            case 'default':
                this.setState({
                    description: 'Merge playlists as-is with deduplication by Spotify id'
                })
                break;
            case 'recents':
                this.setState({
                    description: "Filter added playlists for recently added tracks, optionally add monthly playlists"
                })
                break;
            case 'fmchart':
                this.setState({
                    description: "Include Last.fm track chart data with varying time ranges"
                })
                break;
        }
    }

    /**
     * Handle input changes by setting state
     * @param {*} event 
     */
    handleInputChange(event){
        this.setState({
            [event.target.name]: event.target.value
        });
        this.setDescription(event.target.value);
    }

    /**
     * Validate input and make new playlist API request
     * @param {*} event 
     */
    handleSubmit(event){
        var name = this.state.name;
        this.setState({
            name: ''
        });

        if(name.length != 0){
            axios.get('/api/playlists')
            .then((response) => {

                var names = response.data.playlists.map(entry => entry.name)

                var sameName = names.includes(this.state.name);
                if(sameName == false){
                    axios.put('/api/playlist', {
                        name: name,
                        parts: [],
                        playlist_references: [],
                        shuffle: false,
                        type: this.state.type,
                    }).then((response) => {
                        showMessage(`${this.state.name} Created`);
                    }).catch((error) => {
                        showMessage(`Error Creating Playlist (${error.response.status})`);
                    });
                }else{
                    showMessage('Named Playlist Already Exists');
                }
            })
            .catch((error) => {
                showMessage(`Error Getting Playlists (${error.response.status})`);
            });
        }else{
            showMessage('Enter Name');
        }
    }

    render(){
        return (
            <div style={{maxWidth: '500px', margin: 'auto', marginTop: '20px'}}>
            <Card align="center">
                <CardContent>
                    <Grid container spacing={5}>

                        {/* TITLE */}
                        <Grid item xs={12}>
                            <Typography variant="h3">New</Typography>
                        </Grid>

                        {/* PLAYLIST TYPE DROPDOWN */}
                        <Grid item xs={12} sm={4}>
                            <FormControl variant="filled">
                                <InputLabel htmlFor="type-select">Type</InputLabel>
                                <Select
                                native
                                value={this.state.type}
                                onChange={this.handleInputChange}
                                inputProps={{
                                    name: 'type',
                                    id: 'type-select',
                                }}
                                className="full-width"
                                >
                                    <option value="default">Default</option>
                                    <option value="recents">Currents</option>
                                    <option value="fmchart">Last.fm Chart</option>
                                </Select>
                            </FormControl>
                        </Grid>

                        {/* PLAYLIST NAME TEXTBOX */}
                        <Grid item xs={12} sm={8}>
                            <TextField
                                label="Name" 
                                variant="outlined" 
                                onChange={this.handleInputChange}
                                name="name"
                                value={this.state.name} 
                                className="full-width" />
                        </Grid>

                        {/* PLAYLIST DESCRIPTION TEXT */}
                        <Grid item xs={12}>
                            <Typography variant="body2" color="textSecondary">{ this.state.description }</Typography>
                        </Grid>
                    </Grid>
                </CardContent>

                {/* SUBMIT BUTTON */}
                <CardActions>
                    <Button variant="contained" color="secondary" className="full-width" onClick={this.handleSubmit}>Create</Button>
                </CardActions>
            </Card>
            </div>
        );
    }

}

export default NewPlaylist;