import React, { Component } from "react";
const axios = require('axios');

import { Card, Button, FormControl, TextField, InputLabel, Select, CardActions, CardContent, Typography, Grid } from '@material-ui/core';

import showMessage from "../Toast.js"

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

    componentDidMount(){
        this.setDescription('default');
    }

    setDescription(value){
        switch(value){
            case 'default':
                this.setState({
                    description: 'Merge playlists as-is with deduplication by spotify id'
                })
                break;
            case 'recents':
                this.setState({
                    description: "Select songs from playlists which have been added since a variable number of days"
                })
                break;
        }
    }

    handleInputChange(event){
        this.setState({
            [event.target.name]: event.target.value
        });
        this.setDescription(event.target.value);
    }

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
            <Card align="center">
                <CardContent>
                    <Grid container>
                        <Grid item xs={12}>
                            <Typography variant="h3">New</Typography>
                        </Grid>
                        <Grid item xs={4}>
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
                                >
                                    <option value="default">Default</option>
                                    <option value="recents">Recents</option>
                                </Select>
                            </FormControl>
                        </Grid>
                        <Grid item xs={8}>
                            <TextField
                                label="Name" 
                                variant="outlined" 
                                onChange={this.handleInputChange}
                                name="name"
                                value={this.state.name} />
                        </Grid>
                        <Grid item xs={12}>
                            <Typography variant="body2" color="textSecondary">{ this.state.description }</Typography>
                        </Grid>
                    </Grid>
                </CardContent>
                <CardActions>
                    <Button variant="contained" color="primary" className="full-width" onClick={this.handleSubmit}>Create</Button>
                </CardActions>
            </Card>
        );
    }

}

export default NewPlaylist;