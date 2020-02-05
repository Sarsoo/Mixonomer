import React, { Component } from "react";
import { Link } from "react-router-dom";
import { Button, ButtonGroup, Typography, Card, Grid, CircularProgress } from '@material-ui/core';
import CardActions from '@material-ui/core/CardActions';
import CardContent from '@material-ui/core/CardContent';
const axios = require('axios');

import showMessage from "../Toast.js"

class PlaylistsView extends Component {

    constructor(props){
        super(props);
        this.state = {
            isLoading: true
        }
        this.getPlaylists();
        this.handleRunPlaylist = this.handleRunPlaylist.bind(this);
        this.handleDeletePlaylist = this.handleDeletePlaylist.bind(this);
        this.handleRunAll = this.handleRunAll.bind(this);
    }

    getPlaylists(){
        var self = this;
        axios.get('/api/playlists')
        .then((response) => {

            var playlists = response.data.playlists.slice();
            
            playlists.sort(function(a, b){
                if(a.name.toLowerCase() < b.name.toLowerCase()) { return -1; }
                if(a.name.toLowerCase() > b.name.toLowerCase()) { return 1; }
                return 0;
            });

            self.setState({
                playlists: playlists,
                isLoading: false
            });
        })
        .catch((error) => {
            showMessage(`Error Getting Playlists (${error.response.status})`);
        });
    }

    handleRunPlaylist(name, event){
        axios.get('/api/user')
        .then((response) => {
            if(response.data.spotify_linked == true){
                axios.get('/api/playlist/run', {params: {name: name}})
                .then((response) => {
                    showMessage(`${name} ran`);
                })
                .catch((error) => {
                    showMessage(`Error Running ${name} (${error.response.status})`);
                });
            }else{
                showMessage(`Link Spotify Before Running`);
            }
        }).catch((error) => {
            showMessage(`Error Running ${this.state.name} (${error.response.status})`);
        });
    }

    handleDeletePlaylist(name, event){
        axios.delete('/api/playlist', { params: { name: name } })
        .then((response) => {
            showMessage(`${name} Deleted`);
            this.getPlaylists();
        }).catch((error) => {
            showMessage(`Error Deleting ${name} (${error.response.status})`);
        });
    }

    handleRunAll(event){
        axios.get('/api/user')
        .then((response) => {
            if(response.data.spotify_linked == true){
                axios.get('/api/playlist/run/user')
                .then((response) => {
                    showMessage("All Playlists Ran");
                })
                .catch((error)  => {
                    showMessage(`Error Running All (${error.response.status})`);
                });
            }else{
                showMessage(`Link Spotify Before Running`);
            }
        }).catch((error) => {
            showMessage(`Error Running ${this.state.name} (${error.response.status})`);
        });
    }

    render() {
        
        const grid =   <PlaylistGrid playlists={this.state.playlists} 
                            handleRunPlaylist={this.handleRunPlaylist} 
                            handleDeletePlaylist={this.handleDeletePlaylist}
                            handleRunAll={this.handleRunAll}/>;

        return this.state.isLoading ? <CircularProgress /> : grid;
    }
}

function PlaylistGrid(props){
    return (
        <Grid container 
                spacing={3} 
                direction="row"
                justify="flex-start"
                alignItems="flex-start"
                style={{padding: '24px'}}>
            <Grid item xs>
                <ButtonGroup 
                    color="primary"
                    orientation="vertical" 
                    className="full-width">
                    <Button component={Link} to='playlists/new' >New</Button>
                    <Button onClick={props.handleRunAll}>Run All</Button>
                </ButtonGroup>
            </Grid>
            { props.playlists.length == 0 ? (
                <Grid item xs={12} sm={6} md={3}>
                    <Typography variant="h5" component="h2">No Playlists</Typography>
                </Grid>
            ) : (
                props.playlists.map((playlist) => <PlaylistCard playlist={ playlist } 
                                                        handleRunPlaylist={props.handleRunPlaylist} 
                                                        handleDeletePlaylist={props.handleDeletePlaylist}
                                                        key={ playlist.name }/>)
            )}
        </Grid>
    );
}

function PlaylistCard(props){
    return (
        <Grid item xs>
            <Card>
                <CardContent>
                    <Typography variant="h4" component="h2">
                    { props.playlist.name }
                    </Typography>
                </CardContent>
                <CardActions>
                    <ButtonGroup 
                    color="primary" 
                    variant="contained">
                        <Button component={Link} to={getPlaylistLink(props.playlist.name)}>View</Button>
                        <Button onClick={(e) => props.handleRunPlaylist(props.playlist.name, e)}>Run</Button>
                        <Button onClick={(e) => props.handleDeletePlaylist(props.playlist.name, e)}>Delete</Button>
                    </ButtonGroup>
                </CardActions>
            </Card>
        </Grid>
    );
}

function getPlaylistLink(playlistName){
    return `/app/playlist/${playlistName}/edit`;
}

export default PlaylistsView;