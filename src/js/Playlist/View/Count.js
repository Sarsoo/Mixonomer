import React, { Component } from "react";
const axios = require('axios');

import { Card, Button, CardActions, CardContent, Typography, Grid } from '@material-ui/core';

import showMessage from "../../Toast.js"

const LazyPieChart = React.lazy(() => import("../../Maths/PieChart"))

export class Count extends Component {

    constructor(props){
        super(props);
        this.state = {
            playlist: {
                lastfm_stat_album_count: 0,
                lastfm_stat_artist_count: 0,
                lastfm_stat_count: 0,

                lastfm_stat_album_percent: 0,
                lastfm_stat_artist_percent: 0,
                lastfm_stat_percent: 0,

                lastfm_stat_last_refresh: ''
            },
            name: props.name,
            lastfm_refresh: 'never',
            lastfm_percent: 0,
            count: 0,
            isLoading: true
        }
        this.getUserInfo();

        this.updateStats = this.updateStats.bind(this);
    }

    getUserInfo(){
        axios.get(`/api/playlist?name=${ this.state.name }`)
        .then((response) => {
            if(response.data.lastfm_stat_last_refresh != undefined){
                this.setState({
                    playlist: response.data,
                    isLoading: false
                })
            }else{
                showMessage('No Stats For This Playlist');
            }
        })
        .catch((error) => {
            showMessage(`Error Getting Playlist Info (${error.response.status})`);
        });
    }

    updateStats(){
        axios.get(`/api/spotfm/playlist/refresh?name=${ this.state.name }`)
        .then((response) => {
            showMessage('Stats Refresh Queued');
        })
        .catch((error) => {
            if(error.response.status == 401){
                showMessage('Missing Either Spotify or Last.fm link');
            }else{
                showMessage(`Error Refreshing (${error.response.status})`);
            }
        });
    }

    render() {
        return (
            <div style={{margin: 'auto', marginTop: '20px'}}>
            <Card align="center">
                <CardContent>
                    <Grid container>
                        <Grid item xs={12}>
                            <Typography variant="body2">Scrobble Count: <b>{this.state.playlist.lastfm_stat_count.toLocaleString()} / {this.state.playlist.lastfm_stat_percent}%</b></Typography>
                        </Grid>
                        <Grid item xs={12}>
                            <Typography variant="body2">Album Count: <b>{this.state.playlist.lastfm_stat_album_count.toLocaleString()} / {this.state.playlist.lastfm_stat_album_percent}%</b></Typography>
                        </Grid>
                        <Grid item xs={12}>
                            <Typography variant="body2">Artist Count: <b>{this.state.playlist.lastfm_stat_artist_count.toLocaleString()} / {this.state.playlist.lastfm_stat_artist_percent}%</b></Typography>
                        </Grid>
                        <Grid item xs={12}>
                            <Typography variant="body2">Last Updated <b>{this.state.playlist.lastfm_stat_last_refresh.toLocaleString()}</b></Typography>
                        </Grid>
                        <React.Suspense fallback={<LoadingMessage/>}>
                            <Grid item xs={12} sm={12} md={4}>
                                <LazyPieChart data={[{
                                    "label": `${this.state.playlist.name} Tracks`,
                                    "value": this.state.playlist.lastfm_stat_percent
                                },{
                                    "label": 'Other',
                                    "value": 100 - this.state.playlist.lastfm_stat_percent
                                }]} 
                                title={this.state.playlist.name}/>
                            </Grid>
                            <Grid item xs={12} sm={12} md={4}>
                            <LazyPieChart data={[{
                                "label": `${this.state.playlist.name} Albums`,
                                "value": this.state.playlist.lastfm_stat_album_percent
                            },{
                                "label": 'Other',
                                "value": 100 - this.state.playlist.lastfm_stat_album_percent
                            }]} 
                            title={this.state.playlist.name}/>
                            </Grid>
                            <Grid item xs={12} sm={12} md={4}>
                                <LazyPieChart data={[{
                                    "label": `${this.state.playlist.name} Artists`,
                                    "value": this.state.playlist.lastfm_stat_artist_percent
                                },{
                                    "label": 'Other',
                                    "value": 100 - this.state.playlist.lastfm_stat_artist_percent
                                }]} 
                                title={this.state.playlist.name}/>
                            </Grid>
                        </React.Suspense>
                    </Grid>
                </CardContent>
                <CardActions>
                    <Button variant="contained" color="primary" className="full-width" onClick={this.updateStats}>Update</Button>
                </CardActions>
            </Card>
            </div>
        );
    }
}

function LoadingMessage(props) {
    return <Typography variant="h5" component="h2" className="ui-text center-text">Loading...</Typography>;
}