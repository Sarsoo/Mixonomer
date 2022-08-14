import React, { Component } from "react";
import { Link } from "react-router-dom";
import { Button, ButtonGroup, Typography, Card, CardActions, CardContent, Grid } from '@material-ui/core';
const axios = require('axios');

import showMessage from "../Toast.js"
import Progress from "../Util/circularProgress.js";

/**
 * Top-level object for hosting playlist card grid with new/run all buttons
 */
class PlaylistsView extends Component {

    /**
     * Trigger loading playlist data during init
     * @param {*} props Component properties 
     */
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

    /**
     * Get playlist data from API and set state with results
     */
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

    /**
     * Post run playlist action to API
     * @param {*} name Playlist name to run 
     * @param {*} event Event data
     */
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

    /**
     * Post delete playlist action to API
     * @param {*} name Playlist name to delete
     * @param {*} event Event data
     */
    handleDeletePlaylist(name, event){
        axios.delete('/api/playlist', { params: { name: name } })
        .then((response) => {
            showMessage(`${name} Deleted`);
            this.getPlaylists();
        }).catch((error) => {
            showMessage(`Error Deleting ${name} (${error.response.status})`);
        });
    }

    /**
     * Post run all playlists action to API
     * @param {*} event Event data
     */
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
        
        // Show spinning loading circle until loaded playlist data

        const grid =   <PlaylistGrid playlists={this.state.playlists} 
                            handleRunPlaylist={this.handleRunPlaylist} 
                            handleDeletePlaylist={this.handleDeletePlaylist}
                            handleRunAll={this.handleRunAll}/>;

        return this.state.isLoading ? <Progress /> : grid;
    }
}

/**
 * Playlist grid component for new/run all buttons and playlist cards
 * @param {*} props Component properties
 * @returns Grid component
 */
function PlaylistGrid(props){
    return (
        <Grid container 
                spacing={3} 
                direction="row"
                justifyContent="flex-start"
                alignItems="flex-start"
                style={{padding: 24}}>

            {/* BUTTON BLOCK (NEW/RUN ALL) */}
            <Grid item xs={12} sm={6} md={2}>
                <ButtonGroup 
                    color="primary"
                    orientation="vertical" 
                    className="full-width">
                    <Button component={Link} to='playlists/new' >New</Button>
                    <Button onClick={props.handleRunAll}>Run All</Button>
                </ButtonGroup>
            </Grid>

            {/* PLAYLIST CARDS */}
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

/**
 * Playlist card component with view/run/delete buttons
 * @param {*} props Component properties
 * @returns Playlist card component
 */
function PlaylistCard(props){
    return (
        <Grid item xs>
            <Card>

                {/* NAME TITLE */}
                <CardContent>
                    <Typography variant="h4" component="h2">
                    { props.playlist.name }
                    </Typography>

                    {"lastfm_stat_percent" in props.playlist && 
                    props.playlist.lastfm_stat_percent != null && 
                        <Typography component="h6" style={{color: "#b3b3b3"}}>
                            { Math.round(props.playlist.lastfm_stat_percent) }%
                        </Typography>
                    }
                </CardContent>

                {/* BUTTONS */}
                <CardActions>
                    <ButtonGroup 
                    color="secondary" 
                    variant="contained">

                        {/* VIEW */}
                        <Button component={Link} to={getPlaylistLink(props.playlist.name)}>View</Button>

                        {/* RUN */}
                        <Button onClick={(e) => props.handleRunPlaylist(props.playlist.name, e)}>Run</Button>
                        
                        {/* DELETE */}
                        <Button onClick={(e) => props.handleDeletePlaylist(props.playlist.name, e)}>Delete</Button>
                    </ButtonGroup>
                </CardActions>
            </Card>
        </Grid>
    );
}

/**
 * Get URL for playlist given name
 * @param {*} playlistName Subject playlist name
 * @returns URL string
 */
function getPlaylistLink(playlistName){
    return `/app/playlist/${playlistName}/edit`;
}

export default PlaylistsView;